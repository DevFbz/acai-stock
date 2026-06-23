"""
Base de conhecimento do sistema.

Compila TODOS os dados de um tenant em um contexto estruturado que a IA usa
para gerar relatorios e responder perguntas. A IA "sabe" tudo sobre o estoque,
fornecedores, movimentacoes, pedidos e assinatura do tenant.
"""
import json
from datetime import datetime, timedelta
from django.utils import timezone

from inventory.models import Product, Category, Supplier, StockMovement, PurchaseOrder
from subscriptions.models import Subscription, Payment
from tenants.models import Tenant


class KnowledgeBase:
    """Compila todos os dados do tenant em uma base de conhecimento para a IA."""

    def __init__(self, tenant):
        self.tenant = tenant
        self.compiled_at = timezone.now()
        self.data = self._compile_all()

    def _compile_all(self):
        return {
            "tenant": self._tenant_info(),
            "resumo_estoque": self._stock_summary(),
            "produtos": self._products_detail(),
            "categorias": self._categories(),
            "fornecedores": self._suppliers(),
            "movimentacoes_recentes": self._recent_movements(),
            "movimentacoes_30_dias": self._movements_30_days(),
            "pedidos_compra": self._purchase_orders(),
            "assinatura": self._subscription(),
            "pagamentos": self._payments(),
            "alertas": self._alerts(),
            "estatisticas": self._statistics(),
        }

    def _tenant_info(self):
        t = self.tenant
        return {
            "nome": t.name,
            "plano": t.get_plan_display(),
            "status": t.get_status_display(),
            "criado_em": t.created_at.strftime("%d/%m/%Y"),
        }

    def _stock_summary(self):
        products = Product.objects.filter(tenant=self.tenant, is_active=True)
        total_value = sum(float(p.current_stock) * float(p.cost_price) for p in products)
        low_stock = [p.name for p in products if p.is_low_stock]
        expired = [p.name for p in products if p.is_expired]
        expiring = [
            {"nome": p.name, "dias": p.days_to_expiry}
            for p in products
            if p.days_to_expiry is not None and 0 < p.days_to_expiry <= 7
        ]
        return {
            "total_produtos": products.count(),
            "valor_total_estoque": round(total_value, 2),
            "produtos_estoque_baixo": low_stock,
            "produtos_vencidos": expired,
            "produtos_vencendo_7_dias": expiring,
        }

    def _products_detail(self):
        products = Product.objects.filter(tenant=self.tenant, is_active=True)
        return [
            {
                "nome": p.name,
                "sku": p.sku,
                "categoria": p.category.name if p.category else None,
                "fornecedor": p.supplier.name if p.supplier else None,
                "unidade": p.get_unit_display(),
                "estoque_atual": float(p.current_stock),
                "estoque_minimo": float(p.min_stock),
                "estoque_maximo": float(p.max_stock),
                "preco_custo": float(p.cost_price),
                "preco_venda": float(p.sale_price),
                "validade": p.expiry_date.isoformat() if p.expiry_date else None,
                "dias_para_vencer": p.days_to_expiry,
                "estoque_baixo": p.is_low_stock,
                "vencido": p.is_expired,
                "valor_total_estoque": round(float(p.current_stock) * float(p.cost_price), 2),
            }
            for p in products
        ]

    def _categories(self):
        cats = Category.objects.filter(tenant=self.tenant)
        return [
            {
                "nome": c.name,
                "quantidade_produtos": c.products.filter(is_active=True).count(),
            }
            for c in cats
        ]

    def _suppliers(self):
        sups = Supplier.objects.filter(tenant=self.tenant)
        return [
            {
                "nome": s.name,
                "contato": s.contact_person,
                "telefone": s.phone,
                "email": s.email,
                "ativo": s.is_active,
                "produtos_fornecidos": s.products.filter(is_active=True).count(),
            }
            for s in sups
        ]

    def _recent_movements(self, limit=20):
        movs = StockMovement.objects.filter(product__tenant=self.tenant).order_by("-created_at")[:limit]
        return [
            {
                "produto": m.product.name,
                "tipo": m.get_movement_type_display(),
                "quantidade": float(m.quantity),
                "motivo": m.reason,
                "data": m.created_at.strftime("%d/%m/%Y %H:%M"),
            }
            for m in movs
        ]

    def _movements_30_days(self):
        start = timezone.now() - timedelta(days=30)
        movs = StockMovement.objects.filter(
            product__tenant=self.tenant, created_at__gte=start
        )
        by_type = {"entrada": 0, "saida": 0, "ajuste": 0, "perda": 0}
        by_product = {}
        for m in movs:
            qtd = float(m.quantity)
            if m.movement_type == "in":
                by_type["entrada"] += qtd
            elif m.movement_type == "out":
                by_type["saida"] += qtd
            elif m.movement_type == "waste":
                by_type["perda"] += qtd
            else:
                by_type["ajuste"] += qtd
            name = m.product.name
            if name not in by_product:
                by_product[name] = {"entrada": 0, "saida": 0, "perda": 0}
            if m.movement_type == "in":
                by_product[name]["entrada"] += qtd
            elif m.movement_type == "out":
                by_product[name]["saida"] += qtd
            elif m.movement_type == "waste":
                by_product[name]["perda"] += qtd
        return {
            "por_tipo": by_type,
            "por_produto": by_product,
            "total_movimentacoes": movs.count(),
        }

    def _purchase_orders(self):
        orders = PurchaseOrder.objects.filter(tenant=self.tenant).order_by("-created_at")[:10]
        return [
            {
                "numero": f"PO-{o.id:06d}",
                "fornecedor": o.supplier.name if o.supplier else None,
                "status": o.get_status_display(),
                "total": float(o.total),
                "previsao": o.expected_date.isoformat() if o.expected_date else None,
                "itens": [
                    {
                        "produto": i.product.name,
                        "quantidade": float(i.quantity),
                        "custo_unitario": float(i.unit_cost),
                        "subtotal": float(i.subtotal),
                    }
                    for i in o.items.all()
                ],
            }
            for o in orders
        ]

    def _subscription(self):
        try:
            sub = self.tenant.subscription
            return {
                "plano": sub.get_plan_display(),
                "status": sub.get_status_display(),
                "ciclo": sub.get_billing_cycle_display(),
                "valor": float(sub.amount),
                "periodo_inicio": sub.current_period_start.isoformat(),
                "periodo_fim": sub.current_period_end.isoformat() if sub.current_period_end else None,
                "em_atraso": sub.is_overdue,
            }
        except Subscription.DoesNotExist:
            return None

    def _payments(self):
        try:
            sub = self.tenant.subscription
            payments = sub.payments.all().order_by("-due_date")[:10]
            return [
                {
                    "valor": float(p.amount),
                    "status": p.get_status_display(),
                    "vencimento": p.due_date.isoformat(),
                    "pago_em": p.paid_at.strftime("%d/%m/%Y") if p.paid_at else None,
                    "metodo": p.method,
                }
                for p in payments
            ]
        except Subscription.DoesNotExist:
            return []

    def _alerts(self):
        alerts = []
        products = Product.objects.filter(tenant=self.tenant, is_active=True)
        for p in products:
            if p.is_expired:
                alerts.append({"tipo": "vencido", "produto": p.name, "severidade": "alta"})
            elif p.is_low_stock:
                alerts.append({"tipo": "estoque_baixo", "produto": p.name, "severidade": "media"})
            elif p.days_to_expiry is not None and p.days_to_expiry <= 7:
                alerts.append({
                    "tipo": "vencimento_proximo",
                    "produto": p.name,
                    "dias": p.days_to_expiry,
                    "severidade": "media",
                })
        return alerts

    def _statistics(self):
        products = Product.objects.filter(tenant=self.tenant, is_active=True)
        total_cost = sum(float(p.current_stock) * float(p.cost_price) for p in products)
        total_sale = sum(float(p.current_stock) * float(p.sale_price) for p in products)
        potential_profit = total_sale - total_cost
        return {
            "valor_custo_total": round(total_cost, 2),
            "valor_venda_total": round(total_sale, 2),
            "lucro_potencial": round(potential_profit, 2),
            "ticket_medio_produto": round(total_cost / products.count(), 2) if products.count() > 0 else 0,
            "margem_media": round((potential_profit / total_cost * 100), 2) if total_cost > 0 else 0,
        }

    def to_text(self):
        """Converte a base de conhecimento em texto estruturado para a IA."""
        d = self.data
        lines = []
        lines.append(f"=== BASE DE CONHECIMENTO: {d['tenant']['nome']} ===")
        lines.append(f"Compilado em: {self.compiled_at.strftime('%d/%m/%Y %H:%M')}")
        lines.append(f"Plano: {d['tenant']['plano']} | Status: {d['tenant']['status']}")
        lines.append("")

        lines.append("--- RESUMO DE ESTOQUE ---")
        s = d["resumo_estoque"]
        lines.append(f"Total de produtos: {s['total_produtos']}")
        lines.append(f"Valor total em estoque: R$ {s['valor_total_estoque']}")
        if s["produtos_estoque_baixo"]:
            lines.append(f"Produtos com estoque baixo: {', '.join(s['produtos_estoque_baixo'])}")
        if s["produtos_vencidos"]:
            lines.append(f"Produtos vencidos: {', '.join(s['produtos_vencidos'])}")
        if s["produtos_vencendo_7_dias"]:
            for v in s["produtos_vencendo_7_dias"]:
                lines.append(f"  - {v['nome']}: vence em {v['dias']} dias")
        lines.append("")

        lines.append("--- PRODUTOS DETALHADOS ---")
        for p in d["produtos"]:
            status = []
            if p["estoque_baixo"]:
                status.append("ESTOQUE BAIXO")
            if p["vencido"]:
                status.append("VENCIDO")
            if p["dias_para_vencer"] is not None and 0 < p["dias_para_vencer"] <= 7:
                status.append(f"VENCE EM {p['dias_para_vencer']} DIAS")
            status_str = f" [{', '.join(status)}]" if status else ""
            lines.append(
                f"- {p['nome']} (SKU: {p['sku']}) | Cat: {p['categoria']} | "
                f"Estoque: {p['estoque_atual']}/{p['estoque_minimo']} {p['unidade']} | "
                f"Custo: R${p['preco_custo']} | Venda: R${p['preco_venda']} | "
                f"Validade: {p['validade']}{status_str}"
            )
        lines.append("")

        lines.append("--- MOVIMENTACOES (ULTIMOS 30 DIAS) ---")
        m = d["movimentacoes_30_dias"]
        lines.append(f"Total: {m['total_movimentacoes']}")
        lines.append(f"Entradas: {m['por_tipo']['entrada']} | Saidas: {m['por_tipo']['saida']} | Perdas: {m['por_tipo']['perda']}")
        for prod, vals in m["por_produto"].items():
            lines.append(f"  - {prod}: Entrada {vals['entrada']}, Saida {vals['saida']}, Perda {vals['perda']}")
        lines.append("")

        lines.append("--- FORNECEDORES ---")
        for s in d["fornecedores"]:
            lines.append(f"- {s['nome']} | Contato: {s['contato']} | Tel: {s['telefone']} | Produtos: {s['produtos_fornecidos']} | {'Ativo' if s['ativo'] else 'Inativo'}")
        lines.append("")

        lines.append("--- PEDIDOS DE COMPRA RECENTES ---")
        for o in d["pedidos_compra"]:
            lines.append(f"- {o['numero']} | {o['fornecedor']} | {o['status']} | R$ {o['total']} | Previsao: {o['previsao']}")
        lines.append("")

        lines.append("--- ESTATISTICAS FINANCEIRAS ---")
        st = d["estatisticas"]
        lines.append(f"Valor de custo total: R$ {st['valor_custo_total']}")
        lines.append(f"Valor de venda total: R$ {st['valor_venda_total']}")
        lines.append(f"Lucro potencial: R$ {st['lucro_potencial']}")
        lines.append(f"Margem media: {st['margem_media']}%")
        lines.append("")

        lines.append("--- ALERTAS ATIVOS ---")
        for a in d["alertas"]:
            lines.append(f"- [{a['severidade'].upper()}] {a['tipo']}: {a.get('produto', '')} {a.get('dias', '')}")

        return "\n".join(lines)

    def to_json(self):
        return json.dumps(self.data, ensure_ascii=False, indent=2, default=str)
