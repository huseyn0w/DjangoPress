import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.accounts.roles import DEFAULT_ROLES, DEFAULT_SIGNUP_ROLE
from apps.accounts.signals import sync_default_roles

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_default_roles_created_on_migrate():
    # post_migrate sync runs during test DB setup; all roles should exist.
    for role_name in DEFAULT_ROLES:
        assert Group.objects.filter(name=role_name).exists(), role_name


def test_sync_is_idempotent():
    sync_default_roles()
    sync_default_roles()
    assert Group.objects.filter(name="Administrator").count() == 1


def test_administrator_has_account_capabilities():
    admin_group = Group.objects.get(name="Administrator")
    codenames = set(admin_group.permissions.values_list("codename", flat=True))
    assert {"access_admin", "manage_users", "manage_settings"} <= codenames


def test_editor_lacks_user_management():
    editor = Group.objects.get(name="Editor")
    codenames = set(editor.permissions.values_list("codename", flat=True))
    assert "manage_users" not in codenames
    assert "access_admin" in codenames


def test_subscriber_has_no_permissions():
    subscriber = Group.objects.get(name="Subscriber")
    assert subscriber.permissions.count() == 0


def test_user_in_role_gets_permission():
    user = User.objects.create_user(username="ed")
    user.groups.add(Group.objects.get(name="Administrator"))
    # Re-fetch to clear the permission cache.
    user = User.objects.get(pk=user.pk)
    assert user.has_perm("accounts.manage_users")
    assert user.has_role("Administrator")


def test_signup_assigns_default_role():
    from allauth.account.signals import user_signed_up

    user = User.objects.create_user(username="newbie")
    user_signed_up.send(sender=User, request=None, user=user)
    assert user.has_role(DEFAULT_SIGNUP_ROLE)
