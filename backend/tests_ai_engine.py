import pytest
from tenants.models import Tenant
from inventory.models import Product, StockMovement
from ai_engine.engine import DataAnalyzer, media_movel, tendencia
from ai_engine.nlg import ReportGenerator
from ai_engine.chatbot import ChatBot
from ai_engine.knowledge_base import KnowledgeBase
from datetime import timedelta
from django.utils import timezone


@pytest.mark.django_db
class TestAIEngine:
    def test_media_movel(self):
        assert media_movel([1, 2, 3, 4, 5], 3) == 4.0

    def test_tendencia_crescendo(self):
        assert tendencia([1, 2, 3, 4, 5, 6, 7, 8]) == "crescendo"

    def test_tendencia_caindo(self):
        assert tendencia([8, 7, 6, 5, 4, 3, 2, 1]) == "caindo"

    def test_tendencia_estavel(self):
        assert tendencia([5, 5, 5, 5, 5, 5]) == "estavel"

    def test_data_analyzer(self, tenant):
        p = Product.objects.create(
            tenant=tenant, name="Acai", sku="A1", current_stock=20, min_stock=5
        )
        analyzer = DataAnalyzer(tenant)
        assert analyzer is not None
        insights = analyzer.insights_estoque()
        assert isinstance(insights, list)

    def test_report_generator_geral(self, tenant):
        Product.objects.create(tenant=tenant, name="Acai", sku="A1", current_stock=10)
        gen = ReportGenerator(tenant)
        report = gen.gerar_relatorio_geral()
        assert "Relatorio Geral" in report
        assert "Acai" in report or "produto" in report.lower()

    def test_report_generator_previsao(self, tenant):
        Product.objects.create(tenant=tenant, name="Banana", sku="B1", current_stock=10)
        gen = ReportGenerator(tenant)
        report = gen.gerar_previsao_demanda()
        assert "Previsao" in report

    def test_report_generator_financeiro(self, tenant):
        Product.objects.create(
            tenant=tenant, name="Granola", sku="G1",
            current_stock=10, cost_price=10, sale_price=20,
        )
        gen = ReportGenerator(tenant)
        report = gen.gerar_relatorio_financeiro()
        assert "Financeiro" in report

    def test_knowledge_base(self, tenant):
        Product.objects.create(tenant=tenant, name="Acai", sku="A1")
        kb = KnowledgeBase(tenant)
        assert kb.data["tenant"]["nome"] == tenant.name
        text = kb.to_text()
        assert "BASE DE CONHECIMENTO" in text

    def test_chatbot_responde(self, tenant):
        Product.objects.create(tenant=tenant, name="Acai", sku="A1", current_stock=10)
        bot = ChatBot(tenant)
        resp = bot.responder("estoque baixo")
        assert isinstance(resp, str)
        assert len(resp) > 0

    def test_chatbot_ajuda(self, tenant):
        bot = ChatBot(tenant)
        resp = bot.responder("ajuda")
        assert "estoque baixo" in resp.lower() or "ajuda" in resp.lower()

    def test_chatbot_saudacao(self, tenant):
        bot = ChatBot(tenant)
        resp = bot.responder("ola")
        assert "assistente" in resp.lower() or "ola" in resp.lower()

    def test_chatbot_produto_especifico(self, tenant):
        Product.objects.create(
            tenant=tenant, name="Acai Polpa", sku="ACAI001",
            current_stock=20, min_stock=5, cost_price=15, sale_price=25,
        )
        bot = ChatBot(tenant)
        resp = bot.responder("como esta o estoque de acai polpa?")
        assert "Acai Polpa" in resp or "acai polpa" in resp.lower()
