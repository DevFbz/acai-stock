from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from inventory.models import Category, Product, Supplier, StockMovement, PurchaseOrder
from reports.models import Report
from accounts.models import User
from api.serializers import (
    CategorySerializer, ProductSerializer, SupplierSerializer,
    StockMovementSerializer, PurchaseOrderSerializer,
    ReportSerializer, UserSerializer,
)


class TenantScopedViewSet(viewsets.ModelViewSet):
    """Base ViewSet that filters by tenant and auto-assigns on create."""

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = self.request.user.tenant
        if tenant:
            qs = qs.filter(tenant=tenant)
        else:
            qs = qs.none()
        return qs

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class CategoryViewSet(TenantScopedViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class SupplierViewSet(TenantScopedViewSet):
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()


class ProductViewSet(TenantScopedViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        products = self.get_queryset().filter(is_active=True)
        low = [p for p in products if p.is_low_stock]
        data = ProductSerializer(low, many=True).data
        return Response(data)

    @action(detail=False, methods=["get"])
    def expired(self, request):
        products = self.get_queryset().filter(is_active=True)
        expired = [p for p in products if p.is_expired]
        data = ProductSerializer(expired, many=True).data
        return Response(data)


class StockMovementViewSet(viewsets.ModelViewSet):
    serializer_class = StockMovementSerializer
    queryset = StockMovement.objects.all()

    def get_queryset(self):
        return self.queryset.filter(product__tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        instance = serializer.save()
        product = instance.product
        if instance.movement_type == "in":
            product.current_stock += instance.quantity
        elif instance.movement_type in ("out", "waste"):
            product.current_stock -= instance.quantity
        elif instance.movement_type == "adjustment":
            product.current_stock = instance.quantity
        product.save(update_fields=["current_stock", "updated_at"])


class PurchaseOrderViewSet(TenantScopedViewSet):
    serializer_class = PurchaseOrderSerializer
    queryset = PurchaseOrder.objects.all()

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(PurchaseOrder.status.field.choices):
            return Response({"error": "Status invalido"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        if new_status == "received":
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
        return Response(PurchaseOrderSerializer(order).data)


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.user.tenant)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
