from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """파이프라인 전체에서 공유되는 상태.

    각 노드는 이 상태를 읽고, 자신의 결과를 추가하거나 갱신한 뒤 반환한다.
    messages는 add_messages reducer로 누적되고, 나머지 필드는 덮어쓰기 방식이다.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    topic: str          # 파이프라인 입력 주제
    research: str       # researcher 노드 출력
    analysis: str       # analyzer 노드 출력
    final_report: str   # writer 노드 최종 출력
