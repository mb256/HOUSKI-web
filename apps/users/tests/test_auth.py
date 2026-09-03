import pytest
from django.urls import reverse
from apps.users.models import User


@pytest.fixture
def new_user(db):
    return User.objects.create_user(username='novak', password='TempPass123!')


@pytest.mark.django_db
def test_new_user_is_forced_to_change_password(client, new_user):
    client.login(username='novak', password='TempPass123!')
    response = client.get(reverse('home:index'))
    assert response.status_code == 302
    assert response.url == reverse('password_change')


@pytest.mark.django_db
def test_password_change_clears_must_change_password_flag(client, new_user):
    client.login(username='novak', password='TempPass123!')
    response = client.post(reverse('password_change'), {
        'old_password': 'TempPass123!',
        'new_password1': 'BrandNewPass456!',
        'new_password2': 'BrandNewPass456!',
    })
    assert response.status_code == 302
    new_user.refresh_from_db()
    assert new_user.must_change_password is False


@pytest.mark.django_db
def test_user_without_forced_change_can_browse_freely(client):
    user = User.objects.create_user(username='brouk2', password='Pass123!', must_change_password=False)
    client.login(username='brouk2', password='Pass123!')
    response = client.get(reverse('home:index'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_requires_login(client):
    response = client.get(reverse('users:profile'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_profile_updates_user_data(client):
    user = User.objects.create_user(username='clen3', password='Pass123!', must_change_password=False)
    client.login(username='clen3', password='Pass123!')
    response = client.post(reverse('users:profile'), {
        'first_name': 'Jan',
        'last_name': 'Novák',
        'email': 'jan@example.com',
        'telephone': '123456789',
    })
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.first_name == 'Jan'
    assert user.telephone == '123456789'
