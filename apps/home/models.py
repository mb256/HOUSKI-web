from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_summernote.models import AbstractAttachment
from apps.common.images import process_uploaded_image
import re


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
            process_uploaded_image(self, 'image', 'thumbnail')


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
            process_uploaded_image(self, 'file', 'thumbnail')


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
