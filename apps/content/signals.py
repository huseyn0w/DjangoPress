"""Snapshot a revision whenever a Post or Page is saved."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Page, PageRevision, Post, PostRevision


def _changed_since_last(latest, title: str, body: str) -> bool:
    """True if there is no prior revision or the title/body actually changed.

    Avoids noise: a metadata-only save (e.g. flipping status to published) won't
    create a duplicate snapshot of identical content.
    """
    return latest is None or latest.title != title or latest.body != body


@receiver(post_save, sender=Post)
def _snapshot_post(sender, instance: Post, **kwargs) -> None:
    latest = instance.revisions.first()  # ordered -created_at via Revision.Meta
    if _changed_since_last(latest, instance.title, instance.body):
        PostRevision.objects.create(
            post=instance,
            title=instance.title,
            body=instance.body,
            author=instance.author,
        )


@receiver(post_save, sender=Page)
def _snapshot_page(sender, instance: Page, **kwargs) -> None:
    latest = instance.revisions.first()
    if _changed_since_last(latest, instance.title, instance.body):
        PageRevision.objects.create(
            page=instance,
            title=instance.title,
            body=instance.body,
            author=instance.author,
        )
