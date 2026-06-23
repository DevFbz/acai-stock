from django.urls import path

from inventory import views

app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", views.product_list, name="product_list"),
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("movements/", views.movement_list, name="movement_list"),
    path("purchase-orders/", views.purchase_order_list, name="purchase_order_list"),
]
