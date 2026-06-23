"""
Motor de IA Interno do Acai Stock.

Nao depende de nenhuma API externa (OpenAI, Claude, etc).
Processa todos os dados do sistema e gera:
- Relatorios em linguagem natural com insights reais
- Previsoes de demanda baseadas em medias moveis e tendencias
- Respostas a perguntas via analise de dados + pattern matching
- Deteccao de anomalias e padroes

Tudo computado localmente com algoritmos estatisticos.
"""
import math
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

from django.utils import timezone

from inventory.models import Product, Category, Supplier, StockMovement, PurchaseOrder
from subscriptions.models import Subscription
from tenants.models import Tenant


# ==================== ESTATISTICA ====================

def media_movel(valores, janela=7):
    if len(valores) < janela:
        janela = len(valores)
    if janela == 0:
        return 0
    return sum(valores[-janela:]) / janela


def tendencia(valores):
    """Retorna 'crescendo', 'estavel' ou 'caindo' baseado na inclinacao."""
    if len(valores) < 2:
        return "estavel"
    metade = len(valores) // 2
    prime = sum(valores[:metade]) / max(metade, 1)
    segund = sum(valores[metade:]) / max(len(valores) - metade, 1)
    if prime == 0:
        return "crescendo" if segund > 0 else "estavel"
    variacao = ((segund - prime) / prime) * 100
    if variacao > 10:
        return "crescendo"
    elif variacao < -10:
        return "caindo"
    return "estavel"


def desvio_padrao(valores):
    if len(valores) < 2:
        return 0
    media = sum(valores) / len(valores)
    variancia = sum((x - media) ** 2 for x in valores) / (len(valores) - 1)
    return math.sqrt(variancia)


def projetar_consumo(valores_diarios, dias_futuros=7):
    """Projeta consumo futuro baseado em media movel + tendencia."""
    if not valores_diarios:
        return 0
    mm = media_movel(valores_diarios, 7)
    tend = tendencia(valores_diarios)
    if tend == "crescendo":
        fator = 1.1
    elif tend == "caindo":
        fator = 0.9
    else:
        fator = 1.0
    return mm * dias_futuros * fator


def dias_ate_esgotar(estoque_atual, consumo_diario_medio):
    if consumo_diario_medio <= 0:
        return None
    return int(estoque_atual / consumo_diario_medio)


# ==================== ANALISE DE DADOS ====================

class DataAnalyzer:
    """Analisa todos os dados do tenant e extrai insights."""

    def __init__(self, tenant):
        self.tenant = tenant
        self.products = list(Product.objects.filter(tenant=tenant, is_active=True))
        self.movements = list(
            StockMovement.objects.filter(
                product__tenant=tenant,
                created_at__gte=timezone.now() - timedelta(days=30),
            ).order_by("created_at")
        )
        self._consumo_por_produto = self._calcular_consumo_diario()

    def _calcular_consumo_diario(self):
        """Calcula consumo diario (saidas) por produto nos ultimos 30 dias."""
        consumo = defaultdict(lambda: defaultdict(float))
        for m in self.movements:
            if m.movement_type == "out":
                dia = m.created_at.date()
                consumo[m.product_id][dia] += float(m.quantity)
        return consumo

    def _serie_temporal(self, product_id):
        """Retorna lista de consumo diario dos ultimos 30 dias para um produto."""
        consumo = self._consumo_por_produto.get(product_id, {})
        hoje = timezone.now().date()
        serie = []
        for i in range(30, 0, -1):
            dia = hoje - timedelta(days=i)
            serie.append(consumo.get(dia, 0))
        return serie

    def insights_estoque(self):
        insights = []
        for p in self.products:
            serie = self._serie_temporal(p.id)
            consumo_medio = media_movel(serie, 7)
            dias_restantes = dias_ate_esgotar(float(p.current_stock), consumo_medio)

            if p.is_expired:
                insights.append({
                    "produto": p.name,
                    "tipo": "vencido",
                    "severidade": "alta",
                    "descricao": f"{p.name} esta VENCIDO. Necessario descarte ou acao imediata.",
                    "acao": "Remover do estoque e registrar perda.",
                })
            elif p.is_low_stock:
                insights.append({
                    "produto": p.name,
                    "tipo": "estoque_baixo",
                    "severidade": "alta",
                    "descricao": f"{p.name} com estoque {p.current_stock} (minimo: {p.min_stock}).",
                    "acao": f"Repor imediatamente. Consumo medio: {consumo_medio:.1f}/dia.",
                })
            elif p.days_to_expiry is not None and 0 < p.days_to_expiry <= 7:
                insights.append({
                    "produto": p.name,
                    "tipo": "vencimento_proximo",
                    "severidade": "media",
                    "descricao": f"{p.name} vence em {p.days_to_expiry} dias.",
                    "acao": "Priorizar uso ou criar promocao para evitar perda.",
                })
            elif dias_restantes is not None and dias_restantes <= 3:
                insights.append({
                    "produto": p.name,
                    "tipo": "reposicao_urgente",
                    "severidade": "alta",
                    "descricao": f"{p.name} esgotara em ~{dias_restantes} dias.",
                    "acao": f"Fazer pedido de compra urgente. Consumo: {consumo_medio:.1f}/dia.",
                })
        return insights

    def previsao_demanda(self, dias=7):
        previsoes = []
        for p in self.products:
            serie = self._serie_temporal(p.id)
            consumo_medio = media_movel(serie, 7)
            proj = projetar_consumo(serie, dias)
            tend = tendencia(serie)
            dias_restantes = dias_ate_esgotar(float(p.current_stock), consumo_medio)
            precisa_repor = dias_restantes is not None and dias_restantes <= dias

            previsoes.append({
                "produto": p.name,
                "sku": p.sku,
                "estoque_atual": float(p.current_stock),
                "consumo_medio_diario": round(consumo_medio, 2),
                "previsao_consumo": round(proj, 2),
                "tendencia": tend,
                "dias_ate_esgotar": dias_restantes,
                "precisa_reposicao": precisa_repor,
                "sugestao_compra": round(proj - float(p.current_stock), 2) if proj > float(p.current_stock) else 0,
            })
        previsoes.sort(key=lambda x: x["precisa_reposicao"], reverse=True)
        return previsoes

    def analise_financeira(self):
        total_custo = sum(float(p.current_stock) * float(p.cost_price) for p in self.products)
        total_venda = sum(float(p.current_stock) * float(p.sale_price) for p in self.products)
        lucro = total_venda - total_custo
        margem = (lucro / total_custo * 100) if total_custo > 0 else 0

        produtos_parados = []
        produtos_baixa_margem = []
        for p in self.products:
            serie = self._serie_temporal(p.id)
            consumo_total = sum(serie)
            if consumo_total == 0:
                valor_preso = float(p.current_stock) * float(p.cost_price)
                if valor_preso > 0:
                    produtos_parados.append({
                        "produto": p.name,
                        "valor_preso": round(valor_preso, 2),
                        "estoque": float(p.current_stock),
                    })
            margem_p = ((float(p.sale_price) - float(p.cost_price)) / float(p.cost_price) * 100) if float(p.cost_price) > 0 else 0
            if margem_p < 30 and float(p.cost_price) > 0:
                produtos_baixa_margem.append({
                    "produto": p.name,
                    "margem": round(margem_p, 1),
                    "custo": float(p.cost_price),
                    "venda": float(p.sale_price),
                })

        return {
            "valor_custo_total": round(total_custo, 2),
            "valor_venda_total": round(total_venda, 2),
            "lucro_potencial": round(lucro, 2),
            "margem_media": round(margem, 1),
            "produtos_parados": sorted(produtos_parados, key=lambda x: x["valor_preso"], reverse=True)[:5],
            "produtos_baixa_margem": produtos_baixa_margem,
            "capital_preso": round(sum(pp["valor_preso"] for pp in produtos_parados), 2),
        }

    def analise_fornecedores(self):
        fornecedores = {}
        for p in self.products:
            if p.supplier_id:
                sid = p.supplier_id
                if sid not in fornecedores:
                    sup = p.supplier
                    fornecedores[sid] = {
                        "nome": sup.name,
                        "contato": sup.contact_person,
                        "telefone": sup.phone,
                        "produtos": 0,
                        "valor_estoque": 0,
                    }
                fornecedores[sid]["produtos"] += 1
                fornecedores[sid]["valor_estoque"] += float(p.current_stock) * float(p.cost_price)

        lista = sorted(fornecedores.values(), key=lambda x: x["valor_estoque"], reverse=True)
        for f in lista:
            f["valor_estoque"] = round(f["valor_estoque"], 2)
        return lista

    def top_produtos_consumo(self, limit=10):
        consumos = []
        for p in self.products:
            serie = self._serie_temporal(p.id)
            total = sum(serie)
            if total > 0:
                consumos.append({
                    "produto": p.name,
                    "consumo_30d": round(total, 2),
                    "media_diaria": round(media_movel(serie, 7), 2),
                })
        consumos.sort(key=lambda x: x["consumo_30d"], reverse=True)
        return consumos[:limit]

    def resumo_movimentacoes(self):
        por_tipo = {"entrada": 0, "saida": 0, "perda": 0, "ajuste": 0}
        for m in self.movements:
            q = float(m.quantity)
            if m.movement_type == "in":
                por_tipo["entrada"] += q
            elif m.movement_type == "out":
                por_tipo["saida"] += q
            elif m.movement_type == "waste":
                por_tipo["perda"] += q
            else:
                por_tipo["ajuste"] += q
        return {
            "total": len(self.movements),
            **por_tipo,
            "taxa_perda": round((por_tipo["perda"] / max(por_tipo["saida"] + por_tipo["perda"], 1)) * 100, 1),
        }
