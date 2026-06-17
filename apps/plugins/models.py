from django.db import models
from django.utils.translation import gettext_lazy as _


class Plugin(models.Model):
    """Persisted enable/disable state for an installed plugin app.

    The plugin's code (its app + hooks) is always loaded; this row only controls
    whether its hooks actually run, so plugins toggle at runtime without a restart.
    Human-readable metadata lives on the plugin's AppConfig, not here.
    """

    app_label = models.CharField(_("app label"), max_length=100, unique=True)
    enabled = models.BooleanField(_("enabled"), default=True)

    class Meta:
        verbose_name = _("plugin")
        verbose_name_plural = _("plugins")
        ordering = ["app_label"]

    def __str__(self) -> str:
        return self.app_label
