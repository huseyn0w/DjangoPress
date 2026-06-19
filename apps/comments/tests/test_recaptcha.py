"""reCAPTCHA v3 spam protection on the comment form.

The captcha is layered onto the Phase 9.1 comment flow and is **gracefully
disabled** when no keys are configured: the field is only added when both
``RECAPTCHA_PUBLIC_KEY`` and ``RECAPTCHA_PRIVATE_KEY`` are set, so dev/test
(no keys) keep the original frictionless flow. When enabled, Google's verify
endpoint is the only thing mocked — our wiring is exercised for real.
"""

import pytest
from django_recaptcha.client import RecaptchaResponse

from apps.comments.forms import CommentForm
from apps.comments.models import Comment, CommentStatus
from apps.content.models import Post, Status

pytestmark = pytest.mark.django_db

PUB = "test-public-key"
PRIV = "test-private-key"


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username="writer")


@pytest.fixture
def post(author):
    return Post.objects.create(
        title="Hello", body="<p>x</p>", author=author, status=Status.PUBLISHED
    )


def _pass_verification(monkeypatch, *, is_valid: bool):
    monkeypatch.setattr(
        "django_recaptcha.fields.client.submit",
        lambda *a, **k: RecaptchaResponse(is_valid=is_valid),
    )


# --------------------------------------------------------------------------- #
# Field presence is gated on configured keys
# --------------------------------------------------------------------------- #
def test_no_captcha_field_when_keys_unset(settings):
    settings.RECAPTCHA_PUBLIC_KEY = ""
    settings.RECAPTCHA_PRIVATE_KEY = ""
    assert "captcha" not in CommentForm().fields


def test_captcha_field_present_when_keys_set(settings):
    settings.RECAPTCHA_PUBLIC_KEY = PUB
    settings.RECAPTCHA_PRIVATE_KEY = PRIV
    assert "captcha" in CommentForm().fields


# --------------------------------------------------------------------------- #
# The 9.1 flow is untouched when reCAPTCHA is disabled
# --------------------------------------------------------------------------- #
def test_comment_flow_works_without_recaptcha(client, post, settings):
    settings.RECAPTCHA_PUBLIC_KEY = ""
    settings.RECAPTCHA_PRIVATE_KEY = ""
    resp = client.post(
        post.get_absolute_url(), {"name": "Bob", "email": "b@x.com", "body": "Great post"}
    )
    assert resp.status_code == 302
    assert Comment.objects.filter(name="Bob", status=CommentStatus.PENDING).count() == 1


# --------------------------------------------------------------------------- #
# When enabled, a passing token saves and a failing token is rejected
# --------------------------------------------------------------------------- #
def test_valid_captcha_allows_comment(client, post, settings, monkeypatch):
    settings.RECAPTCHA_PUBLIC_KEY = PUB
    settings.RECAPTCHA_PRIVATE_KEY = PRIV
    _pass_verification(monkeypatch, is_valid=True)
    resp = client.post(
        post.get_absolute_url(),
        {"name": "Bob", "email": "", "body": "Legit", "captcha": "token"},
    )
    assert resp.status_code == 302
    assert Comment.objects.filter(name="Bob").count() == 1


def test_failing_captcha_blocks_comment(client, post, settings, monkeypatch):
    settings.RECAPTCHA_PUBLIC_KEY = PUB
    settings.RECAPTCHA_PRIVATE_KEY = PRIV
    _pass_verification(monkeypatch, is_valid=False)
    resp = client.post(
        post.get_absolute_url(),
        {"name": "Spammer", "email": "", "body": "buy pills", "captcha": "bad"},
    )
    assert resp.status_code == 200  # re-rendered with errors
    assert Comment.objects.filter(name="Spammer").count() == 0


def test_missing_captcha_blocks_comment(client, post, settings):
    settings.RECAPTCHA_PUBLIC_KEY = PUB
    settings.RECAPTCHA_PRIVATE_KEY = PRIV
    resp = client.post(
        post.get_absolute_url(),
        {"name": "Spammer", "email": "", "body": "buy pills"},
    )
    assert resp.status_code == 200
    assert Comment.objects.filter(name="Spammer").count() == 0
