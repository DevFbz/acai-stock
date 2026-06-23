from django.urls import path

from ai_engine import views

app_name = "ai_engine"

urlpatterns = [
    path("", views.ai_dashboard, name="dashboard"),
    path("generate/", views.generate_report, name="generate_report"),
    path("generate-async/", views.generate_async, name="generate_async"),
    path("report/<int:pk>/", views.report_detail, name="report_detail"),
    path("report/<int:pk>/pdf/", views.report_pdf, name="report_pdf"),
    path("chat/", views.chat_view, name="chat"),
    path("chat/clear/", views.chat_clear, name="chat_clear"),
]
