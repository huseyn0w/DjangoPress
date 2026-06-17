"""Root URL configuration for DjangoPress."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # django-allauth: login, signup, logout, password reset, social login.
    path("accounts/", include("allauth.urls")),
    path("", include("apps.content.urls")),
    path("", include("apps.core.urls")),
]
