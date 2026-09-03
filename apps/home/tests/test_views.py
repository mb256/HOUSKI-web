import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page_returns_200(client):
    response = client.get(reverse('home:index'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_page_uses_expected_template(client):
    response = client.get(reverse('home:index'))
    assert 'home/index.html' in [t.name for t in response.templates]
