"""Smoke tests that the settings split is wired correctly."""

from django.conf import settings


def test_core_app_installed():
    assert "apps.core" in settings.INSTALLED_APPS


def test_vite_configured():
    assert "default" in settings.DJANGO_VITE


def test_whitenoise_middleware_present():
    assert "whitenoise.middleware.WhiteNoiseMiddleware" in settings.MIDDLEWARE
