from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from graph.state import AgentState


async def writer_node(state: AgentState) -> dict:
    """조사 및 분석 결과를 종합해 최종 보고서를 작성하는 노드."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    prompt = (
        f"주제 '{state['topic']}'에 대한 최종 보고서를 작성해 주세요.\n\n"
        f"[조사 내용]\n{state['research']}\n\n"
        f"[분석 인사이트]\n{state['analysis']}\n\n"
        "보고서는 서론, 본론, 결론 구조로 작성하세요."
    )
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "final_report": response.content,
        "messages": [
            HumanMessage(content=prompt, name="writer_input"),
            AIMessage(content=response.content, name="writer"),
        ],
    }
