from django.contrib import admin
from django.urls import include, path
from django.views.decorators.http import require_GET
from django.shortcuts import redirect

from inventory.views import dashboard


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect("inventory:dashboard")
    return redirect("accounts:login")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_redirect, name="home"),
    path("accounts/", include("accounts.urls")),
    path("estoque/", include("inventory.urls")),
    path("relatorios/", include("reports.urls")),
    path("ia/", include("ai_engine.urls")),
]
