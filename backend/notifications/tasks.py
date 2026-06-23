from celery import shared_task

from notifications.services import check_stock_alerts


@shared_task
def daily_stock_check():
    """Task diaria que verifica estoque e cria notificacoes."""
    results = check_stock_alerts()
    return results


@shared_task
def send_weekly_summary():
    """Task semanal que envia resumo por email para todos os tenants ativos."""
    from ai_engine.nlg import ReportGenerator
    from notifications.services import send_email_notification
    from tenants.models import Tenant

    count = 0
    for tenant in Tenant.objects.filter(status="active", is_active=True):
        try:
            generator = ReportGenerator(tenant)
            report = generator.gerar_relatorio_geral()
            send_email_notification(
                tenant,
                f"Resumo Semanal de Estoque - {tenant.name}",
                f"Segue o resumo semanal do seu estoque:\n\n{report[:2000]}\n\nAcesse o sistema para detalhes completos.",
            )
            count += 1
        except Exception as e:
            pass
    return {"sent": count}
