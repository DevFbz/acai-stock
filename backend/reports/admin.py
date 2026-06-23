from django.contrib import admin

from reports.models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "report_type", "tenant", "generated_by", "created_at")
    list_filter = ("report_type", "generated_by")
    search_fields = ("title", "summary")
