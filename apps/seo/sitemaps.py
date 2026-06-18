"""XML sitemaps for the public site.

Posts and pages are exposed with per-language alternates (``i18n``/``alternates``),
so the sitemap mirrors the hreflang annotations: one entry per record with
``<xhtml:link rel="alternate" hreflang>`` for every configured language. noindex
content and drafts are excluded.
"""

from __future__ import annotations

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.content.models import Page, Post, Service


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    i18n = True
    alternates = True

    def items(self):
        return Post.objects.published().filter(noindex=False)

    def lastmod(self, obj: Post):
        return obj.updated_at

    def location(self, obj: Post) -> str:
        return obj.get_absolute_url()


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    i18n = True
    alternates = True

    def items(self):
        return Page.objects.published().filter(noindex=False)

    def lastmod(self, obj: Page):
        return obj.updated_at

    def location(self, obj: Page) -> str:
        return obj.get_absolute_url()


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8  # services are primary GEO landing pages
    i18n = True
    alternates = True

    def items(self):
        return Service.objects.published().filter(noindex=False)

    def lastmod(self, obj: Service):
        return obj.updated_at

    def location(self, obj: Service) -> str:
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    i18n = True
    alternates = True

    def items(self) -> list[str]:
        return ["core:home", "content:post_list", "content:service_list"]

    def location(self, item: str) -> str:
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "posts": PostSitemap,
    "pages": PageSitemap,
}
