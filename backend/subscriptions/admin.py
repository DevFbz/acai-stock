from django.contrib import admin
from django.utils import timezone

from subscriptions.models import Subscription, Payment


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "tenant", "plan", "status", "billing_cycle", "amount",
        "current_period_end", "is_overdue",
    )
    list_filter = ("plan", "status", "billing_cycle")
    search_fields = ("tenant__name",)
    actions = ["block_unpaid", "activate_paid"]

    @admin.action(description="Bloquear não pagadores (overdue)")
    def block_unpaid(self, request, queryset):
        today = timezone.now().date()
        count = 0
        for sub in queryset.filter(status="overdue", current_period_end__lt=today):
            sub.tenant.status = "blocked"
            sub.tenant.is_active = False
            sub.tenant.save()
            count += 1
        self.message_user(request, f"{count} tenant(s) bloqueado(s).")

    @admin.action(description="Ativar assinaturas pagas")
    def activate_paid(self, request, queryset):
        updated = queryset.filter(status="paid").update(status="active")
        for sub in queryset.filter(status="paid"):
            sub.tenant.status = "active"
            sub.tenant.is_active = True
            sub.tenant.save()
        self.message_user(request, f"{updated} assinatura(s) ativada(s).")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("subscription", "amount", "status", "due_date", "paid_at", "method")
    list_filter = ("status", "method")
    search_fields = ("subscription__tenant__name", "reference")
    date_hierarchy = "due_date"
