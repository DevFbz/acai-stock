from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from inventory.models import Product, StockMovement
from ai_engine.graph import generate_ai_report
from reports.models import Report


@login_required
def ai_dashboard(request):
    tenant = request.user.tenant
    reports = Report.objects.filter(tenant=tenant, report_type="ai_custom")
    return render(request, "ai_engine/dashboard.html", {"reports": reports})


@login_required
@require_POST
def generate_report(request):
    tenant = request.user.tenant
    products = Product.objects.filter(tenant=tenant, is_active=True)
    stock_data = [
        {
            "name": p.name,
            "current": float(p.current_stock),
            "min": float(p.min_stock),
            "unit": p.unit,
            "expiry": p.expiry_date.isoformat() if p.expiry_date else None,
            "low": p.is_low_stock,
        }
        for p in products
    ]
    movements = StockMovement.objects.filter(product__tenant=tenant)[:50].values(
        "product__name", "movement_type", "quantity", "created_at"
    )
    movement_data = list(movements)

    content = generate_ai_report(tenant.name, stock_data, movement_data)

    report = Report.objects.create(
        tenant=tenant,
        title=f"Relatório IA - {tenant.name}",
        report_type="ai_custom",
        content=content,
        summary=content[:300],
        generated_by="ai_engine",
    )
    return redirect("ai_engine:dashboard")
