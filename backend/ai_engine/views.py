from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from inventory.models import Product, StockMovement
from ai_engine.graph import generate_ai_report, chat_with_ai
from ai_engine.knowledge_base import KnowledgeBase
from reports.models import Report
from ai_engine.tasks import generate_scheduled_report

REPORT_TYPES = [
    ("ai_custom", "Relatorio Geral de Estoque"),
    ("sales_forecast", "Previsao de Demanda"),
    ("supplier_performance", "Desempenho de Fornecedores"),
    ("expiry_alert", "Alerta de Vencimento"),
    ("financial", "Relatorio Financeiro"),
]


@login_required
def ai_dashboard(request):
    tenant = request.user.tenant
    reports = Report.objects.filter(tenant=tenant)
    return render(request, "ai_engine/dashboard.html", {
        "reports": reports, "report_types": REPORT_TYPES,
    })


@login_required
@require_POST
def generate_report(request):
    tenant = request.user.tenant
    report_type = request.POST.get("report_type", "ai_custom")
    content = generate_ai_report(tenant, report_type)
    report = Report.objects.create(
        tenant=tenant,
        title=f"{dict(REPORT_TYPES).get(report_type, report_type)} - {tenant.name}",
        report_type=report_type,
        content=content,
        summary=content[:300],
        generated_by="ai_engine",
        metadata={"knowledge_base": True},
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
    import re

    tenant = request.user.tenant
    report = get_object_or_404(Report, pk=pk, tenant=tenant)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="relatorio_{report.pk}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=18, textColor=HexColor("#7c3aed"))
    body_style = ParagraphStyle("CustomBody", parent=styles["Normal"], fontSize=11, leading=16)

    story = []
    story.append(Paragraph(report.title, title_style))
    story.append(Spacer(1, 20))
    for line in report.content.split("\n"):
        clean = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        clean = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", clean)
        clean = re.sub(r"^### (.+)", r"<b>\1</b>", clean)
        clean = re.sub(r"^## (.+)", r"<b>\1</b>", clean)
        clean = re.sub(r"^# (.+)", r"<b>\1</b>", clean)
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
            answer = chat_with_ai(tenant, query)
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


@login_required
def knowledge_view(request):
    tenant = request.user.tenant
    kb = KnowledgeBase(tenant)
    return render(request, "ai_engine/knowledge.html", {
        "knowledge_text": kb.to_text(),
        "knowledge_json": kb.to_json(),
        "compiled_at": kb.compiled_at,
    })
