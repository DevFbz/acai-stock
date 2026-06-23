from django.urls import path

from ai_engine import views

app_name = "ai_engine"

urlpatterns = [
    path("", views.ai_dashboard, name="dashboard"),
    path("generate/", views.generate_report, name="generate_report"),
]
