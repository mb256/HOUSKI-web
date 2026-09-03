import pytest
import datetime
from django.urls import reverse
from apps.users.models import User
from apps.activities.models import Activity


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author3', password='Pass123!', must_change_password=False)


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username='other3', password='Pass123!', must_change_password=False)


@pytest.mark.django_db
def test_activity_list_returns_200(client):
    response = client.get(reverse('activities:list'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_activity_list_splits_upcoming_and_past(client, author):
    today = datetime.date.today()
    Activity.objects.create(author=author, name='Budoucí výlet', start_date=today + datetime.timedelta(days=5), location='Šumava', description='popis')
    Activity.objects.create(author=author, name='Minulý výlet', start_date=today - datetime.timedelta(days=5), location='Krkonoše', description='popis')

    response = client.get(reverse('activities:list'))
    assert [a.name for a in response.context['upcoming']] == ['Budoucí výlet']
    assert [a.name for a in response.context['past']] == ['Minulý výlet']


@pytest.mark.django_db
def test_anonymous_user_cannot_create_activity(client):
    response = client.get(reverse('activities:create'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_user_can_create_activity(client, author):
    client.login(username='author3', password='Pass123!')
    response = client.post(reverse('activities:create'), {
        'name': 'Metodický seminář',
        'start_date': '2026-09-01',
        'end_date': '',
        'location': 'Plzeň',
        'description': 'popis',
    })
    assert Activity.objects.filter(name='Metodický seminář').exists()


@pytest.mark.django_db
def test_non_author_cannot_delete_activity(client, author, other_user):
    activity = Activity.objects.create(author=author, name='Chráněná akce', start_date=datetime.date.today(), location='Plzeň', description='popis')
    client.login(username='other3', password='Pass123!')
    response = client.post(reverse('activities:delete', args=[activity.pk]))
    assert response.status_code == 302
    assert Activity.objects.filter(pk=activity.pk).exists()
