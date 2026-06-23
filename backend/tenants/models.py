from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("basic", "Básico"),
        ("pro", "Profissional"),
        ("enterprise", "Empresarial"),
    ]

    STATUS_CHOICES = [
        ("active", "Ativo"),
        ("suspended", "Suspenso"),
        ("blocked", "Bloqueado"),
        ("canceled", "Cancelado"),
    ]

    name = models.CharField("Nome", max_length=255)
    slug = models.SlugField("Identificador", unique=True, blank=True)
    plan = models.CharField("Plano", max_length=20, choices=PLAN_CHOICES, default="free")
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="active")
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_accessible(self):
        return self.status in ("active",) and self.is_active
