"""Root URL configuration for DjangoPress."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # The custom panel at /dashboard/ is the primary admin. The Django admin is
    # kept as a superuser-only fallback: it requires is_staff, which NO DjangoPress
    # role grants, so dashboard users (Editors/Authors/etc.) cannot reach it.
    path("admin/", admin.site.urls),
    # django-allauth: login, signup, logout, password reset, social login.
    path("accounts/", include("allauth.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("", include("apps.media.urls")),
    path("", include("apps.content.urls")),
    path("", include("apps.core.urls")),
]

# Serve user-uploaded media in development. In production these are served by the
# web server / object storage in front of the app.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
