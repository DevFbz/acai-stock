from django.db import models

from tenants.models import Tenant


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ("stock_summary", "Resumo de Estoque"),
        ("low_stock", "Estoque Baixo"),
        ("expiry", "Validade"),
        ("movement", "Movimentações"),
        ("sales_forecast", "Previsão de Vendas"),
        ("ai_custom", "Relatório IA Personalizado"),
        ("supplier_performance", "Desempenho de Fornecedores"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="reports")
    title = models.CharField("Título", max_length=200)
    report_type = models.CharField("Tipo", max_length=30, choices=REPORT_TYPE_CHOICES)
    content = models.TextField("Conteúdo", blank=True)
    summary = models.TextField("Resumo", blank=True)
    metadata = models.JSONField("Metadados", default=dict, blank=True)
    generated_by = models.CharField("Gerado por", max_length=50, default="system")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.tenant.name})"
