import pytest
from django.urls import reverse

from apps.content.models import Category, Page, Tag
from apps.core.models import SiteSettings

pytestmark = pytest.mark.django_db


def test_editor_creates_page(client, make_user):
    client.force_login(make_user("ed", role="Editor"))
    response = client.post(
        reverse("dashboard:page_create"),
        {
            "title": "About",
            "slug": "",
            "body": "<p>about</p>",
            "template": "default",
            "status": "published",
        },
    )
    assert response.status_code == 302
    assert Page.objects.filter(title="About").exists()


def test_editor_creates_category_and_tag(client, make_user):
    client.force_login(make_user("ed", role="Editor"))
    client.post(
        reverse("dashboard:category_create"), {"name": "News", "slug": "", "description": ""}
    )
    client.post(reverse("dashboard:tag_create"), {"name": "django", "slug": ""})
    assert Category.objects.filter(name="News").exists()
    assert Tag.objects.filter(name="django").exists()


def test_admin_updates_user_roles(client, make_user):
    from django.contrib.auth.models import Group

    admin = make_user("admin", role="Administrator")
    target = make_user("target")
    client.force_login(admin)

    editor_group = Group.objects.get(name="Editor")
    response = client.post(
        reverse("dashboard:user_edit", args=[target.pk]),
        {"is_active": "on", "groups": [editor_group.pk]},
    )
    assert response.status_code == 302
    target.refresh_from_db()
    assert target.has_role("Editor")


def test_admin_cannot_edit_own_roles(client, make_user):
    # Self-lockout guard: editing your own account via the user form is blocked.
    admin = make_user("admin", role="Administrator")
    client.force_login(admin)
    response = client.get(reverse("dashboard:user_edit", args=[admin.pk]))
    assert response.status_code == 302
    assert response.url == reverse("dashboard:user_list")


def test_admin_updates_settings(client, make_user):
    client.force_login(make_user("admin", role="Administrator"))
    response = client.post(
        reverse("dashboard:settings"),
        {"site_name": "My Blog", "tagline": "Hello", "posts_per_page": "5"},
    )
    assert response.status_code == 302
    assert SiteSettings.load().site_name == "My Blog"
