"""Keep the default roles (Groups) and their permissions in sync after migrate."""

from __future__ import annotations

from allauth.account.signals import user_signed_up
from django.apps import apps as django_apps
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .roles import DEFAULT_ROLES, DEFAULT_SIGNUP_ROLE


def sync_default_roles() -> None:
    """
    Ensure every default role exists as a Group with exactly the permissions
    that currently exist from its definition.

    Idempotent: safe to run on every migrate. Permissions named for models that
    don't exist yet are simply skipped until those phases land.
    """
    # Build a lookup of "app_label.codename" -> Permission for everything present.
    perms = {
        f"{p.content_type.app_label}.{p.codename}": p
        for p in Permission.objects.select_related("content_type").all()
    }

    for role_name, codenames in DEFAULT_ROLES.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        resolved = [perms[c] for c in codenames if c in perms]
        group.permissions.set(resolved)


@receiver(post_migrate)
def _sync_roles_on_migrate(sender, **kwargs) -> None:
    # Run on every app's post_migrate (idempotent and cheap). Permissions for a
    # given model are created during that model's app post_migrate, so by the
    # final pass every permission named in the role map that has a backing model
    # exists and gets assigned. Running per-app — rather than only for accounts —
    # means roles pick up permissions from apps added in later phases too.
    if not django_apps.is_installed("django.contrib.auth"):
        return
    sync_default_roles()


@receiver(user_signed_up)
def _assign_default_role(request, user, **kwargs) -> None:
    """Place every new self-service signup into the default role."""
    group, _ = Group.objects.get_or_create(name=DEFAULT_SIGNUP_ROLE)
    user.groups.add(group)
