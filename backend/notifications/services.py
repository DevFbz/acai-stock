from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from notifications.models import Notification, NotificationSetting
from inventory.models import Product
from tenants.models import Tenant


def create_notification(tenant, title, message, notification_type="system", severity="info", user=None, url=""):
    notif = Notification.objects.create(
        tenant=tenant,
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        severity=severity,
        url=url,
    )
    return notif


def send_email_notification(tenant, subject, body, recipient=None):
    try:
        ns, _ = NotificationSetting.objects.get_or_create(tenant=tenant)
        if not ns.email_enabled:
            return False
    except Exception:
        pass

    recipients = []
    if recipient:
        recipients.append(recipient)
    else:
        users = tenant.users.filter(is_active=True)
        recipients = [u.email for u in users if u.email]

    if not recipients:
        return False

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True,
    )
    return True


def check_stock_alerts():
    """Verifica todos os tenants e cria notificacoes para produtos com problemas."""
    results = {"low_stock": 0, "expiring": 0, "expired": 0}

    for tenant in Tenant.objects.filter(status="active", is_active=True):
        products = Product.objects.filter(tenant=tenant, is_active=True)

        low_stock = [p for p in products if p.is_low_stock]
        expiring = [p for p in products if p.days_to_expiry is not None and 0 < p.days_to_expiry <= 7 and not p.is_expired]
        expired = [p for p in products if p.is_expired]

        if low_stock:
            names = ", ".join(p.name for p in low_stock[:5])
            create_notification(
                tenant=tenant,
                title=f"Estoque Baixo - {len(low_stock)} produto(s)",
                message=f"Produtos com estoque baixo: {names}",
                notification_type="low_stock",
                severity="warning",
                url="/estoque/products/",
            )
            send_email_notification(
                tenant, f"[Acai Stock] Estoque Baixo - {tenant.name}",
                f"Atencao! Os seguintes produtos estao com estoque baixo:\n\n{names}\n\nAcesse o sistema para reposicao.",
            )
            results["low_stock"] += len(low_stock)

        if expiring:
            names = ", ".join(f"{p.name} ({p.days_to_expiry}d)" for p in expiring[:5])
            create_notification(
                tenant=tenant,
                title=f"Vencimento Proximo - {len(expiring)} produto(s)",
                message=f"Produtos vencendo em ate 7 dias: {names}",
                notification_type="expiry",
                severity="warning",
                url="/estoque/products/",
            )
            results["expiring"] += len(expiring)

        if expired:
            names = ", ".join(p.name for p in expired[:5])
            create_notification(
                tenant=tenant,
                title=f"Produtos Vencidos - {len(expired)} produto(s)",
                message=f"Produtos vencidos no estoque: {names}",
                notification_type="expired",
                severity="danger",
                url="/estoque/products/",
            )
            results["expired"] += len(expired)

    return results
