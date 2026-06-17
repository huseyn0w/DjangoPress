"""Test settings: fast, isolated, no external services required."""

from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "test-secret-key-not-used-anywhere-real"  # noqa: S105
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Use an in-memory SQLite database so the suite runs without Postgres.
# All ORM usage stays DB-agnostic, so this is a faithful smoke test.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Fast, deterministic password hashing for tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Render Vite tags as dev-server URLs so tests never need a build manifest.
DJANGO_VITE["default"]["dev_mode"] = True  # noqa: F405

# Plain static storage — no manifest required during tests.
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}
