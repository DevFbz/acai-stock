from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages

from billing.models import BillingAlert
from billing.services import check_and_notify_overdue
from billing.tasks import send_overdue_billing_emails


@login_required
def billing_panel(request):
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Acesso restrito ao administrador.")

    alerts = BillingAlert.objects.all().order_by("-created_at")[:50]
    if request.method == "POST" and "run_check" in request.POST:
        results = check_and_notify_overdue()
        messages.success(request, f"{len(results)} cobranca(s) processada(s).")
        # Re-buscar apos processamento
        alerts = BillingAlert.objects.all().order_by("-created_at")[:50]
    return render(request, "billing/panel.html", {"alerts": alerts})


@login_required
def billing_send_async(request):
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Acesso restrito.")
    task = send_overdue_billing_emails.delay()
    messages.info(request, f"Cobranca enviada para processamento assincrono. Task: {task.id}")
    from django.shortcuts import redirect
    return redirect("billing:panel")
