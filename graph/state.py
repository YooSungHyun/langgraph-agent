from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """파이프라인 전체에서 공유되는 상태.

    흐름: intake → supervisor → (code_helper | text_helper)
    messages는 add_messages reducer로 누적되고, 나머지 필드는 덮어쓰기 방식이다.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    query: str                       # 사용자 입력 질문
    route: Literal["code", "text"]   # supervisor 라우팅 결정
    tool_result: str                 # helper 노드의 툴 호출 결과
    final_answer: str                # 최종 답변


def create_initial_state(query: str) -> AgentState:
    return AgentState(
        messages=[],
        query=query,
        route="text",
        tool_result="",
        final_answer="",
    )
