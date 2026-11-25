import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.articles.models import Article, Category


@pytest.mark.django_db
def test_replaces_categories_of_all_articles():
    old = Category.objects.create(slug='climbing', name='Lezení')
    history = Category.objects.create(slug='historie', name='Historie')
    a1 = Article.objects.create(headline='A', text='t')
    a2 = Article.objects.create(headline='B', text='t')
    a1.categories.add(old)

    call_command('set_all_articles_category', 'historie')

    for article in (a1, a2):
        assert list(article.categories.all()) == [history]


@pytest.mark.django_db
def test_dry_run_changes_nothing():
    old = Category.objects.create(slug='climbing', name='Lezení')
    Category.objects.create(slug='historie', name='Historie')
    article = Article.objects.create(headline='A', text='t')
    article.categories.add(old)

    call_command('set_all_articles_category', 'historie', '--dry-run')

    assert list(article.categories.all()) == [old]


@pytest.mark.django_db
def test_unknown_slug_fails():
    with pytest.raises(CommandError):
        call_command('set_all_articles_category', 'nope')
