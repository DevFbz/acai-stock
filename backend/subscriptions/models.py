from django.db import models
from django.utils import timezone

from tenants.models import Tenant


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Ativa"),
        ("pending", "Pendente"),
        ("overdue", "Em atraso"),
        ("suspended", "Suspensa"),
        ("canceled", "Cancelada"),
    ]

    BILLING_CYCLE_CHOICES = [
        ("monthly", "Mensal"),
        ("quarterly", "Trimestral"),
        ("yearly", "Anual"),
    ]

    tenant = models.OneToOneField(
        Tenant, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.CharField(max_length=20, choices=Tenant.PLAN_CHOICES, default="basic")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default="monthly")
    amount = models.DecimalField("Valor", max_digits=10, decimal_places=2, default=99.90)
    current_period_start = models.DateField("Início do período", default=timezone.now)
    current_period_end = models.DateField("Fim do período", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"

    def __str__(self):
        return f"{self.tenant.name} - {self.get_plan_display()}"

    @property
    def is_overdue(self):
        if not self.current_period_end:
            return False
        return timezone.now().date() > self.current_period_end and self.status == "active"


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("paid", "Pago"),
        ("failed", "Falhou"),
        ("refunded", "Reembolsado"),
    ]

    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    due_date = models.DateField("Vencimento")
    paid_at = models.DateTimeField("Pago em", null=True, blank=True)
    method = models.CharField("Método", max_length=50, blank=True)
    reference = models.CharField("Referência", max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.subscription.tenant.name} - {self.amount} - {self.get_status_display()}"
