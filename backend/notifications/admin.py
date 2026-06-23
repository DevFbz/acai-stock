from django.contrib import admin

from notifications.models import Notification, NotificationSetting


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "notification_type", "severity", "is_read", "created_at")
    list_filter = ("notification_type", "severity", "is_read")
    search_fields = ("title", "message", "tenant__name")


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ("tenant", "email_enabled", "low_stock_alerts", "expiry_alerts", "weekly_report")
