"""Core (landing page) services — orchestration for the public home view.

Keeps the home view at the HTTP boundary and delegates data access to the content
repositories (no ``Model.objects`` here), so the publish rule and query shape live
in one place.
"""

from __future__ import annotations

from apps.content.repositories import PostRepository, ServiceRepository

# How many items the landing showcases per section.
_HOME_LIMIT = 3


def home_context() -> dict:
    """Recent published posts + featured published services for the landing page."""
    return {
        "recent_posts": PostRepository.recent_published(_HOME_LIMIT),
        "featured_services": ServiceRepository.recent_published(_HOME_LIMIT),
    }
