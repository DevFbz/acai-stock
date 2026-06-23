from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import resolve

from tenants.models import Tenant


EXEMPT_PATHS = [
    "accounts:login",
    "accounts:logout",
    "accounts:blocked",
    "admin:index",
    "admin:login",
]


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return

        resolve_match = resolve(request.path_info)
        url_name = f"{resolve_match.namespace}:{resolve_match.url_name}" if resolve_match.namespace else resolve_match.url_name

        if url_name in EXEMPT_PATHS:
            return

        if request.user.is_superuser:
            return

        tenant = request.user.tenant
        if not tenant:
            return redirect("accounts:blocked")

        if not tenant.is_accessible:
            return redirect("accounts:blocked")
