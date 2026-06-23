from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from tenants.models import Tenant


class User(AbstractUser):
    ROLE_CHOICES = [
        ("superadmin", "Super Admin"),
        ("admin", "Administrador"),
        ("manager", "Gerente"),
        ("staff", "Funcionário"),
    ]

    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
    ]

    role = models.CharField("Função", max_length=20, choices=ROLE_CHOICES, default="staff")
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="Tenant",
    )
    theme = models.CharField("Tema", max_length=10, choices=THEME_CHOICES, default="light")
    phone = models.CharField("Telefone", max_length=20, blank=True)
    is_tenant_owner = models.BooleanField("Dono do tenant", default=False)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    @property
    def is_superadmin(self):
        return self.role == "superadmin" or self.is_superuser

    @property
    def is_tenant_admin(self):
        return self.role in ("admin", "superadmin") or self.is_tenant_owner

    @property
    def display_name(self):
        return self.get_full_name() or self.username


def theme_context(request):
    theme = getattr(getattr(request, "user", None), "theme", settings.DEFAULT_THEME)
    return {"theme": theme}
