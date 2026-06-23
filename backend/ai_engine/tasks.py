from celery import shared_task
from django.utils import timezone

from inventory.models import Product, StockMovement
from reports.models import Report
from ai_engine.graph import generate_ai_report
from tenants.models import Tenant


@shared_task(bind=True)
def generate_scheduled_report(self, tenant_id, report_type="ai_custom"):
    try:
        tenant = Tenant.objects.get(pk=tenant_id)
        content = generate_ai_report(tenant, report_type)
        report = Report.objects.create(
            tenant=tenant,
            title=f"Relatorio {report_type} - {tenant.name} - {timezone.now().strftime('%d/%m/%Y')}",
            report_type=report_type,
            content=content,
            summary=content[:300],
            generated_by="celery_scheduled",
            metadata={"task_id": self.request.id, "report_type": report_type, "knowledge_base": True},
        )
        return {"status": "ok", "report_id": report.pk}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task
def check_overdue_subscriptions():
    from billing.services import check_and_notify_overdue
    results = check_and_notify_overdue()
    return {"processed": len(results), "details": results}


@shared_task
def check_low_stock_alerts():
    results = []
    for tenant in Tenant.objects.filter(status="active"):
        low = Product.objects.filter(tenant=tenant, is_active=True)
        alerts = [
            {"tenant": tenant.name, "product": p.name, "current": float(p.current_stock), "min": float(p.min_stock)}
            for p in low
            if p.is_low_stock
        ]
        if alerts:
            Report.objects.create(
                tenant=tenant,
                title=f"Alerta de Estoque Baixo - {timezone.now().strftime('%d/%m/%Y')}",
                report_type="low_stock",
                content=str(alerts),
                summary=f"{len(alerts)} produto(s) com estoque baixo",
                generated_by="celery_alert",
            )
            results.extend(alerts)
    return {"alerts": len(results)}
