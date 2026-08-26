from django.db import models
from django.conf import settings
from PIL import Image
import os


def compress_image(image_path, max_size_kb=400, max_width=1600):
    """Compress image to fit within max_size_kb and max_width."""
    img = Image.open(image_path)
    # Preserve EXIF orientation
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        if exif:
            from PIL.ExifTags import TAGS
            for tag, value in exif.items():
                if TAGS.get(tag) == 'Orientation':
                    # handle rotation if needed
                    pass

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


class PictureOfWeek(models.Model):
    image = models.ImageField(upload_to='picture_of_week/')
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            compress_image(self.image.path)
