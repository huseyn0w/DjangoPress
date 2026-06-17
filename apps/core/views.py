from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Public landing page — a styled placeholder for the foundation phase."""

    template_name = "core/home.html"
