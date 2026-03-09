"""
API 서버 호출 예제

실행 전 서버를 먼저 시작하세요:
    uv run python api.py

그 다음 별도 터미널에서:
    uv run --group dev python examples/client.py
"""

import json
import httpx

BASE_URL = "http://localhost:8000"

QUERIES = [
    "오늘 날짜를 포함해서 Python으로 현재 시간을 출력하는 코드를 작성해줘",
    "블랙홀이 무엇인지 쉽게 설명해줘",
]


def call_run(query: str) -> None:
    """POST /run — 전체 완료 후 결과를 한 번에 받는다."""
    print("=" * 60)
    print(f"[POST /run] 일괄 호출")
    print(f"질문: {query}")
    print("=" * 60)

    response = httpx.post(
        f"{BASE_URL}/run",
        json={"query": query},
        timeout=120,
    )
    response.raise_for_status()

    result = response.json()
    print(f"request_id    : {result['request_id']}")
    print(f"route         : {result['route'].upper()}")
    print(f"execution_time: {result['execution_time']:.2f}s")
    if result["tool_result"]:
        print(f"\n[tool_result]\n{result['tool_result']}")
    print(f"\n[final_answer]\n{result['final_answer']}")


def call_run_stream(query: str) -> None:
    """POST /run/stream — 토큰 단위 SSE 스트리밍을 수신한다."""
    print("\n" + "=" * 60)
    print(f"[POST /run/stream] 토큰 스트리밍 호출")
    print(f"질문: {query}")
    print("=" * 60)

    with httpx.stream(
        "POST",
        f"{BASE_URL}/run/stream",
        json={"query": query},
        timeout=120,
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if not line.startswith("data:"):
                continue

            event = json.loads(line.removeprefix("data:").strip())
            event_type = event.get("type")

            if event_type == "node_start":
                node = event["node"].upper().replace("_", " ")
                print(f"\n\n[{node}] {'━' * 40}")

            elif event_type == "token":
                print(event["token"], end="", flush=True)

            elif event_type == "done":
                print(f"\n\n완료 (request_id: {event['request_id']})")

            elif event_type == "error":
                print(f"\n오류 발생: {event['error']}")


if __name__ == "__main__":
    call_run(QUERIES[0])
    call_run_stream(QUERIES[1])
