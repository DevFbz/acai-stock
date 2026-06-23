from django.urls import path

from inventory import views
from inventory.analytics import analytics_dashboard

app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("analytics/", analytics_dashboard, name="analytics"),

    # Produtos
    path("products/", views.product_list, name="product_list"),
    path("products/new/", views.product_create, name="product_create"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("products/export/csv/", views.export_products_csv, name="export_products_csv"),

    # Categorias
    path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),

    # Fornecedores
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/new/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:pk>/edit/", views.supplier_update, name="supplier_update"),

    # Movimentacoes
    path("movements/", views.movement_list, name="movement_list"),
    path("movements/new/", views.movement_create, name="movement_create"),

    # Pedidos de Compra
    path("purchase-orders/", views.purchase_order_list, name="purchase_order_list"),
    path("purchase-orders/new/", views.purchase_order_create, name="purchase_order_create"),
    path("purchase-orders/<int:pk>/", views.purchase_order_detail, name="purchase_order_detail"),
    path("purchase-orders/<int:pk>/<str:status>/", views.purchase_order_change_status, name="purchase_order_status"),
]
