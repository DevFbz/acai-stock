from rest_framework import serializers

from inventory.models import Category, Product, Supplier, StockMovement, PurchaseOrder, PurchaseOrderItem
from tenants.models import Tenant
from accounts.models import User
from reports.models import Report


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["id", "name", "contact_person", "phone", "email", "cnpj", "address", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "sku", "barcode", "category", "category_name",
            "supplier", "supplier_name", "unit", "min_stock", "max_stock",
            "current_stock", "cost_price", "sale_price", "expiry_date",
            "is_active", "is_low_stock", "is_expired", "days_to_expiry",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = StockMovement
        fields = ["id", "product", "product_name", "movement_type", "quantity", "reason", "reference", "created_at"]
        read_only_fields = ["id", "created_at"]


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_cost", "subtotal"]
        read_only_fields = ["id", "subtotal"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id", "supplier", "supplier_name", "status", "total",
            "expected_date", "received_at", "notes", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "total", "received_at", "created_at", "updated_at"]


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "slug", "plan", "status", "is_active", "created_at"]
        read_only_fields = ["id", "slug", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "theme", "phone", "is_tenant_owner"]
        read_only_fields = ["id"]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "title", "report_type", "content", "summary", "generated_by", "created_at"]
        read_only_fields = ["id", "created_at"]
