from django.contrib import admin

from inventory.models import (
    Category, Product, Supplier, StockMovement, PurchaseOrder, PurchaseOrderItem,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "created_at")
    list_filter = ("tenant",)
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "email", "is_active", "tenant")
    list_filter = ("is_active", "tenant")
    search_fields = ("name", "contact_person", "cnpj")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "sku", "category", "current_stock", "min_stock",
        "is_low_stock", "expiry_date", "is_active",
    )
    list_filter = ("is_active", "category", "tenant")
    search_fields = ("name", "sku", "barcode")
    readonly_fields = ("is_low_stock", "is_expired", "days_to_expiry")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "movement_type", "quantity", "reason", "created_at")
    list_filter = ("movement_type", "created_at")
    search_fields = ("product__name", "reason")
    date_hierarchy = "created_at"


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "status", "total", "expected_date", "created_at")
    list_filter = ("status", "tenant")
    search_fields = ("supplier__name",)
    inlines = [PurchaseOrderItemInline]
    date_hierarchy = "created_at"
