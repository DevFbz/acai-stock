from django.urls import path

from billing import views

app_name = "billing"

urlpatterns = [
    path("", views.billing_panel, name="panel"),
    path("send-async/", views.billing_send_async, name="send_async"),
]
