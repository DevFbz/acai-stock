from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q

from inventory.models import Product, Category, Supplier, StockMovement, PurchaseOrder


@login_required
def dashboard(request):
    tenant = request.user.tenant
    products = Product.objects.filter(tenant=tenant, is_active=True)
    low_stock = [p for p in products if p.is_low_stock]
    expiring_soon = [p for p in products if p.days_to_expiry is not None and p.days_to_expiry <= 7 and not p.is_expired]
    expired = [p for p in products if p.is_expired]
    recent_movements = StockMovement.objects.filter(product__tenant=tenant)[:10]

    context = {
        "products_count": products.count(),
        "low_stock": low_stock,
        "expiring_soon": expiring_soon,
        "expired": expired,
        "recent_movements": recent_movements,
        "suppliers_count": Supplier.objects.filter(tenant=tenant, is_active=True).count(),
        "po_count": PurchaseOrder.objects.filter(tenant=tenant).count(),
    }
    return render(request, "inventory/dashboard.html", context)


@login_required
def product_list(request):
    tenant = request.user.tenant
    qs = Product.objects.filter(tenant=tenant)
    search = request.GET.get("q")
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search) | Q(barcode__icontains=search))
    return render(request, "inventory/product_list.html", {"products": qs, "search": search})


@login_required
def supplier_list(request):
    tenant = request.user.tenant
    qs = Supplier.objects.filter(tenant=tenant)
    return render(request, "inventory/supplier_list.html", {"suppliers": qs})


@login_required
def movement_list(request):
    tenant = request.user.tenant
    qs = StockMovement.objects.filter(product__tenant=tenant)
    return render(request, "inventory/movement_list.html", {"movements": qs})


@login_required
def purchase_order_list(request):
    tenant = request.user.tenant
    qs = PurchaseOrder.objects.filter(tenant=tenant)
    return render(request, "inventory/purchase_order_list.html", {"orders": qs})
