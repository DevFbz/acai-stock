from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse
import csv

from inventory.models import Product, Category, Supplier, StockMovement, PurchaseOrder, PurchaseOrderItem
from inventory.forms import (
    CategoryForm, ProductForm, SupplierForm, StockMovementForm,
    PurchaseOrderForm, PurchaseOrderItemForm,
)


# ==================== Dashboard ====================

@login_required
def dashboard(request):
    tenant = request.user.tenant
    products = Product.objects.filter(tenant=tenant, is_active=True)
    low_stock = [p for p in products if p.is_low_stock]
    expiring_soon = [p for p in products if p.days_to_expiry is not None and p.days_to_expiry <= 7 and not p.is_expired]
    expired = [p for p in products if p.is_expired]
    recent_movements = StockMovement.objects.filter(product__tenant=tenant)[:10]
    total_value = sum(float(p.current_stock) * float(p.cost_price) for p in products)
    context = {
        "products_count": products.count(),
        "low_stock": low_stock,
        "expiring_soon": expiring_soon,
        "expired": expired,
        "recent_movements": recent_movements,
        "suppliers_count": Supplier.objects.filter(tenant=tenant, is_active=True).count(),
        "po_count": PurchaseOrder.objects.filter(tenant=tenant).count(),
        "total_stock_value": total_value,
    }
    return render(request, "inventory/dashboard.html", context)


# ==================== Produtos ====================

@login_required
def product_list(request):
    tenant = request.user.tenant
    qs = Product.objects.filter(tenant=tenant)
    search = request.GET.get("q")
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search) | Q(barcode__icontains=search))
    cat = request.GET.get("category")
    if cat:
        qs = qs.filter(category_id=cat)
    categories = Category.objects.filter(tenant=tenant)
    return render(request, "inventory/product_list.html", {
        "products": qs, "search": search, "categories": categories,
    })


@login_required
def product_detail(request, pk):
    tenant = request.user.tenant
    product = get_object_or_404(Product, pk=pk, tenant=tenant)
    movements = StockMovement.objects.filter(product=product)
    return render(request, "inventory/product_detail.html", {"product": product, "movements": movements})


@login_required
def product_create(request):
    tenant = request.user.tenant
    if request.method == "POST":
        form = ProductForm(request.POST, tenant=tenant)
        if form.is_valid():
            form.save()
            return redirect("inventory:product_list")
    else:
        form = ProductForm(tenant=tenant)
    return render(request, "inventory/product_form.html", {"form": form, "title": "Novo Produto"})


@login_required
def product_update(request, pk):
    tenant = request.user.tenant
    product = get_object_or_404(Product, pk=pk, tenant=tenant)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product, tenant=tenant)
        if form.is_valid():
            form.save()
            return redirect("inventory:product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product, tenant=tenant)
    return render(request, "inventory/product_form.html", {"form": form, "title": "Editar Produto"})


@login_required
def product_delete(request, pk):
    tenant = request.user.tenant
    product = get_object_or_404(Product, pk=pk, tenant=tenant)
    if request.method == "POST":
        product.is_active = False
        product.save(update_fields=["is_active", "updated_at"])
        return redirect("inventory:product_list")
    return render(request, "inventory/confirm_delete.html", {
        "obj": product, "cancel_url": "inventory:product_list",
    })


# ==================== Categorias ====================

@login_required
def category_list(request):
    tenant = request.user.tenant
    qs = Category.objects.filter(tenant=tenant)
    return render(request, "inventory/category_list.html", {"categories": qs})


@login_required
def category_create(request):
    tenant = request.user.tenant
    if request.method == "POST":
        form = CategoryForm(request.POST, tenant=tenant)
        if form.is_valid():
            form.save()
            return redirect("inventory:category_list")
    else:
        form = CategoryForm(tenant=tenant)
    return render(request, "inventory/category_form.html", {"form": form, "title": "Nova Categoria"})


@login_required
def category_update(request, pk):
    tenant = request.user.tenant
    category = get_object_or_404(Category, pk=pk, tenant=tenant)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category, tenant=tenant)
        if form.is_valid():
            form.save()
            return redirect("inventory:category_list")
    else:
        form = CategoryForm(instance=category, tenant=tenant)
    return render(request, "inventory/category_form.html", {"form": form, "title": "Editar Categoria"})


# ==================== Fornecedores ====================

@login_required
def supplier_list(request):
    tenant = request.user.tenant
    qs = Supplier.objects.filter(tenant=tenant)
    return render(request, "inventory/supplier_list.html", {"suppliers": qs})


@login_required
def supplier_create(request):
    tenant = request.user.tenant
    if request.method == "POST":
        form = SupplierForm(request.POST, tenant=tenant)
        if form.is_valid():
            form.save()
            return redirect("inventory:supplier_list")
    else:
        form = SupplierForm(tenant=tenant)
    return render(request, "inventory/supplier_form.html", {"form": form, "title": "Novo Fornecedor"})


@login_required
def supplier_update(request, pk):
    tenant = request.user.tenant
    supplier = get_object_or_404(Supplier, pk=pk, tenant=tenant)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier, tenant=tenant)
        if form.is_valid():
            form.save()
            return redirect("inventory:supplier_list")
    else:
        form = SupplierForm(instance=supplier, tenant=tenant)
    return render(request, "inventory/supplier_form.html", {"form": form, "title": "Editar Fornecedor"})


# ==================== Movimentacoes ====================

@login_required
def movement_list(request):
    tenant = request.user.tenant
    qs = StockMovement.objects.filter(product__tenant=tenant)
    mtype = request.GET.get("type")
    if mtype:
        qs = qs.filter(movement_type=mtype)
    return render(request, "inventory/movement_list.html", {"movements": qs, "filter_type": mtype})


@login_required
def movement_create(request):
    tenant = request.user.tenant
    if request.method == "POST":
        form = StockMovementForm(request.POST, tenant=tenant)
        if form.is_valid():
            form.save()
            return redirect("inventory:movement_list")
    else:
        form = StockMovementForm(tenant=tenant)
    return render(request, "inventory/movement_form.html", {"form": form, "title": "Nova Movimentacao"})


# ==================== Pedidos de Compra ====================

@login_required
def purchase_order_list(request):
    tenant = request.user.tenant
    qs = PurchaseOrder.objects.filter(tenant=tenant)
    return render(request, "inventory/purchase_order_list.html", {"orders": qs})


@login_required
def purchase_order_detail(request, pk):
    tenant = request.user.tenant
    order = get_object_or_404(PurchaseOrder, pk=pk, tenant=tenant)
    items = order.items.all()
    if request.method == "POST" and "add_item" in request.POST:
        item_form = PurchaseOrderItemForm(request.POST, tenant=tenant)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.purchase_order = order
            item.save()
            order.total = sum(i.subtotal for i in order.items.all())
            order.save(update_fields=["total", "updated_at"])
            return redirect("inventory:purchase_order_detail", pk=order.pk)
    else:
        item_form = PurchaseOrderItemForm(tenant=tenant)
    return render(request, "inventory/purchase_order_detail.html", {
        "order": order, "items": items, "item_form": item_form,
    })


@login_required
def purchase_order_create(request):
    tenant = request.user.tenant
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST, tenant=tenant)
        if form.is_valid():
            order = form.save()
            return redirect("inventory:purchase_order_detail", pk=order.pk)
    else:
        form = PurchaseOrderForm(tenant=tenant)
    return render(request, "inventory/purchase_order_form.html", {"form": form, "title": "Novo Pedido de Compra"})


@login_required
def purchase_order_change_status(request, pk, status):
    tenant = request.user.tenant
    order = get_object_or_404(PurchaseOrder, pk=pk, tenant=tenant)
    order.status = status
    if status == "received":
        from django.utils import timezone
        order.received_at = timezone.now()
        for item in order.items.all():
            product = item.product
            product.current_stock += item.quantity
            product.save(update_fields=["current_stock", "updated_at"])
            StockMovement.objects.create(
                product=product, movement_type="in",
                quantity=item.quantity, reason=f"PO-{order.id:06d}",
            )
    order.save()
    return redirect("inventory:purchase_order_detail", pk=order.pk)


# ==================== Export CSV ====================

@login_required
def export_products_csv(request):
    tenant = request.user.tenant
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=produtos.csv"
    writer = csv.writer(response)
    writer.writerow(["Nome", "SKU", "Categoria", "Estoque", "Minimo", "Unidade", "Custo", "Venda", "Validade"])
    for p in Product.objects.filter(tenant=tenant):
        writer.writerow([
            p.name, p.sku, p.category.name if p.category else "",
            p.current_stock, p.min_stock, p.get_unit_display(),
            p.cost_price, p.sale_price,
            p.expiry_date.isoformat() if p.expiry_date else "",
        ])
    return response
