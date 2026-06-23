from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string

from tenants.models import Tenant
from subscriptions.models import Subscription, Payment
from billing.models import BillingAlert


def send_billing_email(tenant, subject, message, recipient=None):
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
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
    return True


def check_and_notify_overdue():
    """Verifica assinaturas em atraso e envia email de cobranca."""
    from datetime import timedelta
    today = timezone.now().date()
    results = []

    for sub in Subscription.objects.filter(status__in=["active", "overdue"]):
        if not sub.current_period_end:
            continue
        days_overdue = (today - sub.current_period_end).days
        if days_overdue <= 0:
            continue

        tenant = sub.tenant

        # Evita enviar alerta duplicado no mesmo dia
        existing = BillingAlert.objects.filter(
            tenant=tenant, status="sent", created_at__date=today
        ).exists()
        if existing:
            continue

        # Determina nivel de urgencia
        if days_overdue <= 3:
            level = "lembrete"
            subject = f"Lembrete: Pagamento da assinatura Acai Stock - {tenant.name}"
            tone = "amigavel"
        elif days_overdue <= 7:
            level = "cobranca"
            subject = f"Cobranca: Pagamento em atraso - Acai Stock - {tenant.name}"
            tone = "firme"
        else:
            level = "urgente"
            subject = f"URGENTE: Acesso sera bloqueado - Acai Stock - {tenant.name}"
            tone = "urgente"

        message = f"""Prezado(a) {tenant.name},

Identificamos que o pagamento da sua assinatura do Acai Stock esta em atraso ha {days_overdue} dia(s).

Detalhes:
- Plano: {sub.get_plan_display()}
- Ciclo: {sub.get_billing_cycle_display()}
- Valor: R$ {sub.amount}
- Vencimento: {sub.current_period_end.strftime('%d/%m/%Y')}

Para regularizar e manter o acesso ao sistema, entre em contato:

E-mail: suporte@acaistock.com
Telefone/WhatsApp: (00) 00000-0000

{"Apos 7 dias de atraso, o acesso ao sistema sera automaticamente bloqueado." if days_overdue <= 7 else "Seu acesso ao sistema pode ser bloqueado a qualquer momento. Regularize o quanto antes!"}

Apos o pagamento, seu acesso sera reativado imediatamente.

Atenciosamente,
Equipe Acai Stock
"""

        sent = send_billing_email(tenant, subject, message)

        alert = BillingAlert.objects.create(
            tenant=tenant,
            subject=subject,
            message=message,
            status="sent" if sent else "pending",
            sent_at=timezone.now() if sent else None,
            days_overdue=days_overdue,
            amount_due=sub.amount,
        )

        # Bloqueia apos 7 dias
        if days_overdue > 7:
            tenant.status = "blocked"
            tenant.is_active = False
            tenant.save(update_fields=["status", "is_active", "updated_at"])
            sub.status = "overdue"
            sub.save(update_fields=["status", "updated_at"])

        results.append({
            "tenant": tenant.name,
            "days_overdue": days_overdue,
            "level": level,
            "sent": sent,
        })

    return results


def send_welcome_email(tenant, user):
    subject = f"Bem-vindo ao Acai Stock, {tenant.name}!"
    message = f"""Ola {user.display_name},

Sua conta no Acai Stock foi criada com sucesso!

Tenant: {tenant.name}
Plano: {tenant.get_plan_display()}

Acesse o sistema e comece a gerenciar seu estoque.

Atenciosamente,
Equipe Acai Stock
"""
    if user.email:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
