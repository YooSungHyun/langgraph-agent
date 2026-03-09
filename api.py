import json
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from graph import build_graph

load_dotenv()

app = FastAPI(title="Sequential Agent API")
graph = build_graph()


class RunRequest(BaseModel):
    topic: str


def _initial_state(topic: str) -> dict:
    return {
        "topic": topic,
        "messages": [],
        "research": "",
        "analysis": "",
        "final_report": "",
    }


@app.post("/run")
async def run(req: RunRequest) -> dict:
    """파이프라인을 실행하고 최종 결과를 한 번에 반환한다."""
    result = await graph.ainvoke(_initial_state(req.topic))
    return {
        "topic": result["topic"],
        "research": result["research"],
        "analysis": result["analysis"],
        "final_report": result["final_report"],
    }


@app.post("/run/stream")
async def run_stream(req: RunRequest) -> StreamingResponse:
    """각 노드 완료 시점마다 결과를 SSE로 스트리밍한다."""

    async def event_generator() -> AsyncIterator[str]:
        async for step in graph.astream(_initial_state(req.topic), stream_mode="updates"):
            node_name, output = next(iter(step.items()))
            payload = json.dumps({"node": node_name, "output": output}, ensure_ascii=False, default=str)
            yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
