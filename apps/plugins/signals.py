"""Keep Plugin rows in sync with installed plugin apps after migrate."""

from __future__ import annotations

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .registry import sync_plugins


@receiver(post_migrate)
def _sync_plugins_on_migrate(sender, **kwargs) -> None:
    # Run once, after this app has migrated (its table exists by then).
    if getattr(sender, "label", None) == "plugins":
        sync_plugins()
