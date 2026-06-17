from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class AdminAccessMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Base gate for every admin-panel view.

    Unauthenticated users are redirected to login; authenticated users without
    `accounts.access_admin` get a 403. Individual views add their own, more
    specific permission via `permission_required` (a tuple is ANDed).
    """

    permission_required = "accounts.access_admin"
