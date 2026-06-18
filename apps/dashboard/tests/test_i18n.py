"""Dashboard editing of per-language translations (django-parler)."""

import pytest
from django.urls import reverse

from apps.content.models import Page, Post

pytestmark = pytest.mark.django_db


def test_post_editor_adds_translation_per_language(client, make_user):
    admin = make_user("admin", role="Administrator")
    client.force_login(admin)

    client.post(
        reverse("dashboard:post_create"),
        {"title": "Hello", "body": "<p>en</p>", "status": "published"},
    )
    post = Post.objects.get(slug="hello")
    assert Post.objects.language("en").get(pk=post.pk).title == "Hello"

    # Editing under ?language=de creates/updates the German translation only.
    edit_url = reverse("dashboard:post_edit", args=[post.pk]) + "?language=de"
    client.post(
        edit_url,
        {"title": "Hallo", "body": "<p>de</p>", "status": "published"},
    )
    assert Post.objects.language("de").get(pk=post.pk).title == "Hallo"
    # English translation is untouched.
    assert Post.objects.language("en").get(pk=post.pk).title == "Hello"


def test_post_form_shows_language_tabs(client, make_user):
    admin = make_user("admin", role="Administrator")
    client.force_login(admin)
    html = client.get(reverse("dashboard:post_create")).content.decode()
    # A language switcher exposes both configured languages in the editor.
    assert "language=de" in html or "?language=de" in html


def test_post_list_search_matches_translated_title(client, make_user):
    admin = make_user("admin", role="Administrator")
    client.force_login(admin)
    client.post(
        reverse("dashboard:post_create"),
        {"title": "Findable Title", "body": "<p>x</p>", "status": "published"},
    )
    # Searching the translated title must not raise and must find the post.
    resp = client.get(reverse("dashboard:post_list") + "?q=Findable")
    assert resp.status_code == 200
    assert b"Findable Title" in resp.content


def test_unknown_language_param_is_rejected(client, make_user):
    """A hand-crafted ?language=xx must not create an orphan translation row."""
    admin = make_user("admin", role="Administrator")
    client.force_login(admin)
    client.post(
        reverse("dashboard:post_create"),
        {"title": "Hello", "body": "<p>en</p>", "status": "published"},
    )
    post = Post.objects.get(slug="hello")
    client.post(
        reverse("dashboard:post_edit", args=[post.pk]) + "?language=zz",
        {"title": "Junk", "body": "<p>junk</p>", "status": "published"},
    )
    # Only the configured languages may have translations; "zz" never persists.
    assert set(post.get_available_languages()) <= {"en", "de"}
    assert "zz" not in post.get_available_languages()


def test_page_editor_adds_translation_per_language(client, make_user):
    admin = make_user("admin", role="Administrator")
    client.force_login(admin)

    client.post(
        reverse("dashboard:page_create"),
        {"title": "About", "body": "<p>en</p>", "template": "default", "status": "published"},
    )
    page = Page.objects.get(slug="about")
    edit_url = reverse("dashboard:page_edit", args=[page.pk]) + "?language=de"
    client.post(
        edit_url,
        {"title": "Uber", "body": "<p>de</p>", "template": "default", "status": "published"},
    )
    assert Page.objects.language("de").get(pk=page.pk).title == "Uber"
    assert Page.objects.language("en").get(pk=page.pk).title == "About"
