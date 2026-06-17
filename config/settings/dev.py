"""Development settings: convenient, verbose, never for production."""

from .base import *  # noqa: F401,F403

DEBUG = True

# Throwaway key for local development only — never used in prod (see prod.py).
SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me")  # noqa: F405

# Permit the usual local hosts even if the env var is unset.
ALLOWED_HOSTS = list({*ALLOWED_HOSTS, "localhost", "127.0.0.1", "0.0.0.0"})  # noqa: F405

# Show emails in the console during development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
