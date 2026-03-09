from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage

from graph.state import AgentState


class IntakeNode:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def __call__(self, state: AgentState) -> dict:
        """사용자 질문을 받아 의도를 명확히 정리하는 입구 노드."""
        prompt = (
            "다음 사용자 질문을 간결하게 한 문장으로 재정리해 주세요. "
            "원래 의미를 유지하면서 모호한 표현을 명확하게 다듬어 주세요.\n\n"
            f"질문: {state['query']}"
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return {
            "query": response.content.strip(),
            "messages": [
                HumanMessage(content=state["query"], name="user"),
                AIMessage(content=response.content, name="intake"),
            ],
        }
