import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image

from apps.users.models import User
from apps.articles.models import Article, Category


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author2', password='Pass123!', must_change_password=False)


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username='other2', password='Pass123!', must_change_password=False)


@pytest.mark.django_db
def test_article_list_returns_200_for_anonymous(client):
    response = client.get(reverse('articles:list'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_article_detail_returns_200(client, author):
    article = Article.objects.create(author=author, headline='Výlet na Petřín', text='text')
    response = client.get(reverse('articles:detail', args=[article.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_cannot_create_article(client):
    response = client.get(reverse('articles:create'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_user_can_create_article(client, author):
    client.login(username='author2', password='Pass123!')
    response = client.post(reverse('articles:create'), {
        'headline': 'Nový článek',
        'text': 'obsah',
        'categories': [],
    })
    assert Article.objects.filter(headline='Nový článek').exists()


@pytest.mark.django_db
def test_inline_image_src_survives_create(client, author):
    """Regression test: bleach sanitization must not strip <img src> (see
    apps.home.fields.SummernoteTextField)."""
    client.login(username='author2', password='Pass123!')
    client.post(reverse('articles:create'), {
        'headline': 'Článek s obrázkem',
        'text': '<p><img src="/media/django-summernote/test.jpg" alt="popis"></p>',
        'categories': [],
    })
    article = Article.objects.get(headline='Článek s obrázkem')
    assert 'src="/media/django-summernote/test.jpg"' in article.text
    assert article.cover_thumbnail_url == '/media/django-summernote/test_thumb.jpg'


@pytest.mark.django_db
def test_non_author_cannot_delete_article(client, author, other_user):
    article = Article.objects.create(author=author, headline='Chráněný', text='text')
    client.login(username='other2', password='Pass123!')
    response = client.post(reverse('articles:delete', args=[article.pk]))
    assert response.status_code == 302
    assert Article.objects.filter(pk=article.pk).exists()


@pytest.mark.django_db
def test_article_list_filters_by_category(client, author):
    climbing = Category.objects.create(slug='climbing', name='Lezení')
    pub = Category.objects.create(slug='pub', name='Hospoda')
    a1 = Article.objects.create(author=author, headline='Lezecký výlet', text='text')
    a1.categories.add(climbing)
    a2 = Article.objects.create(author=author, headline='Večer v hospodě', text='text')
    a2.categories.add(pub)

    response = client.get(reverse('articles:list'), {'category': 'climbing'})
    headlines = [a.headline for a in response.context['page_obj']]
    assert headlines == ['Lezecký výlet']


@pytest.mark.django_db
def test_article_list_groups_by_year(client, author):
    import datetime

    old = Article.objects.create(author=author, headline='Starý článek', text='text')
    Article.objects.filter(pk=old.pk).update(created_at=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc))
    new = Article.objects.create(author=author, headline='Nový článek', text='text')
    Article.objects.filter(pk=new.pk).update(created_at=datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc))

    response = client.get(reverse('articles:list'))
    content = response.content.decode()
    assert '2024' in content and '2022' in content
    assert content.index('2024') < content.index('Nový článek') < content.index('2022') < content.index('Starý článek')


@pytest.mark.django_db
def test_pagination_preserves_category_filter(client, author):
    climbing = Category.objects.create(slug='climbing', name='Lezení')
    for i in range(13):
        a = Article.objects.create(author=author, headline=f'Článek {i}', text='text')
        a.categories.add(climbing)

    response = client.get(reverse('articles:list'), {'category': 'climbing'})
    assert 'category=climbing&page=2' in response.content.decode()


@pytest.mark.django_db
def test_article_archive_lists_all_articles_regardless_of_category(client, author):
    climbing = Category.objects.create(slug='climbing', name='Lezení')
    a1 = Article.objects.create(author=author, headline='S kategorií', text='text')
    a1.categories.add(climbing)
    Article.objects.create(author=author, headline='Bez kategorie', text='text')

    response = client.get(reverse('articles:archive'))
    assert response.status_code == 200
    headlines = [a.headline for a in response.context['articles']]
    assert set(headlines) == {'S kategorií', 'Bez kategorie'}


@pytest.mark.django_db
def test_create_view_accepts_uploaded_cover_image(client, author, tmp_path):
    """Regression test: ArticleForm must be bound with request.FILES, not
    just request.POST, or an uploaded cover_image is silently dropped."""
    with override_settings(MEDIA_ROOT=tmp_path):
        client.login(username='author2', password='Pass123!')
        buf = io.BytesIO()
        Image.new('RGB', (10, 10), color='blue').save(buf, 'PNG')
        cover = SimpleUploadedFile('cover.png', buf.getvalue(), content_type='image/png')

        client.post(reverse('articles:create'), {
            'headline': 'Článek s titulním obrázkem',
            'text': 'obsah',
            'categories': [],
            'cover_image': cover,
        })

        article = Article.objects.get(headline='Článek s titulním obrázkem')
        assert article.cover_image
        assert article.cover_image_thumbnail
