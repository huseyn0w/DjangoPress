"""API services — the data the API viewsets expose, via content repositories.

Viewsets stay at the HTTP boundary and call these; no ``Model.objects`` here.
"""

from __future__ import annotations

from django.db import connection
from django.db.models import QuerySet

from apps.accounts.repositories import UserRepository
from apps.content.repositories import (
    CategoryRepository,
    PageRepository,
    PostRepository,
    ServiceRepository,
    TagRepository,
)

from .repositories import TokenRepository


def published_posts() -> QuerySet:
    return PostRepository.published()


def editable_posts(user) -> QuerySet:
    """Owner-scoped post queryset for API write lookups (update/delete)."""
    return PostRepository.for_dashboard(user)


def issue_token(username: str) -> str | None:
    """Mint (or fetch) an API token for ``username``; None if no such user."""
    user = UserRepository.get_by_username(username)
    if user is None:
        return None
    return TokenRepository.get_or_create_for(user)


def published_pages() -> QuerySet:
    return PageRepository.published()


def published_services() -> QuerySet:
    return ServiceRepository.published()


def all_categories() -> QuerySet:
    return CategoryRepository.with_post_counts()


def all_tags() -> QuerySet:
    return TagRepository.with_post_counts()


def database_ok() -> bool:
    """True if a trivial query against the database succeeds (readiness probe)."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # pragma: no cover - exercised only when the DB is down
        return False
    return True
