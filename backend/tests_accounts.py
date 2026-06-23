import pytest
from django.test import Client
from tenants.models import Tenant
from accounts.models import User


@pytest.mark.django_db
class TestTenantModel:
    def test_tenant_creation(self):
        t = Tenant.objects.create(name="Acai do Joao")
        assert t.slug == "acai-do-joao"
        assert t.status == "active"
        assert t.is_accessible is True

    def test_tenant_blocked(self):
        t = Tenant.objects.create(name="Bloqueado", status="blocked", is_active=False)
        assert t.is_accessible is False

    def test_tenant_str(self):
        t = Tenant.objects.create(name="Test Acai")
        assert str(t) == "Test Acai"


@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self, tenant):
        u = User.objects.create_user(
            username="joao", password="123456", tenant=tenant, role="admin"
        )
        assert u.is_tenant_admin is True
        assert u.is_superadmin is False
        assert u.display_name == "joao"

    def test_superadmin(self):
        u = User.objects.create_superuser(username="root", password="123456")
        assert u.is_superadmin is True
        assert u.role == "superadmin" or u.is_superuser


@pytest.mark.django_db
class TestLoginView:
    def test_login_page_loads(self):
        c = Client()
        resp = c.get("/accounts/login/")
        assert resp.status_code == 200

    def test_login_success(self, tenant):
        User.objects.create_user(username="joao", password="123456", tenant=tenant)
        c = Client()
        resp = c.post("/accounts/login/", {"username": "joao", "password": "123456"})
        assert resp.status_code == 302

    def test_blocked_user_redirect(self, tenant):
        tenant.status = "blocked"
        tenant.is_active = False
        tenant.save()
        User.objects.create_user(username="joao", password="123456", tenant=tenant)
        c = Client()
        c.login(username="joao", password="123456")
        resp = c.get("/estoque/")
        assert resp.status_code == 302
        assert "/blocked/" in resp.url
