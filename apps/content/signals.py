"""Snapshot a revision whenever a Post or Page is saved.

Bodies are translated per language (django-parler), so revisions are scoped to the
language that was just saved: each language keeps its own independent history.
"""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Page, PageRevision, Post, PostRevision


def _changed_since_last(latest, title: str, body: str) -> bool:
    """True if there is no prior revision (in this language) or the content changed.

    Avoids noise: a metadata-only save (e.g. flipping status to published) won't
    create a duplicate snapshot of identical content.
    """
    return latest is None or latest.title != title or latest.body != body


@receiver(post_save, sender=Post)
def _snapshot_post(sender, instance: Post, **kwargs) -> None:
    language = instance.get_current_language()
    title = instance.safe_translation_getter("title", default="", language_code=language)
    body = instance.safe_translation_getter("body", default="", language_code=language)
    latest = instance.revisions.filter(language_code=language).first()
    if _changed_since_last(latest, title, body):
        PostRevision.objects.create(
            post=instance,
            language_code=language,
            title=title,
            body=body,
            author=instance.author,
        )


@receiver(post_save, sender=Page)
def _snapshot_page(sender, instance: Page, **kwargs) -> None:
    language = instance.get_current_language()
    title = instance.safe_translation_getter("title", default="", language_code=language)
    body = instance.safe_translation_getter("body", default="", language_code=language)
    latest = instance.revisions.filter(language_code=language).first()
    if _changed_since_last(latest, title, body):
        PageRevision.objects.create(
            page=instance,
            language_code=language,
            title=title,
            body=body,
            author=instance.author,
        )
