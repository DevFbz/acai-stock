from django.db import models
from django.utils import timezone

from tenants.models import Tenant


class BillingAlert(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("sent", "Enviado"),
        ("resolved", "Resolvido"),
        ("escalated", "Escalado"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="billing_alerts")
    subject = models.CharField("Assunto", max_length=200)
    message = models.TextField("Mensagem")
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="pending")
    sent_at = models.DateTimeField("Enviado em", null=True, blank=True)
    days_overdue = models.IntegerField("Dias em atraso", default=0)
    amount_due = models.DecimalField("Valor devido", max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Alerta de Cobranca"
        verbose_name_plural = "Alertas de Cobranca"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tenant.name} - {self.subject}"
