"""
Orquestracao do motor de IA interno usando LangGraph.

A IA e 100% local - nao depende de OpenAI, Claude ou qualquer API externa.
Usa LangGraph apenas para orquestrar o fluxo: coletar dados -> analisar -> compilar.
"""
from typing import TypedDict

from langgraph.graph import END, StateGraph

from ai_engine.nlg import ReportGenerator
from ai_engine.chatbot import ChatBot


class ReportState(TypedDict, total=False):
    tenant_id: int
    report_type: str
    report_text: str


def gather_data(state: ReportState) -> ReportState:
    return state


def compile_report(state: ReportState) -> ReportState:
    from tenants.models import Tenant
    tenant = Tenant.objects.get(pk=state["tenant_id"])
    generator = ReportGenerator(tenant)
    state["report_text"] = generator.gerar(state.get("report_type", "ai_custom"))
    return state


def build_report_graph():
    graph = StateGraph(ReportState)
    graph.add_node("gather", gather_data)
    graph.add_node("compile", compile_report)
    graph.set_entry_point("gather")
    graph.add_edge("gather", "compile")
    graph.add_edge("compile", END)
    return graph.compile()


report_app = build_report_graph()


def generate_ai_report(tenant, report_type="ai_custom"):
    """Gera relatorio usando o motor de IA interno (sem API externa)."""
    state = ReportState(tenant_id=tenant.pk, report_type=report_type)
    result = report_app.invoke(state)
    return result.get("report_text", "")


# ==================== Chat ====================

class ChatState(TypedDict, total=False):
    tenant_id: int
    user_query: str
    response: str


def chat_respond(state: ChatState) -> ChatState:
    from tenants.models import Tenant
    tenant = Tenant.objects.get(pk=state["tenant_id"])
    bot = ChatBot(tenant)
    state["response"] = bot.responder(state.get("user_query", ""))
    return state


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("chat_respond", chat_respond)
    graph.set_entry_point("chat_respond")
    graph.add_edge("chat_respond", END)
    return graph.compile()


chat_app = build_chat_graph()


def chat_with_ai(tenant, user_query):
    """Chat usando o bot interno (sem API externa)."""
    state = ChatState(tenant_id=tenant.pk, user_query=user_query)
    result = chat_app.invoke(state)
    return result.get("response", "")
