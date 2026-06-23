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
    analysis: str
    recommendations: str
    final_report: str


def gather_data(state: ReportState) -> ReportState:
    return state


def analyze(state: ReportState) -> ReportState:
    if llm is None:
        state["analysis"] = "[IA desativada - configure OPENAI_API_KEY]"
        return state

    prompt = f"""Analise os dados de estoque da açaiteria '{state.get("tenant_name", "")}'.

Dados de estoque:
{state.get("stock_data", "")}

Movimentações recentes:
{state.get("movement_data", "")}

Gere uma análise detalhada identificando:
1. Produtos com estoque crítico
2. Padrões de consumo
3. Produtos próximos ao vencimento
4. Oportunidades de otimização
"""
    response = llm.invoke([SystemMessage(content="Você é um analista de estoque especializado em açaiterias."), HumanMessage(content=prompt)])
    state["analysis"] = response.content
    return state


def recommend(state: ReportState) -> ReportState:
    if llm is None:
        state["recommendations"] = "[IA desativada]"
        return state

    prompt = f"""Com base na análise abaixo, gere recomendações práticas:

{state.get("analysis", "")}

Formate como lista numerada com ações concretas."""
    response = llm.invoke([HumanMessage(content=prompt)])
    state["recommendations"] = response.content
    return state


def compile_report(state: ReportState) -> ReportState:
    state["final_report"] = (
        f"# Relatório de Estoque\n\n"
        f"## Análise\n{state.get('analysis', '')}\n\n"
        f"## Recomendações\n{state.get('recommendations', '')}\n"
    )
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


def generate_ai_report(tenant_name: str, stock_data: dict, movement_data: list) -> str:
    state = ReportState(
        tenant_name=tenant_name,
        stock_data=json.dumps(stock_data, ensure_ascii=False, indent=2),
        movement_data=json.dumps(movement_data, ensure_ascii=False, indent=2),
        report_type="ai_custom",
    )
    result = report_app.invoke(state)
    return result.get("final_report", "")
