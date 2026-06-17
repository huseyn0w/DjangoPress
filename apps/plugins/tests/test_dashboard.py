import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.plugins import registry

User = get_user_model()
pytestmark = pytest.mark.django_db


def _user(role):
    u = User.objects.create_user(username=role.lower(), password="pw")
    u.groups.add(Group.objects.get(name=role))
    return u


def test_plugins_page_requires_manage_settings(client):
    client.force_login(_user("Editor"))  # no manage_settings
    assert client.get(reverse("dashboard:plugins")).status_code == 403


def test_admin_sees_plugin_list(client):
    client.force_login(_user("Administrator"))
    response = client.get(reverse("dashboard:plugins"))
    assert response.status_code == 200
    assert b"Reading Time" in response.content


def test_admin_can_toggle_plugin(client):
    client.force_login(_user("Administrator"))
    assert registry.is_plugin_enabled("reading_time") is True
    response = client.post(reverse("dashboard:plugin_toggle", args=["reading_time"]))
    assert response.status_code == 302
    assert registry.is_plugin_enabled("reading_time") is False


def test_toggle_requires_post(client):
    client.force_login(_user("Administrator"))
    assert client.get(reverse("dashboard:plugin_toggle", args=["reading_time"])).status_code == 405
