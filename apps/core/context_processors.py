from django.conf import settings
from django.urls import translate_url
from django.utils.translation import get_language

from .models import SiteSettings


def site_settings(request):
    """Expose the site settings singleton to every template as `site`."""
    return {"site": SiteSettings.load()}


def i18n_alternates(request):
    """Per-language alternate URLs for the current page (hreflang + switcher).

    For each configured language we re-resolve the current path under that
    language's URL prefix (``translate_url``). Because every non-default language
    carries a prefix (see ``i18n_patterns`` in config/urls.py), the alternates are
    distinct, crawlable URLs — exactly what search/answer engines expect from
    ``rel="alternate" hreflang`` annotations. ``x-default`` points at the default
    language version.
    """
    current = get_language()
    alternates = []
    for code, name in settings.LANGUAGES:
        path = translate_url(request.path, code)
        alternates.append(
            {
                "code": code,
                "name": name,
                "url": request.build_absolute_uri(path),
                "is_current": code == current,
            }
        )
    # Only advertise alternates when the per-language URLs are genuinely distinct.
    # On pages outside i18n_patterns (e.g. the media library) translate_url returns
    # the same path for every language, which would emit duplicate, invalid hreflang.
    distinct = len({alt["url"] for alt in alternates}) > 1
    x_default = next(
        (alt["url"] for alt in alternates if alt["code"] == settings.LANGUAGE_CODE),
        None,
    )
    return {
        "i18n_alternates": alternates if distinct else [],
        "i18n_x_default": x_default if distinct else None,
        "i18n_current_language": current,
    }
