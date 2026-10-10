import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image

from apps.users.models import User
from apps.board.models import BoardPost, BoardImage


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author1', password='Pass123!', must_change_password=False)


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username='other1', password='Pass123!', must_change_password=False)


@pytest.mark.django_db
def test_board_list_returns_200_for_anonymous(client):
    response = client.get(reverse('board:list'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_cannot_create_post(client):
    response = client.get(reverse('board:create'))
    assert response.status_code == 302  # redirected to login


@pytest.mark.django_db
def test_logged_in_user_can_create_post(client, author):
    client.login(username='author1', password='Pass123!')
    response = client.post(reverse('board:create'), {
        'headline': 'Test výlet',
        'text': 'Popis výletu',
        'boardimage_set-TOTAL_FORMS': '0',
        'boardimage_set-INITIAL_FORMS': '0',
        'form-TOTAL_FORMS': '0',
        'form-INITIAL_FORMS': '0',
    })
    assert BoardPost.objects.filter(headline='Test výlet').exists()


@pytest.mark.django_db
def test_non_author_cannot_edit_post(client, author, other_user):
    post = BoardPost.objects.create(author=author, headline='Původní', text='text')
    client.login(username='other1', password='Pass123!')
    response = client.post(reverse('board:edit', args=[post.pk]), {
        'headline': 'Změněno', 'text': 'jiny text',
    })
    post.refresh_from_db()
    assert post.headline == 'Původní'
    assert response.status_code == 302


def _board_image(name='photo.png'):
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), color='green').save(buf, 'PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


@pytest.mark.django_db
def test_author_can_edit_post_without_images(client, author):
    """Regression guard: editing a post with zero images must keep working."""
    post = BoardPost.objects.create(author=author, headline='Původní', text='text')
    client.login(username='author1', password='Pass123!')
    response = client.post(reverse('board:edit', args=[post.pk]), {
        'headline': 'Upraveno', 'text': 'novy text',
        'form-TOTAL_FORMS': '5', 'form-INITIAL_FORMS': '0',
        'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '5',
    })
    post.refresh_from_db()
    assert response.status_code == 302
    assert post.headline == 'Upraveno'


@pytest.mark.django_db
def test_author_can_edit_post_with_existing_image(client, author, tmp_path):
    """Regression test: editing a post that already has a BoardImage must
    succeed and keep the image attached (see form.html hidden 'id' field)."""
    with override_settings(MEDIA_ROOT=tmp_path):
        post = BoardPost.objects.create(author=author, headline='Původní', text='text')
        image = BoardImage.objects.create(post=post, image=_board_image(), order=0)
        client.login(username='author1', password='Pass123!')

        response = client.post(reverse('board:edit', args=[post.pk]), {
            'headline': 'Upraveno', 'text': 'novy text',
            'form-TOTAL_FORMS': '5', 'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '5',
            'form-0-id': str(image.pk),
            'form-0-image': '',
        })

        post.refresh_from_db()
        assert response.status_code == 302
        assert post.headline == 'Upraveno'
        assert BoardImage.objects.filter(pk=image.pk, post=post).exists()


@pytest.mark.django_db
def test_author_can_delete_existing_image_via_formset(client, author, tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        post = BoardPost.objects.create(author=author, headline='Původní', text='text')
        image = BoardImage.objects.create(post=post, image=_board_image(), order=0)
        client.login(username='author1', password='Pass123!')

        response = client.post(reverse('board:edit', args=[post.pk]), {
            'headline': 'Původní', 'text': 'text',
            'form-TOTAL_FORMS': '5', 'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '5',
            'form-0-id': str(image.pk),
            'form-0-image': '',
            'form-0-DELETE': 'on',
        })

        assert response.status_code == 302
        assert not BoardImage.objects.filter(pk=image.pk).exists()


@pytest.mark.django_db
def test_author_can_delete_own_post(client, author):
    post = BoardPost.objects.create(author=author, headline='Ke smazání', text='text')
    client.login(username='author1', password='Pass123!')
    response = client.post(reverse('board:delete', args=[post.pk]))
    assert response.status_code == 302
    assert not BoardPost.objects.filter(pk=post.pk).exists()


@pytest.mark.django_db
def test_board_list_paginates_at_20(client, author):
    for i in range(25):
        BoardPost.objects.create(author=author, headline=f'Post {i}', text='text')
    response = client.get(reverse('board:list'))
    assert len(response.context['page_obj']) == 20


@pytest.mark.django_db
def test_board_list_pagination_inactive_when_20_or_fewer(client, author):
    for i in range(20):
        BoardPost.objects.create(author=author, headline=f'Post {i}', text='text')
    response = client.get(reverse('board:list'))
    content = response.content.decode()
    assert '<span class="disabled">‹</span>' in content
    assert '<span class="disabled">›</span>' in content
    assert '?page=' not in content


@pytest.mark.django_db
def test_board_list_pagination_shows_single_link_at_21(client, author):
    for i in range(21):
        BoardPost.objects.create(author=author, headline=f'Post {i}', text='text')
    response = client.get(reverse('board:list'))
    content = response.content.decode()
    assert '<span class="current">1</span>' in content
    assert '?page=2' in content
    assert '?page=3' not in content
