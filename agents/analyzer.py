from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from graph.state import AgentState


async def analyzer_node(state: AgentState) -> dict:
    """researcher가 수집한 내용을 바탕으로 시사점과 인사이트를 도출하는 노드."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = (
        f"아래 조사 내용을 분석하여 핵심 인사이트와 시사점을 도출해 주세요.\n\n"
        f"[조사 내용]\n{state['research']}"
    )
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "analysis": response.content,
        "messages": [
            HumanMessage(content=prompt, name="analyzer_input"),
            AIMessage(content=response.content, name="analyzer"),
        ],
    }
