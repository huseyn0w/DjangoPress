import pytest
from django.contrib.auth import get_user_model

from apps.content.models import Page, PageRevision, Post, PostRevision, Status

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def author():
    return User.objects.create_user(username="writer", email="w@example.com")


def test_post_autoslug_and_sanitize(author):
    post = Post.objects.create(
        title="My First Post", author=author, body="<p>hi</p><script>x()</script>"
    )
    assert post.slug == "my-first-post"
    assert "<script>" not in post.body
    assert "<p>hi</p>" in post.body


def test_publishing_stamps_published_at(author):
    post = Post.objects.create(title="Draft", author=author)
    assert post.published_at is None
    assert not post.is_published

    post.status = Status.PUBLISHED
    post.save()
    assert post.published_at is not None
    assert post.is_published


def test_published_manager_excludes_drafts(author):
    Post.objects.create(title="Draft one", author=author)
    live = Post.objects.create(title="Live one", author=author, status=Status.PUBLISHED)
    published = list(Post.objects.published())
    assert live in published
    assert all(p.status == Status.PUBLISHED for p in published)
    assert len(published) == 1


def test_post_save_creates_revision(author):
    post = Post.objects.create(title="Versioned", author=author, body="<p>v1</p>")
    assert PostRevision.objects.filter(post=post).count() == 1

    post.body = "<p>v2</p>"
    post.save()
    revisions = PostRevision.objects.filter(post=post).order_by("created_at")
    assert revisions.count() == 2
    assert revisions.last().body == "<p>v2</p>"


def test_page_save_creates_revision_and_sanitizes(author):
    page = Page.objects.create(title="About", author=author, body="<p>ok</p><script>x</script>")
    assert "<script>" not in page.body
    assert page.slug == "about"  # auto slug on Page too
    assert PageRevision.objects.filter(page=page).count() == 1


def test_metadata_only_save_does_not_duplicate_revision(author):
    # Creating then publishing (no title/body change) must not add a 2nd revision.
    post = Post.objects.create(title="Once", author=author, body="<p>same</p>")
    assert PostRevision.objects.filter(post=post).count() == 1
    post.status = Status.PUBLISHED
    post.save()
    assert PostRevision.objects.filter(post=post).count() == 1


def test_republish_keeps_original_published_at(author):
    post = Post.objects.create(title="Stable", author=author, status=Status.PUBLISHED)
    original = post.published_at
    post.status = Status.DRAFT
    post.save()
    post.status = Status.PUBLISHED
    post.save()
    assert post.published_at == original


def test_excerpt_is_sanitized(author):
    post = Post.objects.create(title="Ex", author=author, excerpt="<b>ok</b><script>bad()</script>")
    assert "<script>" not in post.excerpt
    assert "bad()" not in post.excerpt
