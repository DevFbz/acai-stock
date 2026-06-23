from django.contrib import admin

from billing.models import BillingAlert
from billing.services import check_and_notify_overdue


@admin.register(BillingAlert)
class BillingAlertAdmin(admin.ModelAdmin):
    list_display = ("tenant", "subject", "status", "days_overdue", "amount_due", "sent_at", "created_at")
    list_filter = ("status", "days_overdue")
    search_fields = ("tenant__name", "subject")
    actions = ["run_billing_check"]

    @admin.action(description="Verificar e enviar cobrancas agora")
    def run_billing_check(self, request, queryset):
        results = check_and_notify_overdue()
        self.message_user(request, f"{len(results)} email(s) de cobranca processado(s).")
