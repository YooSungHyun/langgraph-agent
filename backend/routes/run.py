import json
import time
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langgraph.graph.state import CompiledStateGraph

from backend.dependencies import get_graph
from backend.exception import AgentException, GraphInvokeException, agent_exception_handler
from backend.protocol import RunRequest, RunResponse, StreamRunRequest
from graph.state import create_initial_state

router = APIRouter(prefix="/run", tags=["run"])

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Access-Control-Allow-Origin": "*",
}

_STREAM_NODES = {"intake", "supervisor", "code_helper", "text_helper"}


@router.post("", response_model=RunResponse)
async def run(req: RunRequest, graph: CompiledStateGraph = Depends(get_graph)):
    try:
        start_time = time.time()
        result = await graph.ainvoke(create_initial_state(req.query))
        execution_time = time.time() - start_time

        return RunResponse(
            request_id=req.request_id,
            query=result["query"],
            route=result["route"],
            tool_result=result["tool_result"],
            final_answer=result["final_answer"],
            status="success",
            execution_time=execution_time,
        )

    except AgentException as e:
        raise agent_exception_handler(e)
    except Exception as e:
        raise agent_exception_handler(GraphInvokeException(str(e)))


@router.post("/stream", response_model=None)
async def run_stream(req: StreamRunRequest, graph: CompiledStateGraph = Depends(get_graph)):
    def _sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    async def event_generator() -> AsyncIterator[str]:
        current_node: str | None = None
        try:
            async for event in graph.astream_events(create_initial_state(req.query), version="v2"):
                kind = event["event"]
                name = event.get("name", "")

                if kind == "on_chain_start" and name in _STREAM_NODES:
                    current_node = name
                    yield _sse({"type": "node_start", "request_id": req.request_id, "node": name})

                elif kind == "on_chat_model_stream" and current_node in _STREAM_NODES:
                    token = event["data"]["chunk"].content
                    if token:
                        yield _sse({"type": "token", "request_id": req.request_id, "node": current_node, "token": token})

                elif kind == "on_chain_end" and name in _STREAM_NODES:
                    yield _sse({"type": "node_end", "request_id": req.request_id, "node": name})
                    current_node = None

            yield _sse({"type": "done", "request_id": req.request_id})

        except Exception as e:
            yield _sse({"type": "error", "request_id": req.request_id, "error": str(e)})

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=SSE_HEADERS)
