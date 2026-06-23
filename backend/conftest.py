import pytest
from django.test import RequestFactory
from tenants.models import Tenant
from accounts.models import User


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(name="Acai Teste", plan="pro", status="active")


@pytest.fixture
def user(tenant, db):
    return User.objects.create_user(
        username="testuser",
        password="Test123!",
        email="test@test.com",
        tenant=tenant,
        role="admin",
    )


@pytest.fixture
def factory():
    return RequestFactory()
