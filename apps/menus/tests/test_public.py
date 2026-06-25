"""Public menu rendering in the shared site shell (F9)."""

import pytest

from apps.menus.models import LinkType, Menu, MenuItem

pytestmark = pytest.mark.django_db


def test_primary_menu_renders_in_header(client):
    menu = Menu.objects.create(name="Primary", slug="primary")
    MenuItem.objects.create(menu=menu, label="Docs", link_type=LinkType.CUSTOM, url="/docs/")
    response = client.get("/")
    assert response.status_code == 200
    assert b"Docs" in response.content
    assert b'href="/docs/"' in response.content


def test_header_falls_back_to_defaults_without_menu(client):
    response = client.get("/")
    assert response.status_code == 200
    # Built-in links remain when no managed menu exists.
    assert b"Services" in response.content
    assert b"Blog" in response.content


def test_footer_menu_renders(client):
    menu = Menu.objects.create(name="Footer", slug="footer")
    MenuItem.objects.create(menu=menu, label="Privacy", link_type=LinkType.CUSTOM, url="/privacy/")
    response = client.get("/")
    assert response.status_code == 200
    assert b"Privacy" in response.content
