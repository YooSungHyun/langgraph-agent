from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agents.tools import TOOLS, get_current_datetime
from graph.state import AgentState


class CodeHelperNode:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm.bind_tools(TOOLS)

    async def __call__(self, state: AgentState) -> dict:
        """코드·개발 관련 질문에 답변하는 노드. 필요 시 get_current_datetime 툴을 호출한다."""
        system = (
            "당신은 숙련된 소프트웨어 엔지니어입니다. "
            "코드 예시와 함께 명확하고 실용적인 답변을 제공하세요. "
            "현재 날짜나 시간이 필요하다면 get_current_datetime 툴을 사용하세요."
        )
        messages = [
            HumanMessage(content=f"[시스템] {system}"),
            HumanMessage(content=state["query"]),
        ]

        response = await self.llm.ainvoke(messages)

        tool_result = ""
        final_content = response.content

        if response.tool_calls:
            messages.append(response)
            for tc in response.tool_calls:
                if tc["name"] == "get_current_datetime":
                    tool_result = get_current_datetime.invoke({})
                    messages.append(
                        ToolMessage(content=tool_result, tool_call_id=tc["id"])
                    )

            follow_up = await self.llm.ainvoke(messages)
            final_content = follow_up.content

        return {
            "tool_result": tool_result,
            "final_answer": final_content,
            "messages": [
                AIMessage(content=final_content, name="code_helper"),
            ],
        }
