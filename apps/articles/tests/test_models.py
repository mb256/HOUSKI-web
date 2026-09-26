import pytest
from apps.users.models import User
from apps.articles.models import Article


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author3', password='Pass123!', must_change_password=False)


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
