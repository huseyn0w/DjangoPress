from django.apps import AppConfig


class ReadingTimeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.reading_time"
    label = "reading_time"
    verbose_name = "Reading Time"
    # Metadata read by the plugin registry for the admin listing.
    plugin_description = "Adds an estimated reading time to the top of each post."
    plugin_version = "1.0"

    def ready(self) -> None:
        from . import hooks  # noqa: F401  registers the post_content filter
