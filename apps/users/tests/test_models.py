import pytest
from apps.users.models import User, Role


@pytest.mark.django_db
def test_user_defaults_to_must_change_password():
    user = User.objects.create_user(username='clen1', password='TestPass123!')
    assert user.must_change_password is True


@pytest.mark.django_db
def test_user_can_have_multiple_roles():
    predseda = Role.objects.create(name='predseda')
    clen = Role.objects.create(name='clen')
    user = User.objects.create_user(username='clen2', password='TestPass123!')
    user.roles.set([predseda, clen])
    assert user.roles.count() == 2
