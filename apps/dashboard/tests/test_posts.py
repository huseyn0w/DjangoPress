import pytest
from django.urls import reverse

from apps.content.models import Post, Status

pytestmark = pytest.mark.django_db


def test_author_creates_and_publishes_post(client, make_user):
    author = make_user("writer", role="Author")
    client.force_login(author)
    response = client.post(
        reverse("dashboard:post_create"),
        {"title": "Hello", "slug": "", "excerpt": "", "body": "<p>hi</p>", "status": "published"},
    )
    assert response.status_code == 302
    post = Post.objects.get()
    assert post.author == author
    assert post.status == Status.PUBLISHED
    assert post.published_at is not None


def test_contributor_create_form_renders_without_status(client, make_user):
    client.force_login(make_user("contrib", role="Contributor"))
    response = client.get(reverse("dashboard:post_create"))
    assert response.status_code == 200
    assert b"trix-editor" in response.content
    assert b'name="status"' not in response.content


def test_contributor_post_is_forced_to_draft(client, make_user):
    contributor = make_user("contrib", role="Contributor")
    client.force_login(contributor)
    # Even if a published status is smuggled in, it is forced to draft.
    client.post(
        reverse("dashboard:post_create"),
        {"title": "Sneaky", "slug": "", "excerpt": "", "body": "<p>x</p>", "status": "draft"},
    )
    post = Post.objects.get()
    assert post.status == Status.DRAFT


def test_contributor_edit_does_not_unpublish(client, make_user):
    # Regression: an Editor publishes a Contributor's post; the Contributor editing
    # it must NOT silently send it back to draft.
    contributor = make_user("contrib", role="Contributor")
    post = Post.objects.create(title="Live", author=contributor, status=Status.PUBLISHED)
    assert post.published_at is not None

    client.force_login(contributor)
    response = client.post(
        reverse("dashboard:post_edit", args=[post.pk]),
        {"title": "Live edited", "slug": post.slug, "excerpt": "", "body": "<p>x</p>"},
    )
    assert response.status_code == 302
    post.refresh_from_db()
    assert post.status == Status.PUBLISHED
    assert post.title == "Live edited"


def test_author_cannot_edit_another_authors_post(client, make_user):
    a = make_user("a", role="Author")
    b = make_user("b", role="Author")
    post = Post.objects.create(title="A only", author=a)
    client.force_login(b)
    assert client.get(reverse("dashboard:post_edit", args=[post.pk])).status_code == 404


def test_author_list_is_scoped_to_own_posts(client, make_user):
    a = make_user("a", role="Author")
    b = make_user("b", role="Author")
    Post.objects.create(title="A post", author=a)
    Post.objects.create(title="B post", author=b)

    client.force_login(a)
    response = client.get(reverse("dashboard:post_list"))
    assert b"A post" in response.content
    assert b"B post" not in response.content


def test_editor_sees_all_posts(client, make_user):
    a = make_user("a", role="Author")
    editor = make_user("ed", role="Editor")
    Post.objects.create(title="A post", author=a)

    client.force_login(editor)
    response = client.get(reverse("dashboard:post_list"))
    assert b"A post" in response.content


def test_contributor_cannot_edit_others_post(client, make_user):
    a = make_user("a", role="Author")
    contributor = make_user("c", role="Contributor")
    post = Post.objects.create(title="Not yours", author=a)

    client.force_login(contributor)
    assert client.get(reverse("dashboard:post_edit", args=[post.pk])).status_code == 404


def test_contributor_can_edit_own_post(client, make_user):
    contributor = make_user("c", role="Contributor")
    post = Post.objects.create(title="Mine", author=contributor)
    client.force_login(contributor)
    assert client.get(reverse("dashboard:post_edit", args=[post.pk])).status_code == 200


def test_contributor_cannot_delete(client, make_user):
    contributor = make_user("c", role="Contributor")
    post = Post.objects.create(title="Mine", author=contributor)
    client.force_login(contributor)
    # Contributor lacks delete_post entirely.
    assert client.post(reverse("dashboard:post_delete", args=[post.pk])).status_code == 403
    assert Post.objects.filter(pk=post.pk).exists()


def test_editor_can_delete(client, make_user):
    a = make_user("a", role="Author")
    editor = make_user("ed", role="Editor")
    post = Post.objects.create(title="Doomed", author=a)
    client.force_login(editor)
    response = client.post(reverse("dashboard:post_delete", args=[post.pk]))
    assert response.status_code == 302
    assert not Post.objects.filter(pk=post.pk).exists()
