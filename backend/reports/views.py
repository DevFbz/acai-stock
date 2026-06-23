from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from reports.models import Report


@login_required
def report_list(request):
    tenant = request.user.tenant
    reports = Report.objects.filter(tenant=tenant)
    return render(request, "reports/report_list.html", {"reports": reports})
