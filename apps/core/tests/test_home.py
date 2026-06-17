import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_status_ok(client):
    response = client.get(reverse("core:home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_uses_expected_template(client):
    response = client.get(reverse("core:home"))
    assert "core/home.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_home_renders_brand(client):
    response = client.get(reverse("core:home"))
    assert b"DjangoPress" in response.content
