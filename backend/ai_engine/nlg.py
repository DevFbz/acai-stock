"""
Gerador de Relatorios em Linguagem Natural.

Transforma dados analisados em relatorios textuais profissionais,
sem depender de nenhuma API externa de IA.
"""
from datetime import datetime

from ai_engine.engine import DataAnalyzer
from ai_engine.knowledge_base import KnowledgeBase


class ReportGenerator:
    """Gera relatorios em texto a partir da analise dos dados do sistema."""

    def __init__(self, tenant):
        self.tenant = tenant
        self.analyzer = DataAnalyzer(tenant)
        self.kb = KnowledgeBase(tenant)
        self.data = self.kb.data

    def _header(self, titulo):
        data = datetime.now().strftime("%d/%m/%Y as %H:%M")
        return f"# {titulo} - {self.tenant.name}\nGerado em: {data}\n"

    def gerar_relatorio_geral(self):
        r = []
        r.append(self._header("Relatorio Geral de Estoque"))
        s = self.data["resumo_estoque"]
        st = self.data["estatisticas"]
        mov = self.analyzer.resumo_movimentacoes()

        r.append("\n## Visao Geral\n")
        r.append(f"- Total de produtos ativos: {s['total_produtos']}")
        r.append(f"- Valor total em estoque: R$ {s['valor_total_estoque']:.2f}")
        r.append(f"- Lucro potencial: R$ {st['lucro_potencial']:.2f}")
        r.append(f"- Margem media: {st['margem_media']}%")
        r.append(f"- Movimentacoes (30 dias): {mov['total']} | Entradas: {mov['entrada']:.1f} | Saidas: {mov['saida']:.1f} | Perdas: {mov['perda']:.1f}")
        r.append(f"- Taxa de perda: {mov['taxa_perda']}%")

        r.append("\n## Produtos Criticos\n")
        insights = self.analyzer.insights_estoque()
        if insights:
            for ins in insights:
                emoji = {"alta": "🔴", "media": "🟡"}.get(ins["severidade"], "⚪")
                r.append(f"{emoji} [{ins['severidade'].upper()}] {ins['descricao']}")
                r.append(f"   → Acao: {ins['acao']}")
        else:
            r.append("✅ Nenhum alerta critico. Estoque em condicoes normais.")

        r.append("\n## Top 5 Produtos por Consumo (30 dias)\n")
        top = self.analyzer.top_produtos_consumo(5)
        if top:
            for i, t in enumerate(top, 1):
                r.append(f"{i}. {t['produto']} - Consumo: {t['consumo_30d']} (Media: {t['media_diaria']}/dia)")
        else:
            r.append("Sem dados de consumo suficientes.")

        r.append("\n## Produtos Parados (sem movimentacao)\n")
        fin = self.analyzer.analise_financeira()
        if fin["produtos_parados"]:
            for p in fin["produtos_parados"]:
                r.append(f"- {p['produto']} | Estoque: {p['estoque']} | Valor preso: R$ {p['valor_preso']:.2f}")
        else:
            r.append("✅ Todos os produtos tiveram movimentacao nos ultimos 30 dias.")

        r.append(self._gerar_recomendacoes(insights, fin))
        return "\n".join(r)

    def gerar_previsao_demanda(self):
        r = []
        r.append(self._header("Previsao de Demanda (7 dias)"))
        previsoes = self.analyzer.previsao_demanda(7)

        r.append("\n## Tabela de Previsao\n")
        r.append(f"{'Produto':<30} {'Estoque':>10} {'Cons/Dia':>10} {'Prev 7d':>10} {'Tendencia':>12} {'Repor?':>8}")
        r.append("-" * 85)
        for p in previsoes:
            repor = "SIM ⚠️" if p["precisa_reposicao"] else "Nao"
            r.append(
                f"{p['produto'][:30]:<30} {p['estoque_atual']:>10.1f} "
                f"{p['consumo_medio_diario']:>10.1f} {p['previsao_consumo']:>10.1f} "
                f"{p['tendencia']:>12} {repor:>8}"
            )

        r.append("\n## Produtos que Precisam Reposicao Urgente\n")
        urgentes = [p for p in previsoes if p["precisa_reposicao"]]
        if urgentes:
            for p in urgentes:
                r.append(f"🔴 {p['produto']}")
                r.append(f"   Estoque atual: {p['estoque_atual']}")
                r.append(f"   Consumo medio: {p['consumo_medio_diario']}/dia")
                r.append(f"   Previsao 7 dias: {p['previsao_consumo']}")
                if p["dias_ate_esgotar"] is not None:
                    r.append(f"   Esgota em: {p['dias_ate_esgotar']} dias")
                r.append(f"   Sugestao de compra: {p['sugestao_compra']:.1f} unidades")
                r.append("")
        else:
            r.append("✅ Nenhum produto precisa reposicao imediata.")

        r.append("\n## Recomendacoes de Compra\n")
        compras = [p for p in previsoes if p["sugestao_compra"] > 0]
        if compras:
            total = sum(p["sugestao_compra"] for p in compras)
            r.append(f"Total de produtos para comprar: {len(compras)}")
            r.append(f"Quantidade total sugerida: {total:.1f} unidades")
        else:
            r.append("Nenhuma compra necessaria no momento.")

        return "\n".join(r)

    def gerar_relatorio_financeiro(self):
        r = []
        r.append(self._header("Relatorio Financeiro de Estoque"))
        fin = self.analyzer.analise_financeira()

        r.append("\n## Resumo Financeiro\n")
        r.append(f"- Valor investido (custo): R$ {fin['valor_custo_total']:.2f}")
        r.append(f"- Valor potencial de venda: R$ {fin['valor_venda_total']:.2f}")
        r.append(f"- Lucro potencial: R$ {fin['lucro_potencial']:.2f}")
        r.append(f"- Margem media: {fin['margem_media']}%")
        r.append(f"- Capital preso em produtos parados: R$ {fin['capital_preso']:.2f}")

        r.append("\n## Produtos com Baixa Margem (< 30%)\n")
        if fin["produtos_baixa_margem"]:
            for p in fin["produtos_baixa_margem"]:
                r.append(f"⚠️ {p['produto']} | Margem: {p['margem']}% | Custo: R$ {p['custo']:.2f} | Venda: R$ {p['venda']:.2f}")
        else:
            r.append("✅ Todos os produtos tem margem saudavel (> 30%).")

        r.append("\n## Produtos Parados (Capital Preso)\n")
        if fin["produtos_parados"]:
            for p in fin["produtos_parados"]:
                r.append(f"🔴 {p['produto']} | Estoque: {p['estoque']} | Valor preso: R$ {p['valor_preso']:.2f}")
            r.append(f"\nTotal de capital preso: R$ {fin['capital_preso']:.2f}")
        else:
            r.append("✅ Nao ha produtos parados.")

        r.append("\n## Recomendacoes\n")
        r.append("1. [ALTA] Reajustar preco de produtos com margem < 30% ou renegociar com fornecedor")
        r.append("2. [MEDIA] Criar promocao para produtos parados e liberar capital")
        r.append("3. [MEDIA] Revisar estoque maximo de produtos parados para nao exceder demanda")
        r.append("4. [BAIXA] Considerar descontinuar produtos com baixa margem e baixo consumo")

        return "\n".join(r)

    def gerar_relatorio_vencimento(self):
        r = []
        r.append(self._header("Alerta de Vencimento"))
        insights = [i for i in self.analyzer.insights_estoque() if i["tipo"] in ("vencido", "vencimento_proximo")]

        r.append("\n## Produtos Vencidos\n")
        vencidos = [i for i in insights if i["tipo"] == "vencido"]
        if vencidos:
            for ins in vencidos:
                r.append(f"🔴 {ins['descricao']}")
                r.append(f"   → {ins['acao']}")
            # Calcular valor em risco
            valor_risco = sum(
                float(p.current_stock) * float(p.cost_price)
                for p in self.analyzer.products if p.is_expired
            )
            r.append(f"\nValor financeiro em risco: R$ {valor_risco:.2f}")
        else:
            r.append("✅ Nenhum produto vencido.")

        r.append("\n## Produtos Vencendo em ate 7 dias\n")
        vencendo = [i for i in insights if i["tipo"] == "vencimento_proximo"]
        if vencendo:
            for ins in vencendo:
                r.append(f"🟡 {ins['descricao']}")
                r.append(f"   → {ins['acao']}")
        else:
            r.append("✅ Nenhum produto vencendo nos proximos 7 dias.")

        r.append("\n## Plano de Acao\n")
        if vencidos or vencendo:
            r.append("1. [IMEDIATO] Remover produtos vencidos do estoque e registrar perda")
            r.append("2. [IMEDIATO] Priorizar uso de produtos vencendo em preparos")
            r.append("3. [CURTO PRAZO] Criar promocoes para acelerar consumo de produtos proximos ao vencimento")
            r.append("4. [MEDIO PRAZO] Revisar quantidades de compra para produtos pereciveis")
            r.append("5. [MEDIO PRAZO] Implementar sistema FIFO (primeiro a vencer, primeiro a usar)")
        else:
            r.append("✅ Nenhuma acao necessaria. Estoque com validades controladas.")

        return "\n".join(r)

    def gerar_relatorio_fornecedores(self):
        r = []
        r.append(self._header("Analise de Fornecedores"))
        fornecedores = self.analyzer.analise_fornecedores()

        r.append("\n## Ranking de Fornecedores por Valor em Estoque\n")
        if fornecedores:
            for i, f in enumerate(fornecedores, 1):
                r.append(f"{i}. {f['nome']}")
                r.append(f"   Produtos fornecidos: {f['produtos']}")
                r.append(f"   Valor em estoque: R$ {f['valor_estoque']:.2f}")
                r.append(f"   Contato: {f['contato'] or '-'} | Tel: {f['telefone'] or '-'}")
                r.append("")
        else:
            r.append("Nenhum fornecedor vinculado a produtos.")

        r.append("\n## Recomendacoes\n")
        if fornecedores:
            top = fornecedores[0]
            r.append(f"1. Maior dependencia: {top['nome']} (R$ {top['valor_estoque']:.2f} em estoque)")
            r.append("2. Considere diversificar fornecedores para reduzir dependencia")
            r.append("3. Negociar descontos com fornecedores de maior volume")
            r.append("4. Avaliar prazos de entrega e qualidade dos produtos")
        else:
            r.append("Cadastre fornecedores e vincule aos produtos para analises completas.")

        return "\n".join(r)

    def _gerar_recomendacoes(self, insights, fin):
        r = ["\n## Recomendacoes\n"]
        alta = [i for i in insights if i["severidade"] == "alta"]
        media = [i for i in insights if i["severidade"] == "media"]

        if alta:
            r.append("### Prioridade Alta\n")
            for i, ins in enumerate(alta, 1):
                r.append(f"{i}. {ins['acao']}")

        if media:
            r.append("\n### Prioridade Media\n")
            for i, ins in enumerate(media, 1):
                r.append(f"{i}. {ins['acao']}")

        if fin["capital_preso"] > 0:
            r.append(f"\n### Financeiro\n")
            r.append(f"- Capital preso em produtos parados: R$ {fin['capital_preso']:.2f}")
            r.append("- Sugerir promocoes para liberar capital")

        if not alta and not media:
            r.append("✅ Estoque saudavel. Nenhuma acao critica necessaria.")
            r.append("- Continuar monitorando consumo e validades")
            r.append("- Manter rotina de conferencia de estoque")

        return "\n".join(r)

    def gerar(self, report_type="ai_custom"):
        geradores = {
            "ai_custom": self.gerar_relatorio_geral,
            "sales_forecast": self.gerar_previsao_demanda,
            "financial": self.gerar_relatorio_financeiro,
            "expiry_alert": self.gerar_relatorio_vencimento,
            "supplier_performance": self.gerar_relatorio_fornecedores,
        }
        gerar = geradores.get(report_type, self.gerar_relatorio_geral)
        return gerar()
