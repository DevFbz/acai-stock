from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from notifications.models import Notification, NotificationSetting


@login_required
def notification_list(request):
    tenant = request.user.tenant
    notifs = Notification.objects.filter(tenant=tenant)[:50]
    unread = Notification.objects.filter(tenant=tenant, is_read=False).count()
    return render(request, "notifications/list.html", {"notifications": notifs, "unread_count": unread})


@login_required
def notification_unread_count(request):
    tenant = request.user.tenant
    count = Notification.objects.filter(tenant=tenant, is_read=False).count()
    return JsonResponse({"count": count})


@login_required
@require_POST
def mark_read(request, pk):
    tenant = request.user.tenant
    notif = Notification.objects.get(pk=pk, tenant=tenant)
    notif.is_read = True
    notif.save(update_fields=["is_read"])
    return JsonResponse({"ok": True})


@login_required
@require_POST
def mark_all_read(request):
    tenant = request.user.tenant
    Notification.objects.filter(tenant=tenant, is_read=False).update(is_read=True)
    return JsonResponse({"ok": True})


@login_required
def settings_view(request):
    tenant = request.user.tenant
    ns, _ = NotificationSetting.objects.get_or_create(tenant=tenant)
    if request.method == "POST":
        ns.email_enabled = "email_enabled" in request.POST
        ns.low_stock_alerts = "low_stock_alerts" in request.POST
        ns.expiry_alerts = "expiry_alerts" in request.POST
        ns.daily_summary = "daily_summary" in request.POST
        ns.weekly_report = "weekly_report" in request.POST
        ns.save()
        return redirect("notifications:settings")
    return render(request, "notifications/settings.html", {"settings": ns})
