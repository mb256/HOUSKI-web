import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from apps.home.models import PictureOfWeek


def _png_upload(name='photo.png'):
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), color='red').save(buf, 'PNG')
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
