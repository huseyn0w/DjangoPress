import pytest

from apps.plugins import registry
from apps.plugins.models import Plugin

pytestmark = pytest.mark.django_db


def test_discovers_installed_plugin():
    slugs = {p.slug for p in registry.get_installed_plugins()}
    assert "reading_time" in slugs


def test_plugin_metadata_from_appconfig():
    info = next(p for p in registry.get_installed_plugins() if p.slug == "reading_time")
    assert info.name == "Reading Time"
    assert "reading time" in info.description.lower()
    assert info.version == "1.0"


def test_enabled_by_default():
    assert registry.is_plugin_enabled("reading_time") is True


def test_set_enabled_toggles_and_persists():
    assert registry.set_enabled("reading_time", False) is True
    assert registry.is_plugin_enabled("reading_time") is False
    assert Plugin.objects.get(app_label="reading_time").enabled is False


def test_set_enabled_unknown_plugin_rejected():
    assert registry.set_enabled("nope", True) is False


def test_sync_creates_rows():
    Plugin.objects.all().delete()
    registry.sync_plugins()
    assert Plugin.objects.filter(app_label="reading_time").exists()
