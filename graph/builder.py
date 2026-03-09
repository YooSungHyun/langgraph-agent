from langgraph.graph import StateGraph, START, END

from graph.state import AgentState
from agents import researcher_node, analyzer_node, writer_node


def build_graph() -> StateGraph:
    """시퀀셜 파이프라인 그래프를 생성하고 컴파일해서 반환한다.

    흐름: START → researcher → analyzer → writer → END
    """
    builder = StateGraph(AgentState)

    builder.add_node("researcher", researcher_node)
    builder.add_node("analyzer", analyzer_node)
    builder.add_node("writer", writer_node)

    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", "analyzer")
    builder.add_edge("analyzer", "writer")
    builder.add_edge("writer", END)

    return builder.compile()
