from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.views import (
    CategoryViewSet, SupplierViewSet, ProductViewSet,
    StockMovementViewSet, PurchaseOrderViewSet, ReportViewSet, MeView,
)

app_name = "api"

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("suppliers", SupplierViewSet)
router.register("products", ProductViewSet)
router.register("movements", StockMovementViewSet)
router.register("purchase-orders", PurchaseOrderViewSet)
router.register("reports", ReportViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="swagger"),
]
