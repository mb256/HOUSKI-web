from django.db import models
from django.conf import settings
from django.urls import reverse
from apps.home.fields import SummernoteTextField
from apps.common.images import process_uploaded_image
from apps.home.models import sync_text_attachments, delete_text_attachments
import os
import re


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('climbing',     'Lezení'),
        ('mountains',    'Hory'),
        ('skialpinism',  'Skialpinismus'),
        ('trekking',     'Trekking'),
        ('other_sport',  'Jiný sport'),
        ('kids',         'Děti'),
        ('pub',          'Hospoda'),
    ]
    slug = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'kategorie'
        verbose_name_plural = 'kategorie'

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, verbose_name='autor')
    headline = models.CharField('nadpis', max_length=300)
    text = SummernoteTextField('text')
    categories = models.ManyToManyField(Category, blank=True, verbose_name='kategorie')
    cover_image = models.ImageField('titulní obrázek', upload_to='articles/covers/', null=True, blank=True)
    cover_image_thumbnail = models.ImageField(upload_to='articles/covers/', null=True, blank=True, editable=False)
    created_at = models.DateTimeField('vytvořeno', auto_now_add=True)
    updated_at = models.DateTimeField('aktualizováno', auto_now=True)

    class Meta:
        verbose_name = 'článek'
        verbose_name_plural = 'články'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.headline

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        sync_text_attachments(self, 'text')
        if self.cover_image:
            process_uploaded_image(self, 'cover_image', 'cover_image_thumbnail')

    def delete(self, *args, **kwargs):
        delete_text_attachments(self)
        return super().delete(*args, **kwargs)

    _FIRST_IMG_SRC_RE = re.compile(r'<img[^>]+src="([^"]+)"')

    @property
    def cover_thumbnail_url(self):
        """URL of the article's cover thumbnail: the manually uploaded
        `cover_image` if set, otherwise the thumbnail of the first inline
        image in `text`. Images inserted via Summernote (and legacy gallery
        images migrated into text) are saved through
        compress_image/make_thumbnail, which always produce a
        `<same-path-without-ext>_thumb.jpg` sibling file - so the fallback
        thumbnail can be derived from the image URL without a DB lookup.
        """
        if self.cover_image_thumbnail:
            return self.cover_image_thumbnail.url
        match = self._FIRST_IMG_SRC_RE.search(self.text or '')
        if not match:
            return None
        root, _ext = os.path.splitext(match.group(1))
        return f'{root}_thumb.jpg'
