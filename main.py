import os
from dotenv import load_dotenv
from graph import build_graph

load_dotenv()  # .env 파일에서 OPENAI_API_KEY 로드


def run(topic: str) -> None:
    graph = build_graph()

    initial_state = {
        "topic": topic,
        "messages": [],
        "research": "",
        "analysis": "",
        "final_report": "",
    }

    print(f"\n{'='*60}")
    print(f"주제: {topic}")
    print(f"{'='*60}\n")

    # stream()으로 각 노드 실행 결과를 순서대로 출력
    for step in graph.stream(initial_state, stream_mode="updates"):
        node_name, output = next(iter(step.items()))
        print(f"[{node_name.upper()}] 완료")

        if node_name == "researcher":
            print(output["research"])
        elif node_name == "analyzer":
            print(output["analysis"])
        elif node_name == "writer":
            print("\n--- 최종 보고서 ---")
            print(output["final_report"])

        print()


if __name__ == "__main__":
    run("생성형 AI가 소프트웨어 개발에 미치는 영향")
