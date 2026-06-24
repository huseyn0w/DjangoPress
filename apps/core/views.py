from django.views.generic import TemplateView

from . import services


class HomeView(TemplateView):
    """Public landing page. Showcases the CMS with its own real published
    content (recent posts and services) rather than mock previews."""

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(services.home_context())
        return ctx
