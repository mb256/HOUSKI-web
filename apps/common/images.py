"""Generic, model-agnostic image processing helpers.

Used by any model with an uploaded image field (PictureOfWeek, BoardImage,
SummernoteAttachment, Article.cover_image, ...) - kept here rather than in
any single app's models.py so other apps aren't importing image-processing
logic out of an unrelated app's internals.
"""
import io
import os

from PIL import Image, ImageOps


def _encode_jpeg_within_size(img, max_size_kb, quality):
    """Encode `img` as JPEG in memory, lowering quality by 10 until it fits
    under max_size_kb or quality drops to 30 (whichever first) - same
    stepping as the callers used to do writing straight to disk on every
    attempt. Returns the final encoded bytes; the caller writes them once.
    """
    buf = io.BytesIO()
    while quality > 30:
        buf.seek(0)
        buf.truncate()
        img.save(buf, 'JPEG', quality=quality, optimize=True)
        if buf.tell() <= max_size_kb * 1024:
            break
        quality -= 10
    return buf.getvalue()


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

    data = _encode_jpeg_within_size(img, max_size_kb, quality=85)
    with open(image_path, 'wb') as f:
        f.write(data)

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

    data = _encode_jpeg_within_size(img, max_size_kb, quality=80)
    with open(thumb_path, 'wb') as f:
        f.write(data)

    return thumb_name


def process_uploaded_image(instance, image_attr, thumbnail_attr):
    """Compress the image at `getattr(instance, image_attr)` in place,
    generate a thumbnail at `thumbnail_attr`, and persist both onto
    `instance`'s row directly via `.update()` (bypassing `save()` to avoid
    recursing back into it), keeping `instance` in memory consistent with
    what's now stored. Call after `super().save()`, only when the image
    field is set.
    """
    image_field = getattr(instance, image_attr)
    updates = {}

    new_name = compress_image(image_field)
    if new_name:
        image_field.name = new_name
        updates[image_attr] = new_name

    updates[thumbnail_attr] = thumb_name = make_thumbnail(image_field)

    type(instance).objects.filter(pk=instance.pk).update(**updates)
    getattr(instance, thumbnail_attr).name = thumb_name
