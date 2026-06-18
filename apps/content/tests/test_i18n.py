"""Multilingual (django-parler) behaviour for content + hreflang rendering."""

import pytest
from django.contrib.auth import get_user_model
from django.utils import translation

from apps.content.models import Category, Post, Status, Tag

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def author():
    return User.objects.create_user(username="writer")


# --------------------------------------------------------------------------- #
# Model translation behaviour
# --------------------------------------------------------------------------- #
def test_create_writes_default_language_translation(author):
    post = Post.objects.create(title="Hello", body="<p>english</p>", author=author)
    # Default language row exists and round-trips.
    en = Post.objects.language("en").get(pk=post.pk)
    assert en.title == "Hello"
    assert "<p>english</p>" in en.body


def test_second_language_translation_is_independent(author):
    post = Post.objects.create(title="Hello", body="<p>english</p>", author=author)
    post.set_current_language("de")
    post.title = "Hallo"
    post.body = "<p>deutsch</p>"
    post.save()

    assert Post.objects.language("en").get(pk=post.pk).title == "Hello"
    assert Post.objects.language("de").get(pk=post.pk).title == "Hallo"


def test_missing_translation_falls_back_to_default(author):
    post = Post.objects.create(title="OnlyEnglish", author=author)
    # No German translation -> fallback to the default language value.
    de = Post.objects.language("de").get(pk=post.pk)
    assert de.title == "OnlyEnglish"


def test_translated_body_is_sanitized_per_language(author):
    post = Post.objects.create(title="Clean", author=author)
    post.set_current_language("de")
    post.title = "Sauber"
    post.body = "<p>ok</p><script>evil()</script>"
    post.save()

    de = Post.objects.language("de").get(pk=post.pk)
    assert "<script>" not in de.body
    assert "<p>ok</p>" in de.body


def test_slug_is_shared_across_languages(author):
    """Slug lives on the shared model: one URL slug per record, language via prefix."""
    post = Post.objects.create(title="Shared Slug", author=author)
    assert post.slug == "shared-slug"
    post.set_current_language("de")
    post.title = "Geteilter Slug"
    post.save()
    # Slug unchanged regardless of the active language.
    assert Post.objects.language("de").get(pk=post.pk).slug == "shared-slug"


def test_category_and_tag_are_translatable(author):
    cat = Category.objects.create(name="News")
    cat.set_current_language("de")
    cat.name = "Nachrichten"
    cat.save()
    assert Category.objects.language("en").get(pk=cat.pk).name == "News"
    assert Category.objects.language("de").get(pk=cat.pk).name == "Nachrichten"

    tag = Tag.objects.create(name="Django")
    assert Tag.objects.language("de").get(pk=tag.pk).name == "Django"  # fallback


# --------------------------------------------------------------------------- #
# Public rendering: hreflang + language-prefixed URLs
# --------------------------------------------------------------------------- #
def test_post_detail_renders_hreflang_alternates(client, author):
    post = Post.objects.create(title="Hello", author=author, status=Status.PUBLISHED)
    html = client.get(post.get_absolute_url()).content.decode()
    assert 'rel="alternate"' in html
    assert 'hreflang="en"' in html
    assert 'hreflang="de"' in html
    assert 'hreflang="x-default"' in html
    # The German alternate is a distinct, language-prefixed URL.
    assert f"/de/blog/{post.slug}/" in html


def test_german_url_serves_german_translation(client, author):
    post = Post.objects.create(
        title="Hello", body="<p>english</p>", author=author, status=Status.PUBLISHED
    )
    post.set_current_language("de")
    post.title = "Hallo"
    post.body = "<p>deutsch</p>"
    post.save()

    html = client.get(f"/de/blog/{post.slug}/").content.decode()
    assert "Hallo" in html
    assert "deutsch" in html
    assert "english" not in html


def test_default_language_url_has_no_prefix(client, author):
    """Default language keeps clean URLs (prefix_default_language=False).

    get_absolute_url() honours the active language (so it stays correct on the
    German page); pin it to the default here to assert the prefix-free form.
    """
    post = Post.objects.create(title="Hello", author=author, status=Status.PUBLISHED)
    with translation.override("en"):
        assert post.get_absolute_url() == f"/blog/{post.slug}/"
    assert client.get(f"/blog/{post.slug}/").status_code == 200


def test_language_switcher_present_on_public_pages(client):
    html = client.get("/blog/").content.decode()
    # The switcher offers both configured languages.
    assert "English" in html
    assert "Deutsch" in html
