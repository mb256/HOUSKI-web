import io
import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from apps.users.models import User
from apps.articles.models import Article
from apps.home.models import SummernoteAttachment


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author3', password='Pass123!', must_change_password=False)


def _attachment(tmp_path, name='photo.png'):
    with override_settings(MEDIA_ROOT=tmp_path):
        buf = io.BytesIO()
        Image.new('RGB', (10, 10), color='red').save(buf, 'PNG')
        return SummernoteAttachment.objects.create(
            file=SimpleUploadedFile(name, buf.getvalue(), content_type='image/png'),
        )


def _cover_upload(name='cover.png'):
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), color='blue').save(buf, 'PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


@pytest.mark.django_db
def test_cover_thumbnail_url_none_without_image(author):
    article = Article.objects.create(author=author, headline='Bez obrázku', text='<p>jen text</p>')
    assert article.cover_thumbnail_url is None


@pytest.mark.django_db
def test_cover_thumbnail_url_derived_from_first_image(author):
    text = (
        '<p>úvod</p>'
        '<p><img src="/media/django-summernote/2026-01-01/abc123.jpg" style="width: 100px;"></p>'
        '<p><img src="/media/django-summernote/2026-01-01/second.jpg"></p>'
    )
    article = Article.objects.create(author=author, headline='S obrázky', text=text)
    assert article.cover_thumbnail_url == '/media/django-summernote/2026-01-01/abc123_thumb.jpg'


@pytest.mark.django_db
def test_save_links_referenced_attachment_to_article(author, tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        attachment = _attachment(tmp_path)
        article = Article.objects.create(
            author=author, headline='S obrázkem',
            text=f'<p><img src="/media/{attachment.file.name}"></p>',
        )
        attachment.refresh_from_db()
        assert attachment.owner == article


@pytest.mark.django_db
def test_edit_removing_image_unlinks_attachment(author, tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        attachment = _attachment(tmp_path)
        article = Article.objects.create(
            author=author, headline='S obrázkem',
            text=f'<p><img src="/media/{attachment.file.name}"></p>',
        )
        article.text = '<p>obrázek smazán</p>'
        article.save()
        attachment.refresh_from_db()
        assert attachment.owner is None


@pytest.mark.django_db
def test_delete_article_removes_owned_attachment(author, tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        attachment = _attachment(tmp_path)
        article = Article.objects.create(
            author=author, headline='S obrázkem',
            text=f'<p><img src="/media/{attachment.file.name}"></p>',
        )
        file_path = attachment.file.path
        article.delete()
        assert not SummernoteAttachment.objects.filter(pk=attachment.pk).exists()
        assert not os.path.exists(file_path)


@pytest.mark.django_db
def test_cover_image_takes_precedence_over_first_inline_image(author, tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        text = '<p><img src="/media/django-summernote/inline.jpg"></p>'
        article = Article.objects.create(
            author=author, headline='S titulním obrázkem', text=text,
            cover_image=_cover_upload(),
        )
        article.refresh_from_db()
        assert article.cover_image_thumbnail
        assert article.cover_thumbnail_url == article.cover_image_thumbnail.url
        assert 'inline' not in article.cover_thumbnail_url


@pytest.mark.django_db
def test_falls_back_to_first_inline_image_without_cover_image(author, tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        text = '<p><img src="/media/django-summernote/inline.jpg"></p>'
        article = Article.objects.create(author=author, headline='Bez titulního obrázku', text=text)
        assert article.cover_thumbnail_url == '/media/django-summernote/inline_thumb.jpg'
