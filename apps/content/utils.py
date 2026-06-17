"""Helpers for content: server-side HTML sanitization and unique slugs."""

from __future__ import annotations

import nh3
from django.utils.text import slugify

# Allowlist for rich-text bodies. Anything not listed is stripped. This runs on
# every save, so stored HTML is always safe regardless of what a client sends —
# never trust the editor or the request to have sanitized for us.
_ALLOWED_TAGS: set[str] = {
    "p",
    "br",
    "hr",
    "span",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "sub",
    "sup",
    "blockquote",
    "code",
    "pre",
    "kbd",
    "h2",
    "h3",
    "h4",
    "ul",
    "ol",
    "li",
    "a",
    "img",
    "figure",
    "figcaption",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
}

_ALLOWED_ATTRIBUTES: dict[str, set[str]] = {
    # "rel" is intentionally omitted: nh3 sets it via link_rel below and panics
    # if it's also in the allowlist.
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"},
    "span": {"class"},
    "code": {"class"},
}


def sanitize_html(html: str) -> str:
    """Return ``html`` with only allowlisted tags/attributes; safe to store and render.

    URLs are restricted to safe schemes and ``rel="noopener"`` is enforced on links
    by nh3's link-rel handling.
    """
    if not html:
        return ""
    return nh3.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer",
    )


def unique_slugify(instance, value: str, slug_field: str = "slug", max_length: int = 50) -> str:
    """Build a unique slug for ``instance`` from ``value`` within its model.

    Appends ``-2``, ``-3``, ... on collision. Excludes the instance itself so
    re-saving an object keeps its slug.
    """
    model = instance.__class__
    base = slugify(value)[:max_length] or "item"
    slug = base
    suffix = 2
    qs = model._default_manager.all()
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(**{slug_field: slug}).exists():
        trimmed = base[: max_length - len(f"-{suffix}")]
        slug = f"{trimmed}-{suffix}"
        suffix += 1
    return slug
