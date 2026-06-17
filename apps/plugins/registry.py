"""Discovery and enable-state for plugin apps.

A plugin is any installed Django app whose import path starts with ``plugins.``
(they live in the top-level ``plugins/`` directory). Metadata is read from the
plugin's AppConfig; enable state is stored in the :class:`Plugin` model.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.apps import apps as django_apps
from django.core.cache import cache

_PLUGIN_PREFIX = "plugins."
_CACHE_PREFIX = "plugin_enabled:"


@dataclass(frozen=True)
class PluginInfo:
    slug: str  # the app label
    name: str
    description: str
    version: str


def _iter_plugin_configs():
    for config in django_apps.get_app_configs():
        if config.name.startswith(_PLUGIN_PREFIX):
            yield config


def get_installed_plugins() -> list[PluginInfo]:
    plugins = [
        PluginInfo(
            slug=config.label,
            name=getattr(config, "verbose_name", config.label) or config.label,
            description=getattr(config, "plugin_description", ""),
            version=str(getattr(config, "plugin_version", "")),
        )
        for config in _iter_plugin_configs()
    ]
    plugins.sort(key=lambda p: p.name.lower())
    return plugins


def is_plugin_enabled(slug: str) -> bool:
    """Whether a plugin's hooks should run. Cached; defaults to True."""
    key = f"{_CACHE_PREFIX}{slug}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from .models import Plugin

    row = Plugin.objects.filter(app_label=slug).first()
    enabled = True if row is None else row.enabled
    cache.set(key, enabled)
    return enabled


def set_enabled(slug: str, enabled: bool) -> bool:
    """Enable/disable a known plugin. Returns False for an unknown slug."""
    if slug not in {p.slug for p in get_installed_plugins()}:
        return False
    from .models import Plugin

    Plugin.objects.update_or_create(app_label=slug, defaults={"enabled": enabled})
    cache.delete(f"{_CACHE_PREFIX}{slug}")
    return True


def sync_plugins() -> None:
    """Ensure a Plugin row exists for every installed plugin (idempotent)."""
    from .models import Plugin

    for info in get_installed_plugins():
        Plugin.objects.get_or_create(app_label=info.slug)
        cache.delete(f"{_CACHE_PREFIX}{info.slug}")
