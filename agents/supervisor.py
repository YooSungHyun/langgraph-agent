from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from graph.state import AgentState


class RouteDecision(BaseModel):
    route: Literal["code", "text"]
    reason: str


class SupervisorNode:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm.with_structured_output(RouteDecision)

    async def __call__(self, state: AgentState) -> dict:
        """질문 유형을 분류해 code_helper 또는 text_helper로 라우팅하는 노드."""
        prompt = (
            "아래 질문이 코드 작성·디버깅·프로그래밍 언어·개발 도구 등 "
            "소프트웨어 개발과 직접 관련된 경우 route='code'로, "
            "그 외 일반 지식·글쓰기·설명 등은 route='text'로 분류하세요.\n\n"
            f"질문: {state['query']}"
        )
        decision: RouteDecision = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return {
            "route": decision.route,
            "messages": [
                AIMessage(
                    content=f"[라우팅] {decision.route.upper()} — {decision.reason}",
                    name="supervisor",
                ),
            ],
        }
