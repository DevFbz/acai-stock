from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("blocked/", views.blocked_view, name="blocked"),
    path("toggle-theme/", views.toggle_theme, name="toggle_theme"),
]
