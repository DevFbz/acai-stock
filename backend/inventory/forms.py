from django import forms
from django.utils import timezone

from inventory.models import (
    Category, Product, Supplier, StockMovement, PurchaseOrder, PurchaseOrderItem,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Nome da categoria"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Descricao (opcional)"}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant
        if commit:
            instance.save()
        return instance


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "phone", "email", "cnpj", "address", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Nome do fornecedor"}),
            "contact_person": forms.TextInput(attrs={"class": "form-input", "placeholder": "Pessoa de contato"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "(00) 00000-0000"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "email@fornecedor.com"}),
            "cnpj": forms.TextInput(attrs={"class": "form-input", "placeholder": "00.000.000/0000-00"}),
            "address": forms.Textarea(attrs={"class": "form-input", "rows": 2, "placeholder": "Endereco"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check"}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant
        if commit:
            instance.save()
        return instance


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "sku", "barcode", "category", "supplier", "unit",
            "min_stock", "max_stock", "current_stock",
            "cost_price", "sale_price", "expiry_date", "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Nome do produto"}),
            "sku": forms.TextInput(attrs={"class": "form-input", "placeholder": "SKU"}),
            "barcode": forms.TextInput(attrs={"class": "form-input", "placeholder": "Codigo de barras"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "supplier": forms.Select(attrs={"class": "form-input"}),
            "unit": forms.Select(attrs={"class": "form-input"}),
            "min_stock": forms.NumberInput(attrs={"class": "form-input", "step": "0.001"}),
            "max_stock": forms.NumberInput(attrs={"class": "form-input", "step": "0.001"}),
            "current_stock": forms.NumberInput(attrs={"class": "form-input", "step": "0.001"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "sale_price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "expiry_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check"}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant:
            self.fields["category"].queryset = Category.objects.filter(tenant=tenant)
            self.fields["supplier"].queryset = Supplier.objects.filter(tenant=tenant, is_active=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant
        if commit:
            instance.save()
        return instance


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["product", "movement_type", "quantity", "reason", "reference"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-input"}),
            "movement_type": forms.Select(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "step": "0.001", "min": "0.001"}),
            "reason": forms.TextInput(attrs={"class": "form-input", "placeholder": "Motivo da movimentacao"}),
            "reference": forms.TextInput(attrs={"class": "form-input", "placeholder": "Referencia (opcional)"}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant:
            self.fields["product"].queryset = Product.objects.filter(tenant=tenant, is_active=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        product = instance.product
        if instance.movement_type == "in":
            product.current_stock += instance.quantity
        elif instance.movement_type in ("out", "waste"):
            product.current_stock -= instance.quantity
        elif instance.movement_type == "adjustment":
            product.current_stock = instance.quantity
        product.save(update_fields=["current_stock", "updated_at"])
        if commit:
            instance.save()
        return instance


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["supplier", "expected_date", "notes"]
        widgets = {
            "supplier": forms.Select(attrs={"class": "form-input"}),
            "expected_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Observacoes"}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant:
            self.fields["supplier"].queryset = Supplier.objects.filter(tenant=tenant, is_active=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant
        if commit:
            instance.save()
        return instance


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ["product", "quantity", "unit_cost"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "step": "0.001", "min": "0.001"}),
            "unit_cost": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields["product"].queryset = Product.objects.filter(tenant=tenant, is_active=True)

