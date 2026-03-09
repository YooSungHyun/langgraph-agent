from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from graph.state import AgentState


async def researcher_node(state: AgentState) -> dict:
    """주어진 topic에 대해 핵심 정보를 수집하는 노드."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"다음 주제에 대해 핵심 사실과 배경 정보를 3~5가지로 정리해 주세요.\n\n주제: {state['topic']}"
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "research": response.content,
        "messages": [
            HumanMessage(content=prompt, name="researcher_input"),
            AIMessage(content=response.content, name="researcher"),
        ],
    }
