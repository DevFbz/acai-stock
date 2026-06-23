from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from accounts.forms import LoginForm
from accounts.models import User


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.tenant and not user.tenant.is_accessible and not user.is_superuser:
            return redirect("accounts:blocked")
        login(self.request, user)
        return redirect(self.get_success_url())


def blocked_view(request):
    return render(request, "accounts/blocked.html", {})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
@require_POST
def toggle_theme(request):
    user = request.user
    user.theme = "dark" if user.theme == "light" else "light"
    user.save(update_fields=["theme"])
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))
