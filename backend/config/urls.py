from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect


def serve_manifest(request):
    import json
    from django.conf import settings
    manifest = {
        "name": "Acai Stock - Gestao de Estoque",
        "short_name": "Acai Stock",
        "description": "Sistema de gestao de estoque para acaiterias",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#1e1b2e",
        "theme_color": "#7c3aed",
        "icons": [],
    }
    return JsonResponse(manifest)


def offline_view(request):
    return render(request, "offline.html")


def serve_sw(request):
    from django.conf import settings
    import os
    sw_path = os.path.join(settings.BASE_DIR, "backend", "static", "sw.js")
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HttpResponse(content, content_type="application/javascript")


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
    path("cobranca/", include("billing.urls")),
    path("notificacoes/", include("notifications.urls")),
    path("api/v1/", include("api.urls", namespace="api")),
    path("manifest.json", serve_manifest, name="manifest"),
    path("offline/", offline_view, name="offline"),
    path("sw.js", serve_sw, name="sw"),
]
