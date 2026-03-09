from graph.state import AgentState

def route_from_supervisor(state: AgentState) -> str:
    """supervisor가 결정한 route를 다음 노드 이름으로 변환한다."""
    if state["route"] == "code":
        return "code_helper"
    elif state["route"] == "text":
        return "text_helper"
    else:
        raise ValueError(f"Unknown route: {state['route']}")
