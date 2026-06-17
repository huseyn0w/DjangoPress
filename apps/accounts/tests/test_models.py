import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def test_custom_user_model_is_active():
    assert settings.AUTH_USER_MODEL == "accounts.User"


@pytest.mark.django_db
def test_create_user_and_superuser():
    user = User.objects.create_user(username="alice", email="alice@example.com", password="pw")
    assert user.pk is not None
    assert user.check_password("pw")
    assert not user.is_staff

    admin = User.objects.create_superuser(username="root", email="root@example.com", password="pw")
    assert admin.is_staff and admin.is_superuser


@pytest.mark.django_db
def test_display_name_prefers_full_name():
    user = User.objects.create_user(username="bob", first_name="Bob", last_name="Stone")
    assert user.display_name == "Bob Stone"

    plain = User.objects.create_user(username="nameless")
    assert plain.display_name == "nameless"


@pytest.mark.django_db
def test_profile_fields_exist():
    user = User.objects.create_user(username="carol", bio="Writer.", website="https://carol.dev")
    user.full_clean(exclude=["password"])
    assert user.bio == "Writer."
    assert user.website == "https://carol.dev"
