from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_summernote.models import AbstractAttachment
from PIL import Image, ImageOps
import os
import re


def compress_image(image_field, max_size_kb=400, max_width=1600):
    """Compress image to fit within max_size_kb and max_width.

    Always re-encodes to JPEG. If the field's current filename doesn't have
    a .jpg/.jpeg extension, the file is renamed to match (via the field's
    storage, to avoid clobbering an unrelated existing file) and the new
    name (relative to storage root) is returned; otherwise returns None.
    """
    image_path = image_field.path
    img = Image.open(image_path)
    # Bake EXIF orientation into pixels (phones store portrait photos as
    # landscape pixels + a rotation tag; JPEG re-save below drops the tag).
    img = ImageOps.exif_transpose(img)

    # Resize if too wide
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Convert RGBA to RGB for JPEG
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Save with quality reduction until under max_size_kb
    quality = 85
    while quality > 30:
        img.save(image_path, 'JPEG', quality=quality, optimize=True)
        if os.path.getsize(image_path) <= max_size_kb * 1024:
            break
        quality -= 10

    root, ext = os.path.splitext(image_field.name)
    if ext.lower() in ('.jpg', '.jpeg'):
        return None

    storage = image_field.storage
    new_name = storage.get_available_name(root + '.jpg')
    os.rename(image_path, storage.path(new_name))
    return new_name


def make_thumbnail(image_field, max_size_kb=200, max_width=400):
    """Create/refresh a small JPEG thumbnail next to image_field's file.

    Uses a deterministic '<name>_thumb.jpg' path (derived from the field's
    current, already-compressed filename) so repeated saves overwrite the
    same thumbnail instead of piling up orphaned files. Returns the new
    thumbnail name (relative to storage root).
    """
    img = Image.open(image_field.path)
    img = ImageOps.exif_transpose(img)

    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    root, _ext = os.path.splitext(image_field.name)
    thumb_name = f'{root}_thumb.jpg'
    thumb_path = image_field.storage.path(thumb_name)

    quality = 80
    while quality > 30:
        img.save(thumb_path, 'JPEG', quality=quality, optimize=True)
        if os.path.getsize(thumb_path) <= max_size_kb * 1024:
            break
        quality -= 10

    return thumb_name


class PictureOfWeek(models.Model):
    image = models.ImageField(upload_to='picture_of_week/')
    thumbnail = models.ImageField(upload_to='picture_of_week/', null=True, blank=True, editable=False)
    description = models.CharField('popis', max_length=255)
    author = models.CharField('autor fotografie', max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField('aktivní', default=True)

    class Meta:
        verbose_name = 'fotografie týdne'
        verbose_name_plural = 'fotografie týdne'
        ordering = ['-uploaded_at']

    def __str__(self) -> str:
        return f'{self.description} ({self.author})'

    @property
    def thumb_url(self):
        return self.thumbnail.url if self.thumbnail else self.image.url

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            new_name = compress_image(self.image)
            if new_name:
                PictureOfWeek.objects.filter(pk=self.pk).update(image=new_name)
                self.image.name = new_name
            thumb_name = make_thumbnail(self.image)
            PictureOfWeek.objects.filter(pk=self.pk).update(thumbnail=thumb_name)
            self.thumbnail.name = thumb_name


class SummernoteAttachment(AbstractAttachment):
    """Attachment model used by every Summernote editor in the project
    (article/board/activity text fields). Uploaded images are resized to a
    "detail" size and a sibling thumbnail is generated, exactly like
    PictureOfWeek above, so inline images stay reasonably small.

    django-summernote uploads attachments before the owning object (e.g. a
    new Article) exists, so the owner can't be set at upload time. Instead
    `content_type`/`object_id` are populated afterwards by
    `sync_text_attachments()`, called from the owner's `save()`.
    """
    thumbnail = models.FileField(upload_to='django-summernote/', null=True, blank=True, editable=False)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.file:
            new_name = compress_image(self.file)
            if new_name:
                SummernoteAttachment.objects.filter(pk=self.pk).update(file=new_name)
                self.file.name = new_name
            thumb_name = make_thumbnail(self.file)
            SummernoteAttachment.objects.filter(pk=self.pk).update(thumbnail=thumb_name)
            self.thumbnail.name = thumb_name


_IMG_SRC_RE = re.compile(r'<img[^>]+src="([^"]+)"')


def _attachment_names_in_text(text):
    """Storage-relative file names of every <img> referenced in `text`.

    Inline image URLs are `MEDIA_URL + <FileField.name>`
    (e.g. '/media/django-summernote/x.jpg' -> 'django-summernote/x.jpg'),
    which is what `SummernoteAttachment.file` is queried by below.
    """
    names = set()
    for src in _IMG_SRC_RE.findall(text or ''):
        if src.startswith(settings.MEDIA_URL):
            names.add(src[len(settings.MEDIA_URL):])
    return names


def sync_text_attachments(instance, text_field_name='text'):
    """Point the SummernoteAttachment rows still referenced by
    `getattr(instance, text_field_name)` at `instance`, and unlink any
    attachment previously owned by `instance` that's no longer referenced
    (removed from the text before saving). Call after `instance` is saved
    (a pk is required).
    """
    content_type = ContentType.objects.get_for_model(instance)
    referenced_names = _attachment_names_in_text(getattr(instance, text_field_name))

    SummernoteAttachment.objects.filter(
        content_type=content_type, object_id=instance.pk,
    ).exclude(file__in=referenced_names).update(content_type=None, object_id=None)

    if referenced_names:
        SummernoteAttachment.objects.filter(file__in=referenced_names).update(
            content_type=content_type, object_id=instance.pk,
        )


def delete_text_attachments(instance):
    """Delete the SummernoteAttachment rows (and their files) owned by
    `instance`. Call before deleting `instance` itself.
    """
    content_type = ContentType.objects.get_for_model(instance)
    attachments = SummernoteAttachment.objects.filter(content_type=content_type, object_id=instance.pk)
    for attachment in attachments:
        attachment.file.delete(save=False)
        attachment.thumbnail.delete(save=False)
        attachment.delete()
