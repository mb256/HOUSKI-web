import pytest
from django.urls import reverse
from apps.users.models import User
from apps.board.models import BoardPost


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


@pytest.mark.django_db
def test_author_can_delete_own_post(client, author):
    post = BoardPost.objects.create(author=author, headline='Ke smazání', text='text')
    client.login(username='author1', password='Pass123!')
    response = client.post(reverse('board:delete', args=[post.pk]))
    assert response.status_code == 302
    assert not BoardPost.objects.filter(pk=post.pk).exists()


@pytest.mark.django_db
def test_board_list_paginates_at_25(client, author):
    for i in range(30):
        BoardPost.objects.create(author=author, headline=f'Post {i}', text='text')
    response = client.get(reverse('board:list'))
    assert len(response.context['page_obj']) == 25
