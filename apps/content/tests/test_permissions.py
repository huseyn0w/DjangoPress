"""The Phase 2 role sync should now resolve content permissions that exist."""

import pytest
from django.contrib.auth.models import Group

pytestmark = pytest.mark.django_db


def test_administrator_has_content_permissions():
    admin = Group.objects.get(name="Administrator")
    codenames = set(admin.permissions.values_list("codename", flat=True))
    assert {"add_post", "change_post", "delete_post", "publish_post"} <= codenames
    assert {"add_page", "add_category", "add_tag"} <= codenames


def test_author_can_publish_but_not_delete():
    author = Group.objects.get(name="Author")
    codenames = set(author.permissions.values_list("codename", flat=True))
    assert "publish_post" in codenames
    assert "add_post" in codenames
    assert "delete_post" not in codenames


def test_contributor_cannot_publish():
    contributor = Group.objects.get(name="Contributor")
    codenames = set(contributor.permissions.values_list("codename", flat=True))
    assert "add_post" in codenames
    assert "publish_post" not in codenames
