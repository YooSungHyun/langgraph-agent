import asyncio

from dotenv import load_dotenv

from graph import build_graph, create_initial_state

load_dotenv()

NODE_LABELS = {
    "intake": "INTAKE",
    "supervisor": "SUPERVISOR",
    "code_helper": "CODE HELPER",
    "text_helper": "TEXT HELPER",
}


async def run(query: str) -> None:
    graph = build_graph()

    print(f"\n{'='*60}")
    print(f"질문: {query}")
    print(f"{'='*60}")

    current_node = None

    async for event in graph.astream_events(create_initial_state(query), version="v2"):
        kind = event["event"]
        name = event.get("name", "")

        if kind == "on_chain_start" and name in NODE_LABELS:
            current_node = name
            print(f"\n\n[{NODE_LABELS[name]}] {'━' * 40}")

        elif kind == "on_chat_model_stream" and current_node in NODE_LABELS:
            token = event["data"]["chunk"].content
            if token:
                print(token, end="", flush=True)

        elif kind == "on_chain_end" and name in NODE_LABELS:
            current_node = None

    print("\n")


if __name__ == "__main__":
    asyncio.run(run("오늘 날짜를 포함해서 Python으로 현재 시간을 출력하는 코드를 작성해줘"))
