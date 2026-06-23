import json
from typing import TypedDict

from django.conf import settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=settings.OPENAI_API_KEY,
) if settings.OPENAI_API_KEY else None


class ReportState(TypedDict, total=False):
    tenant_name: str
    stock_data: str
    movement_data: str
    report_type: str
    user_query: str
    analysis: str
    recommendations: str
    forecast: str
    final_report: str


def gather_data(state: ReportState) -> ReportState:
    return state


def analyze(state: ReportState) -> ReportState:
    if llm is None:
        state["analysis"] = "[IA desativada - configure OPENAI_API_KEY no .env]"
        return state

    report_type = state.get("report_type", "ai_custom")
    prompts = {
        "ai_custom": f"""Analise os dados de estoque da acaiteria '{state.get("tenant_name", "")}'.

Dados de estoque:
{state.get("stock_data", "")}

Movimentacoes recentes:
{state.get("movement_data", "")}

Gere uma analise detalhada identificando:
1. Produtos com estoque critico
2. Padroes de consumo
3. Produtos proximos ao vencimento
4. Oportunidades de otimizacao""",
        "sales_forecast": f"""Com base nos dados de movimentacao da acaiteria '{state.get("tenant_name", "")}':

{state.get("movement_data", "")}

E dados de estoque atual:
{state.get("stock_data", "")}

Gere uma previsao de demanda para os proximos 7 dias:
1. Produtos que terao maior saida
2. Quantidade estimada por produto
3. Produtos que precisam reposicao antes da previsao esgotar
4. Sazonalidade ou tendencias identificadas""",
        "supplier_performance": f"""Analise o desempenho de fornecedores da acaiteria '{state.get("tenant_name", "")}'.

Dados:
{state.get("stock_data", "")}

Movimentacoes:
{state.get("movement_data", "")}

Gere analise de:
1. Fornecedores mais utilizados
2. Produtos por fornecedor
3. Recomendacoes de consolidacao de compras
4. Sugestoes de negociacao""",
        "expiry_alert": f"""Analise produtos proximos ao vencimento da acaiteria '{state.get("tenant_name", "")}'.

Dados de estoque:
{state.get("stock_data", "")}

Gere:
1. Lista de produtos vencendo em ate 7 dias
2. Estrategias para evitar perdas (promocoes, priorizacao de uso)
3. Valor financeiro em risco
4. Plano de acao imediato""",
    }

    prompt = prompts.get(report_type, prompts["ai_custom"])
    response = llm.invoke([
        SystemMessage(content="Voce e um analista de estoque especializado em acaiterias. Use portugues brasileiro."),
        HumanMessage(content=prompt),
    ])
    state["analysis"] = response.content
    return state


def forecast_node(state: ReportState) -> ReportState:
    if llm is None:
        state["forecast"] = ""
        return state

    if state.get("report_type") == "sales_forecast":
        prompt = f"""Com base na analise abaixo, gere uma tabela de previsao de demanda em formato markdown:

{state.get("analysis", "")}

Inclua colunas: Produto, Previsao 7 dias, Estoque atual, Necessita reposicao (Sim/Nao)."""
        response = llm.invoke([HumanMessage(content=prompt)])
        state["forecast"] = response.content
    else:
        state["forecast"] = ""
    return state


def recommend(state: ReportState) -> ReportState:
    if llm is None:
        state["recommendations"] = "[IA desativada]"
        return state

    forecast_text = state.get("forecast", "")
    forecast_section = f"\n\nPrevisao:\n{forecast_text}\n" if forecast_text else ""
    prompt = f"""Com base na analise abaixo, gere recomendacoes praticas e acionaveis:

{state.get("analysis", "")}{forecast_section}

Formate como lista numerada com acoes concretas e prioridades (Alta/Media/Baixa)."""
    response = llm.invoke([HumanMessage(content=prompt)])
    state["recommendations"] = response.content
    return state


def compile_report(state: ReportState) -> ReportState:
    parts = [f"# Relatorio de Estoque - {state.get('tenant_name', '')}\n"]
    parts.append(f"## Analise\n{state.get('analysis', '')}\n")
    if state.get("forecast"):
        parts.append(f"## Previsao de Demanda\n{state.get('forecast', '')}\n")
    parts.append(f"## Recomendacoes\n{state.get('recommendations', '')}\n")
    state["final_report"] = "\n".join(parts)
    return state


def build_report_graph():
    graph = StateGraph(ReportState)
    graph.add_node("gather", gather_data)
    graph.add_node("analyze", analyze)
    graph.add_node("do_forecast", forecast_node)
    graph.add_node("recommend", recommend)
    graph.add_node("compile", compile_report)

    graph.set_entry_point("gather")
    graph.add_edge("gather", "analyze")
    graph.add_edge("analyze", "do_forecast")
    graph.add_edge("do_forecast", "recommend")
    graph.add_edge("recommend", "compile")
    graph.add_edge("compile", END)

    return graph.compile()


report_app = build_report_graph()


def generate_ai_report(tenant_name, stock_data, movement_data, report_type="ai_custom"):
    state = ReportState(
        tenant_name=tenant_name,
        stock_data=json.dumps(stock_data, ensure_ascii=False, indent=2),
        movement_data=json.dumps(movement_data, ensure_ascii=False, indent=2),
        report_type=report_type,
    )
    result = report_app.invoke(state)
    return result.get("final_report", "")


# ==================== Chat IA ====================

class ChatState(TypedDict, total=False):
    tenant_name: str
    context_data: str
    user_query: str
    response: str


def chat_retrieve(state: ChatState) -> ChatState:
    return state


def chat_respond(state: ChatState) -> ChatState:
    if llm is None:
        state["response"] = "[IA desativada - configure OPENAI_API_KEY]"
        return state

    prompt = f"""Contexto do estoque da acaiteria '{state.get("tenant_name", "")}':
{state.get("context_data", "")}

Pergunta do usuario: {state.get("user_query", "")}

Responda em portugues brasileiro de forma clara e pratica. Use os dados do contexto."""
    response = llm.invoke([
        SystemMessage(content="Voce e um assistente de gestao de estoque para acaiterias. Responda de forma concisa e pratica."),
        HumanMessage(content=prompt),
    ])
    state["response"] = response.content
    return state


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("chat_retrieve", chat_retrieve)
    graph.add_node("chat_respond", chat_respond)
    graph.set_entry_point("chat_retrieve")
    graph.add_edge("chat_retrieve", "chat_respond")
    graph.add_edge("chat_respond", END)
    return graph.compile()


chat_app = build_chat_graph()


def chat_with_ai(tenant_name, context_data, user_query):
    state = ChatState(
        tenant_name=tenant_name,
        context_data=json.dumps(context_data, ensure_ascii=False),
        user_query=user_query,
    )
    result = chat_app.invoke(state)
    return result.get("response", "")
