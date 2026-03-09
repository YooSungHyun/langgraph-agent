from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agents.tools import TOOLS, get_current_datetime
from graph.state import AgentState


def _to_str(content) -> str:
    """AIMessage.content가 list로 반환되는 경우(Gemini 등)를 단일 문자열로 정규화."""
    if isinstance(content, str):
        return content
    return "\n".join(part if isinstance(part, str) else part.get("text", "") for part in content)


class TextHelperNode:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm.bind_tools(TOOLS)

    async def __call__(self, state: AgentState) -> dict:
        """일반 지식·설명 질문에 답변하는 노드. 필요 시 get_current_datetime 툴을 호출한다."""
        system = (
            "당신은 친절하고 박식한 어시스턴트입니다. "
            "질문에 대해 이해하기 쉬운 언어로 상세하게 답변하세요. "
            "현재 날짜나 시간이 필요하다면 get_current_datetime 툴을 사용하세요."
        )
        messages = [
            HumanMessage(content=f"[시스템] {system}"),
            HumanMessage(content=state["query"]),
        ]

        response = await self.llm.ainvoke(messages)

        tool_result = ""
        final_content = _to_str(response.content)

        if response.tool_calls:
            messages.append(response)
            for tc in response.tool_calls:
                if tc["name"] == "get_current_datetime":
                    tool_result = get_current_datetime.invoke({})
                    messages.append(
                        ToolMessage(content=tool_result, tool_call_id=tc["id"])
                    )

            follow_up = await self.llm.ainvoke(messages)
            final_content = _to_str(follow_up.content)

        return {
            "tool_result": tool_result,
            "final_answer": final_content,
            "messages": [
                AIMessage(content=final_content, name="text_helper"),
            ],
        }
