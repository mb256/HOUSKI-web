from datetime import datetime

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone

from apps.articles.admin import ArticleAdmin
from apps.articles.models import Article


def test_article_admin_form_exposes_created_at():
    model_admin = ArticleAdmin(Article, AdminSite())
    form = model_admin.get_form(RequestFactory().get('/admin/'))

    assert 'created_at' in form.base_fields


@pytest.mark.django_db
def test_article_admin_form_saves_custom_created_at():
    author = get_user_model().objects.create_user(username='admin-test')
    article = Article.objects.create(
        author=author,
        headline='Test article',
        text='Article text',
    )
    model_admin = ArticleAdmin(Article, AdminSite())
    form_class = model_admin.get_form(RequestFactory().get('/admin/'), article)
    form = form_class(
        instance=article,
        data={
            'author': author.pk,
            'headline': article.headline,
            'text': article.text,
            'categories': [],
            'cover_image': '',
            'created_at_0': '2001-02-03',
            'created_at_1': '04:05:06',
        },
    )

    assert form.is_valid(), form.errors
    updated_article = form.save()

    assert updated_article.created_at == timezone.make_aware(datetime(2001, 2, 3, 4, 5, 6))


@pytest.mark.django_db
def test_article_admin_add_form_saves_custom_created_at():
    author = get_user_model().objects.create_user(username='admin-test')
    model_admin = ArticleAdmin(Article, AdminSite())
    form_class = model_admin.get_form(RequestFactory().get('/admin/'))
    form = form_class(
        data={
            'author': author.pk,
            'headline': 'Historical article',
            'text': 'Article text',
            'categories': [],
            'cover_image': '',
            'created_at_0': '2001-02-03',
            'created_at_1': '04:05:06',
        },
    )

    assert form.is_valid(), form.errors
    article = form.save()

    assert article.created_at == timezone.make_aware(datetime(2001, 2, 3, 4, 5, 6))
