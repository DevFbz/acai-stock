from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from inventory.models import Product, StockMovement, Category, Supplier, PurchaseOrder
from reports.models import Report


def _last_n_days(n):
    return timezone.now().date() - timedelta(days=n)


@login_required
def analytics_dashboard(request):
    tenant = request.user.tenant
    products = Product.objects.filter(tenant=tenant, is_active=True)

    # KPIs
    total_products = products.count()
    total_stock_value = sum(float(p.current_stock) * float(p.cost_price) for p in products)
    low_stock_count = len([p for p in products if p.is_low_stock])
    expired_count = len([p for p in products if p.is_expired])
    expiring_count = len([p for p in products if p.days_to_expiry is not None and 0 < p.days_to_expiry <= 7])

    # Movimentacoes ultimos 30 dias
    thirty_days_ago = _last_n_days(30)
    movements = StockMovement.objects.filter(
        product__tenant=tenant, created_at__date__gte=thirty_days_ago
    )
    daily_data = {}
    for m in movements:
        day = m.created_at.date().isoformat()
        if day not in daily_data:
            daily_data[day] = {"in": 0, "out": 0, "waste": 0}
        key = m.movement_type if m.movement_type in daily_data[day] else "out"
        daily_data[day][key] += float(m.quantity)
    movement_labels = sorted(daily_data.keys())
    movement_in = [daily_data[d]["in"] for d in movement_labels]
    movement_out = [daily_data[d]["out"] for d in movement_labels]
    movement_waste = [daily_data[d]["waste"] for d in movement_labels]

    # Top produtos por movimentacao (saidas)
    top_products = list(
        StockMovement.objects.filter(
            product__tenant=tenant, movement_type="out", created_at__date__gte=thirty_days_ago
        ).values("product__name").annotate(total=Sum("quantity")).order_by("-total")[:10]
    )
    top_labels = [t["product__name"] for t in top_products]
    top_values = [float(t["total"]) for t in top_products]

    # Distribuicao por categoria
    cat_data = []
    for cat in Category.objects.filter(tenant=tenant):
        count = products.filter(category=cat).count()
        if count > 0:
            cat_data.append({"name": cat.name, "count": count})
    cat_labels = [c["name"] for c in cat_data]
    cat_values = [c["count"] for c in cat_data]

    # Status de estoque
    ok_count = total_products - low_stock_count - expired_count
    status_data = [ok_count, low_stock_count, expired_count, expiring_count]

    # Movimentacoes por tipo
    type_data = movements.values("movement_type").annotate(total=Sum("quantity"))
    type_map = {"in": 0, "out": 0, "adjustment": 0, "waste": 0}
    for t in type_data:
        type_map[t["movement_type"]] = float(t["total"])

    context = {
        "total_products": total_products,
        "total_stock_value": total_stock_value,
        "low_stock_count": low_stock_count,
        "expired_count": expired_count,
        "expiring_count": expiring_count,
        "movement_labels": json.dumps(movement_labels),
        "movement_in": json.dumps(movement_in),
        "movement_out": json.dumps(movement_out),
        "movement_waste": json.dumps(movement_waste),
        "top_labels": json.dumps(top_labels),
        "top_values": json.dumps(top_values),
        "cat_labels": json.dumps(cat_labels),
        "cat_values": json.dumps(cat_values),
        "status_data": json.dumps(status_data),
        "type_in": type_map["in"],
        "type_out": type_map["out"],
        "type_waste": type_map["waste"],
        "type_adjustment": type_map["adjustment"],
    }
    return render(request, "inventory/analytics.html", context)
