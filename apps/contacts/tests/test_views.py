import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_contacts_page_returns_200(client):
    response = client.get(reverse('contacts:index'))
    assert response.status_code == 200
