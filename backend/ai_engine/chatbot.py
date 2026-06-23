"""
Chat Bot Interno do Acai Stock.

Responde perguntas do usuario analisando os dados do sistema em tempo real.
Nao depende de nenhuma API externa. Usa pattern matching + analise estatistica.
"""
import re
from datetime import datetime, timedelta

from django.utils import timezone

from ai_engine.engine import DataAnalyzer, media_movel
from ai_engine.knowledge_base import KnowledgeBase


class ChatBot:
    """Bot que responde perguntas sobre o estoque analisando dados reais."""

    def __init__(self, tenant):
        self.tenant = tenant
        self.analyzer = DataAnalyzer(tenant)
        self.kb = KnowledgeBase(tenant)

    def responder(self, pergunta):
        p = pergunta.lower().strip()

        # Estoque baixo
        if any(w in p for w in ["estoque baixo", "baixo estoque", "precisa repor", "reposicao"]):
            return self._resposta_estoque_baixo()

        # Vencidos / validade
        if any(w in p for w in ["vencido", "vencida", "validade", "vencendo"]):
            return self._resposta_vencidos()

        # Previsao / demanda / futuro
        if any(w in p for w in ["previsao", "demanda", "futuro", "vai acabar", "esgotar", "quanto vou vender"]):
            return self._resposta_previsao()

        # Financeiro / lucro / valor
        if any(w in p for w in ["lucro", "financeiro", "valor", "margem", "custo", "preco", "dinheiro", "capital"]):
            return self._resposta_financeiro()

        # Fornecedores
        if any(w in p for w in ["fornecedor", "fornecedores"]):
            return self._resposta_fornecedores()

        # Top produtos / mais vendidos / consumo
        if any(w in p for w in ["mais vendido", "top", "mais consumido", "mais sai", "ranking"]):
            return self._resposta_top_produtos()

        # Produtos parados
        if any(w in p for w in ["parado", "sem movimento", "encalhado", "parado no estoque"]):
            return self._resposta_produtos_parados()

        # Quantos produtos / total
        if any(w in p for w in ["quantos produtos", "total de produtos", "qtd produtos"]):
            return self._resposta_total_produtos()

        # Perdas / desperdicio
        if any(w in p for w in ["perda", "perdas", "desperdicio", "desperdic"]):
            return self._resposta_perdas()

        # Movimentacoes
        if any(w in p for w in ["movimentacao", "movimentacoes", "entrada", "saida"]):
            return self._resposta_movimentacoes()

        # Assinatura / plano
        if any(w in p for w in ["plano", "assinatura", "pagamento", "mensalidade"]):
            return self._resposta_assinatura()

        # O que voce sabe / ajuda
        if any(w in p for w in ["ajuda", "o que voce sabe", "pode fazer", "comandos", "help"]):
            return self._resposta_ajuda()

        # Saudacao
        if any(w in p for w in ["ola", "oi", "bom dia", "boa tarde", "boa noite"]):
            return f"Ola! Sou o assistente do Acai Stock. Posso analisar seu estoque e responder perguntas. Digite 'ajuda' para ver o que posso fazer."

        # Tentar identificar nome de produto
        produtos_nomes = [prod.name.lower() for prod in self.analyzer.products]
        for prod in self.analyzer.products:
            if prod.name.lower() in p:
                return self._resposta_produto_especifico(prod)

        return self._resposta_padrao(pergunta)

    def _resposta_estoque_baixo(self):
        insights = [i for i in self.analyzer.insights_estoque() if i["tipo"] in ("estoque_baixo", "reposicao_urgente")]
        if not insights:
            return "✅ Nenhum produto com estoque baixo no momento. Tudo sob controle!"
        linhas = ["🔴 Produtos com estoque baixo:\n"]
        for ins in insights:
            linhas.append(f"• {ins['descricao']}")
            linhas.append(f"  → {ins['acao']}")
        return "\n".join(linhas)

    def _resposta_vencidos(self):
        insights = [i for i in self.analyzer.insights_estoque() if i["tipo"] in ("vencido", "vencimento_proximo")]
        if not insights:
            return "✅ Nenhum produto vencido ou proximo ao vencimento!"
        linhas = ["⚠️ Alertas de validade:\n"]
        for ins in insights:
            emoji = "🔴" if ins["severidade"] == "alta" else "🟡"
            linhas.append(f"{emoji} {ins['descricao']}")
            linhas.append(f"  → {ins['acao']}")
        return "\n".join(linhas)

    def _resposta_previsao(self):
        previsoes = self.analyzer.previsao_demanda(7)
        urgentes = [p for p in previsoes if p["precisa_reposicao"]]
        if not urgentes:
            return "✅ Com base no consumo dos ultimos 30 dias, nenhum produto deve esgotar nos proximos 7 dias."
        linhas = ["📊 Previsao de demanda (7 dias) - Produtos que precisam reposicao:\n"]
        for p in urgentes[:5]:
            linhas.append(f"• {p['produto']}")
            linhas.append(f"  Estoque: {p['estoque_atual']} | Consumo/dia: {p['consumo_medio_diario']}")
            if p["dias_ate_esgotar"] is not None:
                linhas.append(f"  Esgota em ~{p['dias_ate_esgotar']} dias | Tendencia: {p['tendencia']}")
            linhas.append(f"  Sugestao de compra: {p['sugestao_compra']:.1f} unidades")
        return "\n".join(linhas)

    def _resposta_financeiro(self):
        fin = self.analyzer.analise_financeira()
        linhas = [
            "💰 Analise Financeira do Estoque:\n",
            f"• Valor investido (custo): R$ {fin['valor_custo_total']:.2f}",
            f"• Valor potencial de venda: R$ {fin['valor_venda_total']:.2f}",
            f"• Lucro potencial: R$ {fin['lucro_potencial']:.2f}",
            f"• Margem media: {fin['margem_media']}%",
            f"• Capital preso (produtos parados): R$ {fin['capital_preso']:.2f}",
        ]
        if fin["produtos_baixa_margem"]:
            linhas.append(f"\n⚠️ {len(fin['produtos_baixa_margem'])} produto(s) com margem < 30%. Considere reajustar precos.")
        return "\n".join(linhas)

    def _resposta_fornecedores(self):
        forts = self.analyzer.analise_fornecedores()
        if not forts:
            return "Nenhum fornecedor vinculado a produtos ainda. Cadastre fornecedores e vincule aos produtos."
        linhas = ["🏭 Fornecedores cadastrados:\n"]
        for f in forts:
            linhas.append(f"• {f['nome']} - {f['produtos']} produto(s) | R$ {f['valor_estoque']:.2f} em estoque")
            if f["telefone"]:
                linhas.append(f"  Tel: {f['telefone']}")
        return "\n".join(linhas)

    def _resposta_top_produtos(self):
        top = self.analyzer.top_produtos_consumo(5)
        if not top:
            return "Ainda nao ha dados de consumo suficientes. Registre movimentacoes de saida para gerar estatisticas."
        linhas = ["🏆 Top 5 produtos por consumo (30 dias):\n"]
        for i, t in enumerate(top, 1):
            linhas.append(f"{i}. {t['produto']} - {t['consumo_30d']} unidades (media: {t['media_diaria']}/dia)")
        return "\n".join(linhas)

    def _resposta_produtos_parados(self):
        fin = self.analyzer.analise_financeira()
        if not fin["produtos_parados"]:
            return "✅ Nenhum produto parado! Todos tiveram movimentacao nos ultimos 30 dias."
        linhas = [f"🔴 {len(fin['produtos_parados'])} produto(s) sem movimentacao (capital preso: R$ {fin['capital_preso']:.2f}):\n"]
        for p in fin["produtos_parados"]:
            linhas.append(f"• {p['produto']} - Estoque: {p['estoque']} | Valor: R$ {p['valor_preso']:.2f}")
        linhas.append("\nSugestao: crie promocoes para liberar o capital preso.")
        return "\n".join(linhas)

    def _resposta_total_produtos(self):
        s = self.data["resumo_estoque"]
        return (f"Total de produtos ativos: {s['total_produtos']}\n"
                f"Valor em estoque: R$ {s['valor_total_estoque']:.2f}\n"
                f"Produtos com estoque baixo: {len(s['produtos_estoque_baixo'])}\n"
                f"Produtos vencidos: {len(s['produtos_vencidos'])}")

    def _resposta_perdas(self):
        mov = self.analyzer.resumo_movimentacoes()
        return (f"📊 Perdas nos ultimos 30 dias:\n"
                f"• Total de perdas: {mov['perda']:.1f} unidades\n"
                f"• Taxa de perda: {mov['taxa_perda']}% do total de saidas\n"
                f"• Total de movimentacoes: {mov['total']}")

    def _resposta_movimentacoes(self):
        mov = self.analyzer.resumo_movimentacoes()
        return (f"📋 Movimentacoes dos ultimos 30 dias:\n"
                f"• Total: {mov['total']}\n"
                f"• Entradas: {mov['entrada']:.1f}\n"
                f"• Saidas: {mov['saida']:.1f}\n"
                f"• Perdas: {mov['perda']:.1f}\n"
                f"• Ajustes: {mov['ajuste']:.1f}\n"
                f"• Taxa de perda: {mov['taxa_perda']}%")

    def _resposta_assinatura(self):
        sub = self.data.get("assinatura")
        if not sub:
            return "Nenhuma assinatura configurada para este tenant."
        return (f"📋 Sua assinatura:\n"
                f"• Plano: {sub['plano']}\n"
                f"• Status: {sub['status']}\n"
                f"• Ciclo: {sub['ciclo']}\n"
                f"• Valor: R$ {sub['valor']:.2f}\n"
                f"• Periodo: {sub['periodo_inicio']} a {sub['periodo_fim']}")

    def _resposta_produto_especifico(self, produto):
        from ai_engine.engine import media_movel
        serie = self.analyzer._serie_temporal(produto.id)
        consumo_medio = media_movel(serie, 7)
        total_30d = sum(serie)
        linhas = [
            f"📦 {produto.name}:\n",
            f"• Estoque atual: {produto.current_stock} {produto.get_unit_display()}",
            f"• Estoque minimo: {produto.min_stock}",
            f"• Preco custo: R$ {produto.cost_price:.2f} | Venda: R$ {produto.sale_price:.2f}",
            f"• Consumo medio (7 dias): {consumo_medio:.1f}/dia",
            f"• Consumo total (30 dias): {total_30d:.1f}",
        ]
        if produto.expiry_date:
            linhas.append(f"• Validade: {produto.expiry_date.strftime('%d/%m/%Y')}")
            if produto.is_expired:
                linhas.append("🔴 PRODUTO VENCIDO!")
            elif produto.days_to_expiry is not None and produto.days_to_expiry <= 7:
                linhas.append(f"🟡 Vence em {produto.days_to_expiry} dias!")
        if produto.is_low_stock:
            linhas.append("🔴 ESTOQUE BAIXO!")
        if produto.supplier:
            linhas.append(f"• Fornecedor: {produto.supplier.name}")
        return "\n".join(linhas)

    def _resposta_ajuda(self):
        return """🤖 Posso ajudar com:

• "estoque baixo" - mostra produtos com estoque critico
• "vencidos" - alertas de validade
• "previsao de demanda" - previsao de consumo para 7 dias
• "lucro" ou "financeiro" - analise financeira do estoque
• "fornecedores" - ranking de fornecedores
• "top produtos" - produtos mais consumidos
• "produtos parados" - capital preso em estoque
• "perdas" - taxa de desperdicio
• "movimentacoes" - resumo de entradas e saidas
• "assinatura" - dados do seu plano

Voce tambem pode perguntar sobre um produto especifico pelo nome!

Exemplo: "Como esta o estoque de Acai?\""""

    def _resposta_padrao(self, pergunta):
        return ("Nao entendi exatamente sua pergunta. Digite 'ajuda' para ver o que posso fazer.\n"
                f"Sua pergunta foi: \"{pergunta}\"")
