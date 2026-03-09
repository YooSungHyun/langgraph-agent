from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents import CodeHelperNode, IntakeNode, SupervisorNode, TextHelperNode
from config import AgentConfig, create_llm, get_settings
from graph.state import AgentState


def _route_after_supervisor(state: AgentState) -> str:
    """supervisor가 결정한 route 값으로 다음 노드를 선택한다."""
    return state["route"]


def build_graph(config: AgentConfig | None = None) -> CompiledStateGraph:
    """설정을 받아 supervisor 분기 그래프를 생성한다.

    흐름: START → intake → supervisor → (code_helper | text_helper) → END
    """
    agent_config = config or get_settings().agents

    builder = StateGraph(AgentState)
    builder.add_node("intake", IntakeNode(create_llm(agent_config.intake)))
    builder.add_node("supervisor", SupervisorNode(create_llm(agent_config.supervisor)))
    builder.add_node("code_helper", CodeHelperNode(create_llm(agent_config.code_helper)))
    builder.add_node("text_helper", TextHelperNode(create_llm(agent_config.text_helper)))

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        _route_after_supervisor,
        {"code": "code_helper", "text": "text_helper"},
    )
    builder.add_edge("code_helper", END)
    builder.add_edge("text_helper", END)

    return builder.compile()
