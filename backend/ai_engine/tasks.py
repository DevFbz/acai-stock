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
        products = Product.objects.filter(tenant=tenant, is_active=True)
        stock_data = [
            {
                "name": p.name,
                "current": float(p.current_stock),
                "min": float(p.min_stock),
                "unit": p.unit,
                "expiry": p.expiry_date.isoformat() if p.expiry_date else None,
                "low": p.is_low_stock,
                "cost": float(p.cost_price),
                "sale": float(p.sale_price),
            }
            for p in products
        ]
        movements = list(
            StockMovement.objects.filter(product__tenant=tenant)[:50].values(
                "product__name", "movement_type", "quantity", "created_at"
            )
        )
        content = generate_ai_report(tenant.name, stock_data, movements, report_type)
        report = Report.objects.create(
            tenant=tenant,
            title=f"Relatorio {report_type} - {tenant.name} - {timezone.now().strftime('%d/%m/%Y')}",
            report_type=report_type,
            content=content,
            summary=content[:300],
            generated_by="celery_scheduled",
            metadata={"task_id": self.request.id, "report_type": report_type},
        )
        return {"status": "ok", "report_id": report.pk}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task
def check_overdue_subscriptions():
    from subscriptions.models import Subscription
    today = timezone.now().date()
    overdue = Subscription.objects.filter(
        status="active", current_period_end__lt=today
    )
    count = 0
    for sub in overdue:
        sub.status = "overdue"
        sub.save(update_fields=["status", "updated_at"])
        sub.tenant.status = "blocked"
        sub.tenant.is_active = False
        sub.tenant.save(update_fields=["status", "is_active", "updated_at"])
        count += 1
    return {"blocked": count}


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
