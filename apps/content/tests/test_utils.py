import pytest

from apps.content.models import Category
from apps.content.utils import sanitize_html, unique_slugify


def test_sanitize_strips_scripts_and_keeps_allowed():
    dirty = "<p>Hello</p><script>alert(1)</script><strong>x</strong>"
    clean = sanitize_html(dirty)
    assert "<script>" not in clean
    assert "alert(1)" not in clean
    assert "<p>Hello</p>" in clean
    assert "<strong>x</strong>" in clean


def test_sanitize_drops_unsafe_link_scheme():
    clean = sanitize_html('<a href="javascript:alert(1)">x</a>')
    assert "javascript:" not in clean


def test_sanitize_empty_is_safe():
    assert sanitize_html("") == ""


@pytest.mark.django_db
def test_unique_slugify_increments_on_collision():
    a = Category.objects.create(name="Tech News")
    b = Category.objects.create(name="Tech News")
    assert a.slug == "tech-news"
    assert b.slug == "tech-news-2"


@pytest.mark.django_db
def test_unique_slugify_keeps_own_slug_on_resave():
    cat = Category.objects.create(name="Design")
    slug = unique_slugify(cat, "Design")
    assert slug == "design"
