from .models import SiteSettings


def site_settings(request):
    """Expose the site settings singleton to every template as `site`."""
    return {"site": SiteSettings.load()}
