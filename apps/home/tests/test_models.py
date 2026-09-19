import io
import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from apps.home.models import PictureOfWeek


def _png_upload(name='photo.png'):
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), color='red').save(buf, 'PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


def _large_upload(name='photo.png', size=(2000, 1500)):
    buf = io.BytesIO()
    Image.new('RGB', size, color=(120, 180, 90)).save(buf, 'PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


@pytest.mark.django_db
def test_png_upload_is_renamed_to_jpg(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        pic = PictureOfWeek.objects.create(
            image=_png_upload(), description='popis', author='autor',
        )
        pic.refresh_from_db()

        assert pic.image.name.endswith('.jpg')
        assert pic.image.storage.exists(pic.image.name)
        assert not pic.image.storage.exists('picture_of_week/photo.png')


@pytest.mark.django_db
def test_thumbnail_is_generated_smaller_than_main_image(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        pic = PictureOfWeek.objects.create(
            image=_large_upload(), description='popis', author='autor',
        )
        pic.refresh_from_db()

        assert pic.thumbnail
        assert pic.thumbnail.name.endswith('_thumb.jpg')

        with Image.open(pic.thumbnail.path) as thumb:
            assert thumb.width <= 400
        with Image.open(pic.image.path) as main:
            assert main.width <= 1600

        assert os.path.getsize(pic.thumbnail.path) < os.path.getsize(pic.image.path)
        assert pic.thumb_url == pic.thumbnail.url
