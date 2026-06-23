from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "tenant", "is_tenant_owner", "is_active")
    list_filter = ("role", "is_active", "is_tenant_owner")
    search_fields = ("username", "email", "first_name", "last_name")
    list_editable = ("role",)
