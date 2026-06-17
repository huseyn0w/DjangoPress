"""End-to-end: the example plugin changes the rendered post, and toggling it works."""

import pytest
from django.contrib.auth import get_user_model

from apps.content.models import Post, Status
from apps.plugins import registry

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def published_post():
    author = User.objects.create_user(username="writer")
    return Post.objects.create(
        title="On Hooks",
        author=author,
        body="<p>" + "word " * 400 + "</p>",
        status=Status.PUBLISHED,
    )


def test_reading_time_shows_when_enabled(client, published_post):
    response = client.get(published_post.get_absolute_url())
    assert response.status_code == 200
    assert b"min read" in response.content


def test_reading_time_hidden_when_disabled(client, published_post):
    registry.set_enabled("reading_time", False)
    response = client.get(published_post.get_absolute_url())
    assert b"min read" not in response.content
