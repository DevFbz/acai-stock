from django.contrib import admin

from tenants.models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "plan", "status", "is_active", "created_at")
    list_filter = ("plan", "status", "is_active")
    search_fields = ("name", "slug")
    actions = ["block_access", "suspend_access", "reactivate_access"]

    @admin.action(description="Bloquear acesso (não pagou)")
    def block_access(self, request, queryset):
        updated = queryset.update(status="blocked", is_active=False)
        self.message_user(request, f"{updated} tenant(s) bloqueado(s).")

    @admin.action(description="Suspender acesso")
    def suspend_access(self, request, queryset):
        updated = queryset.update(status="suspended")
        self.message_user(request, f"{updated} tenant(s) suspenso(s).")

    @admin.action(description="Reativar acesso")
    def reactivate_access(self, request, queryset):
        updated = queryset.update(status="active", is_active=True)
        self.message_user(request, f"{updated} tenant(s) reativado(s).")
