from celery import shared_task

from billing.services import check_and_notify_overdue


@shared_task
def send_overdue_billing_emails():
    """Task diaria que verifica e envia emails de cobranca para inadimplentes."""
    results = check_and_notify_overdue()
    return {"sent": len(results), "details": results}
