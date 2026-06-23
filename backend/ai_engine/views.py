from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from inventory.models import Product, StockMovement
from ai_engine.graph import generate_ai_report, chat_with_ai
from reports.models import Report
from ai_engine.tasks import generate_scheduled_report

REPORT_TYPES = [
    ("ai_custom", "Relatorio Geral de Estoque"),
    ("sales_forecast", "Previsao de Demanda"),
    ("supplier_performance", "Desempenho de Fornecedores"),
    ("expiry_alert", "Alerta de Vencimento"),
]


def _gather_tenant_data(tenant):
    products = Product.objects.filter(tenant=tenant, is_active=True)
    stock_data = [
        {
            "name": p.name, "current": float(p.current_stock),
            "min": float(p.min_stock), "unit": p.unit,
            "expiry": p.expiry_date.isoformat() if p.expiry_date else None,
            "low": p.is_low_stock, "expired": p.is_expired,
            "days_to_expiry": p.days_to_expiry,
            "cost": float(p.cost_price), "sale": float(p.sale_price),
            "supplier": p.supplier.name if p.supplier else None,
            "category": p.category.name if p.category else None,
        }
        for p in products
    ]
    movements = list(
        StockMovement.objects.filter(product__tenant=tenant)[:50].values(
            "product__name", "movement_type", "quantity", "reason", "created_at"
        )
    )
    return stock_data, movements


@login_required
def ai_dashboard(request):
    tenant = request.user.tenant
    reports = Report.objects.filter(tenant=tenant, report_type__startswith="ai").union(
        Report.objects.filter(tenant=tenant, report_type__in=["sales_forecast", "supplier_performance", "expiry_alert"])
    ) if hasattr(Report.objects, "union") else Report.objects.filter(tenant=tenant)
    return render(request, "ai_engine/dashboard.html", {
        "reports": reports, "report_types": REPORT_TYPES,
    })


@login_required
@require_POST
def generate_report(request):
    tenant = request.user.tenant
    report_type = request.POST.get("report_type", "ai_custom")
    stock_data, movements = _gather_tenant_data(tenant)
    content = generate_ai_report(tenant.name, stock_data, movements, report_type)
    report = Report.objects.create(
        tenant=tenant,
        title=f"{dict(REPORT_TYPES).get(report_type, report_type)} - {tenant.name}",
        report_type=report_type,
        content=content,
        summary=content[:300],
        generated_by="ai_engine",
    )
    return redirect("ai_engine:report_detail", pk=report.pk)


@login_required
def report_detail(request, pk):
    tenant = request.user.tenant
    report = get_object_or_404(Report, pk=pk, tenant=tenant)
    return render(request, "ai_engine/report_detail.html", {"report": report})


@login_required
def report_pdf(request, pk):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.colors import HexColor
    import html

    tenant = request.user.tenant
    report = get_object_or_404(Report, pk=pk, tenant=tenant)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="relatorio_{report.pk}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=18, textColor=HexColor("#7c3aed"))
    body_style = ParagraphStyle("CustomBody", parent=styles["Normal"], fontSize=11, leading=16)

    story = []
    story.append(Paragraph(html.escape(report.title), title_style))
    story.append(Spacer(1, 20))
    for line in report.content.split("\n"):
        clean = html.escape(line).replace("**", "<b>").replace("*", "<b>")
        if clean.strip():
            story.append(Paragraph(clean, body_style))
        else:
            story.append(Spacer(1, 8))
    doc.build(story)
    return response


@login_required
@require_POST
def generate_async(request):
    tenant = request.user.tenant
    report_type = request.POST.get("report_type", "ai_custom")
    task = generate_scheduled_report.delay(tenant.pk, report_type)
    return render(request, "ai_engine/task_started.html", {
        "task_id": task.id, "report_type": report_type,
    })


@login_required
def chat_view(request):
    tenant = request.user.tenant
    conversation = request.session.get("chat_history", [])
    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        if query:
            stock_data, movements = _gather_tenant_data(tenant)
            context = {"stock": stock_data[:30], "movements": movements[:20]}
            answer = chat_with_ai(tenant.name, context, query)
            conversation.append({"role": "user", "text": query})
            conversation.append({"role": "ai", "text": answer})
            request.session["chat_history"] = conversation[-20:]
            request.session.modified = True
            return redirect("ai_engine:chat")
    return render(request, "ai_engine/chat.html", {"conversation": conversation})


@login_required
def chat_clear(request):
    request.session.pop("chat_history", None)
    return redirect("ai_engine:chat")
