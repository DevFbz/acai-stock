import json
from typing import TypedDict

from django.conf import settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from ai_engine.knowledge_base import KnowledgeBase


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=settings.OPENAI_API_KEY,
) if settings.OPENAI_API_KEY else None

SYSTEM_PROMPT = """Voce e o Analista Inteligente do Acai Stock, um sistema de gestao de estoque para acaiterias.

Voce tem acesso COMPLETO a base de conhecimento do tenant, que inclui:
- Todos os produtos e seus detalhes (estoque, precos, validade)
- Todas as movimentacoes dos ultimos 30 dias
- Fornecedores e seus dados
- Pedidos de compra
- Estatisticas financeiras (custo, venda, lucro, margem)
- Alertas ativos (estoque baixo, vencimentos, perdas)
- Assinatura e status de pagamento

Voce "sabe" tudo sobre o estoque do cliente. Use TODOS esses dados para gerar
analises precisas, recomendacoes acionaveis e previsoes fundamentadas.

Sempre responda em portugues brasileiro de forma profissional e pratica."""


class ReportState(TypedDict, total=False):
    tenant_name: str
    knowledge_text: str
    report_type: str
    user_query: str
    analysis: str
    recommendations: str
    forecast: str
    final_report: str


def gather_data(state: ReportState) -> ReportState:
    return state


REPORT_PROMPTS = {
    "ai_custom": """Com base em TODOS os dados da base de conhecimento abaixo, gere um relatorio completo de estoque:

{knowledge}

Gere:
1. Visao geral do estoque (valor, quantidade, status)
2. Analise de produtos criticos (estoque baixo, vencidos)
3. Analise de consumo (produtos com maior saida)
4. Analise financeira (custo, venda, margem, lucro potencial)
5. Oportunidades de otimizacao""",

    "sales_forecast": """Com base em TODOS os dados de movimentacoes e estoque da base de conhecimento abaixo:

{knowledge}

Gere uma PREVISAO DE DEMANDA para os proximos 7 e 14 dias:
1. Para cada produto, estime a demanda baseada no historico de saidas
2. Identifique quais produtos precisarao reposicao antes de esgotar
3. Calcule o ponto de reposicao ideal para cada produto
4. Identifique tendencias de consumo (crescimento/queda)
5. Considere sazonalidade e produtos pereciveis""",

    "supplier_performance": """Com base na base de conhecimento abaixo:

{knowledge}

Analise o desempenho de fornecedores:
1. Fornecedores mais utilizados (por quantidade de produtos)
2. Produtos por fornecedor e dependencia
3. Recomendacoes de consolidacao de compras
4. Sugestoes de negociacao ou busca de novos fornecedores
5. Analise de prazos de entrega (se houver dados)""",

    "expiry_alert": """Com base na base de conhecimento abaixo:

{knowledge}

Gere um plano de acao para produtos proximos ao vencimento:
1. Lista de produtos vencidos (acao imediata)
2. Lista de produtos vencendo em ate 7 dias
3. Valor financeiro em risco
4. Estrategias para evitar perdas (promocoes, priorizacao, doacao)
5. Plano de acao por produto com prioridade""",

    "financial": """Com base na base de conhecimento abaixo:

{knowledge}

Gere um relatorio financeiro do estoque:
1. Valor total investido em estoque
2. Valor potencial de venda
3. Margem de lucro por produto e geral
4. Produtos com baixa margem (sugerir reajuste)
5. Produtos parados (sem movimentacao) que representam capital preso
6. Recomendacoes para melhorar o fluxo de caixa""",
}


def analyze(state: ReportState) -> ReportState:
    if llm is None:
        state["analysis"] = "[IA desativada - configure OPENAI_API_KEY no arquivo .env]"
        state["recommendations"] = "[IA desativada]"
        state["forecast"] = ""
        state["final_report"] = state["analysis"]
        return state

    knowledge = state.get("knowledge_text", "")
    report_type = state.get("report_type", "ai_custom")
    prompt_template = REPORT_PROMPTS.get(report_type, REPORT_PROMPTS["ai_custom"])
    prompt = prompt_template.format(knowledge=knowledge)

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    state["analysis"] = response.content
    return state


def recommend(state: ReportState) -> ReportState:
    if llm is None:
        return state

    prompt = f"""Com base na analise abaixo, gere recomendacoes praticas e acionaveis:

{state.get("analysis", "")}

Formate como lista numerada com:
- Acao concreta
- Prioridade (Alta/Media/Baixa)
- Prazo sugerido (Imediato/Curto prazo/Medio prazo)
- Responsavel sugerido (Compras/Gestao/Operacao)"""
    response = llm.invoke([HumanMessage(content=prompt)])
    state["recommendations"] = response.content
    return state


def compile_report(state: ReportState) -> ReportState:
    report_type = state.get("report_type", "ai_custom")
    titles = {
        "ai_custom": "Relatorio Geral de Estoque",
        "sales_forecast": "Previsao de Demanda",
        "supplier_performance": "Desempenho de Fornecedores",
        "expiry_alert": "Alerta de Vencimento",
        "financial": "Relatorio Financeiro de Estoque",
    }
    title = titles.get(report_type, "Relatorio")

    parts = [
        f"# {title} - {state.get('tenant_name', '')}",
        f"Gerado em: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "## Analise",
        state.get("analysis", ""),
        "",
        "## Recomendacoes",
        state.get("recommendations", ""),
    ]
    state["final_report"] = "\n".join(parts)
    return state


def build_report_graph():
    graph = StateGraph(ReportState)
    graph.add_node("gather", gather_data)
    graph.add_node("analyze", analyze)
    graph.add_node("recommend", recommend)
    graph.add_node("compile", compile_report)

    graph.set_entry_point("gather")
    graph.add_edge("gather", "analyze")
    graph.add_edge("analyze", "recommend")
    graph.add_edge("recommend", "compile")
    graph.add_edge("compile", END)

    return graph.compile()


report_app = build_report_graph()


def generate_ai_report(tenant, report_type="ai_custom"):
    """Gera relatorio usando a base de conhecimento completa do tenant."""
    kb = KnowledgeBase(tenant)
    state = ReportState(
        tenant_name=tenant.name,
        knowledge_text=kb.to_text(),
        report_type=report_type,
    )
    result = report_app.invoke(state)
    return result.get("final_report", "")


# ==================== Chat IA ====================

class ChatState(TypedDict, total=False):
    tenant_name: str
    knowledge_text: str
    user_query: str
    response: str


def chat_respond(state: ChatState) -> ChatState:
    if llm is None:
        state["response"] = "[IA desativada - configure OPENAI_API_KEY no .env]"
        return state

    prompt = f"""Voce e o assistente do Acai Stock. O usuario fez uma pergunta sobre o estoque dele.

BASE DE CONHECIMENTO (tudo que voce sabe sobre o estoque do cliente):
{state.get("knowledge_text", "")}

PERGUNTA DO USUARIO: {state.get("user_query", "")}

Responda de forma clara e pratica, usando os dados reais da base de conhecimento.
Se nao houver dados suficientes, diga o que esta faltando."""
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    state["response"] = response.content
    return state


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("chat_respond", chat_respond)
    graph.set_entry_point("chat_respond")
    graph.add_edge("chat_respond", END)
    return graph.compile()


chat_app = build_chat_graph()


def chat_with_ai(tenant, user_query):
    """Chat usando a base de conhecimento completa."""
    kb = KnowledgeBase(tenant)
    state = ChatState(
        tenant_name=tenant.name,
        knowledge_text=kb.to_text(),
        user_query=user_query,
    )
    result = chat_app.invoke(state)
    return result.get("response", "")
