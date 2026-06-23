from django.db import models
from django.utils import timezone

from tenants.models import Tenant


class Category(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField("Nome", max_length=100)
    description = models.TextField("Descrição", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        unique_together = ("tenant", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="suppliers")
    name = models.CharField("Nome", max_length=200)
    contact_person = models.CharField("Contato", max_length=100, blank=True)
    phone = models.CharField("Telefone", max_length=20, blank=True)
    email = models.EmailField("E-mail", blank=True)
    cnpj = models.CharField("CNPJ", max_length=20, blank=True)
    address = models.TextField("Endereço", blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ("un", "Unidade"),
        ("kg", "Quilograma"),
        ("g", "Grama"),
        ("l", "Litro"),
        ("ml", "Mililitro"),
        ("cx", "Caixa"),
        ("pct", "Pacote"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="products")
    name = models.CharField("Nome", max_length=200)
    sku = models.CharField("SKU", max_length=50, blank=True)
    barcode = models.CharField("Código de barras", max_length=50, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    unit = models.CharField("Unidade", max_length=10, choices=UNIT_CHOICES, default="un")
    min_stock = models.DecimalField("Estoque mínimo", max_digits=10, decimal_places=3, default=0)
    max_stock = models.DecimalField("Estoque máximo", max_digits=10, decimal_places=3, default=0)
    current_stock = models.DecimalField("Estoque atual", max_digits=10, decimal_places=3, default=0)
    cost_price = models.DecimalField("Preço de custo", max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField("Preço de venda", max_digits=10, decimal_places=2, default=0)
    expiry_date = models.DateField("Validade", null=True, blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        unique_together = ("tenant", "sku")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})" if self.sku else self.name

    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock and self.min_stock > 0

    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return timezone.now().date() > self.expiry_date

    @property
    def days_to_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now().date()).days


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ("in", "Entrada"),
        ("out", "Saída"),
        ("adjustment", "Ajuste"),
        ("waste", "Perda"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField("Tipo", max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField("Quantidade", max_digits=10, decimal_places=3)
    reason = models.CharField("Motivo", max_length=200, blank=True)
    reference = models.CharField("Referência", max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("sent", "Enviado"),
        ("received", "Recebido"),
        ("canceled", "Cancelado"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="purchase_orders")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="draft")
    total = models.DecimalField("Total", max_digits=12, decimal_places=2, default=0)
    expected_date = models.DateField("Data prevista", null=True, blank=True)
    received_at = models.DateTimeField("Recebido em", null=True, blank=True)
    notes = models.TextField("Observações", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido de Compra"
        verbose_name_plural = "Pedidos de Compra"
        ordering = ["-created_at"]

    def __str__(self):
        return f"PO-{self.id:06d} - {self.supplier or 'Sem fornecedor'}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField("Quantidade", max_digits=10, decimal_places=3)
    unit_cost = models.DecimalField("Custo unitário", max_digits=10, decimal_places=2)
    subtotal = models.DecimalField("Subtotal", max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
