from django.db import models
from django.conf import settings

from tenants.models import Tenant


class Notification(models.Model):
    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("success", "Sucesso"),
        ("warning", "Aviso"),
        ("danger", "Critico"),
    ]

    TYPE_CHOICES = [
        ("low_stock", "Estoque Baixo"),
        ("expiry", "Vencimento Proximo"),
        ("expired", "Produto Vencido"),
        ("billing", "Cobranca"),
        ("system", "Sistema"),
        ("ai_report", "Relatorio IA"),
        ("purchase_order", "Pedido de Compra"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="notifications")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="notifications",
    )
    title = models.CharField("Titulo", max_length=200)
    message = models.TextField("Mensagem")
    notification_type = models.CharField("Tipo", max_length=30, choices=TYPE_CHOICES, default="system")
    severity = models.CharField("Severidade", max_length=20, choices=SEVERITY_CHOICES, default="info")
    is_read = models.BooleanField("Lida", default=False)
    url = models.CharField("URL de acao", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificacao"
        verbose_name_plural = "Notificacoes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.tenant.name})"


class NotificationSetting(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="notification_settings")
    email_enabled = models.BooleanField("Notificacoes por email", default=True)
    low_stock_alerts = models.BooleanField("Alertas de estoque baixo", default=True)
    expiry_alerts = models.BooleanField("Alertas de vencimento", default=True)
    daily_summary = models.BooleanField("Resumo diario", default=False)
    weekly_report = models.BooleanField("Relatorio semanal", default=True)

    class Meta:
        verbose_name = "Configuracao de Notificacoes"
        verbose_name_plural = "Configuracoes de Notificacoes"

    def __str__(self):
        return f"Config - {self.tenant.name}"
