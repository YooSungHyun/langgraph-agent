# Supervisor Agent

LangGraph 기반 Supervisor 패턴 멀티 에이전트 파이프라인

## 예제 태스크와 노드 구조

### 예제 태스크

사용자가 자연어 질문을 입력하면, 파이프라인이 질문의 **성격을 자동으로 판단**해 전담 노드로 라우팅한 뒤 답변을 생성합니다.

- **코드 관련 질문** (코드 작성·디버깅·라이브러리 사용법 등) → `code_helper`
- **일반 지식 질문** (개념 설명·역사·과학 등) → `text_helper`

두 helper 노드 모두 **`get_current_datetime` 툴**을 사용할 수 있으며, LLM이 날짜·시간 정보가 필요하다고 판단하면 자동으로 호출합니다.

### 노드 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   START ──► intake ──► supervisor ──► code_helper ──► END       │
│                                  └──► text_helper ──► END       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| 노드 | 역할 |
|---|---|
| **intake** | 사용자 질문을 받아 의도를 명확하게 한 문장으로 재정리 |
| **supervisor** | 정제된 질문을 분석해 `code` 또는 `text`로 분류하고 라우팅 결정 |
| **code_helper** | 코드·개발 관련 질문에 답변. `get_current_datetime` 툴 사용 가능 |
| **text_helper** | 일반 지식·설명 질문에 답변. `get_current_datetime` 툴 사용 가능 |

### 상태 흐름

```
AgentState
  query        ── intake가 정제 → supervisor·helper에서 읽기
  route        ── supervisor가 "code" / "text" 중 하나로 설정
  tool_result  ── helper가 툴을 호출했을 때 결과 저장
  final_answer ── helper가 작성한 최종 답변
  messages     ── 모든 노드의 메시지를 누적 (add_messages reducer)
```

### 라우팅 관리

분기 로직은 **`graph/routing.py`** 의 `route_from_supervisor` 함수 한 곳에서 관리합니다.

```python
# graph/routing.py
def route_from_supervisor(state: AgentState) -> str:
    if state["route"] == "code":
        return "code_helper"
    elif state["route"] == "text":
        return "text_helper"
    else:
        raise ValueError(f"Unknown route: {state['route']}")
```

이 함수를 `builder.py`의 `add_conditional_edges`에 넘기면 LangGraph가 supervisor 노드 실행 후 자동으로 호출해 다음 노드를 결정합니다. **새 분기 추가 시 여기에 `elif` 하나만 추가하면 됩니다.**

---

## 프로젝트 구조

```
agent-test/
├── agents/
│   ├── __init__.py
│   ├── tools.py            # get_current_datetime 툴 정의
│   ├── intake.py           # 질문 정제 노드
│   ├── supervisor.py       # 라우팅 분류 노드 (structured output)
│   ├── code_helper.py      # 코드 전담 답변 노드 (tool calling)
│   └── text_helper.py      # 일반 지식 답변 노드 (tool calling)
├── graph/
│   ├── __init__.py
│   ├── routing.py          # route_from_supervisor 라우팅 함수
│   ├── state.py            # 공유 상태 스키마 (AgentState)
│   └── builder.py          # 그래프 조립 (build_graph, 조건부 분기)
├── backend/
│   ├── __init__.py
│   ├── protocol.py         # 요청/응답 Pydantic 스키마
│   ├── exception.py        # 커스텀 예외 클래스
│   ├── dependencies.py     # FastAPI Depends 함수
│   └── routes/
│       └── run.py          # API 라우터 (/run, /run/stream)
├── config/
│   ├── __init__.py
│   ├── settings.py         # pydantic-settings 기반 전체 설정
│   └── llm_factory.py      # 모델명 기반 LLM 인스턴스 팩토리
├── examples/
│   └── client.py           # API 호출 예제 (일괄 + 토큰 스트리밍)
├── api.py                  # FastAPI 서버 진입점
├── main.py                 # CLI 실행 진입점 (토큰 스트리밍)
├── .env                    # 환경 변수 (git 제외)
└── .env.example            # 환경 변수 템플릿
```

---

## 설치

### uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 의존성 설치

```bash
# 서버 실행에 필요한 메인 의존성만 설치
uv sync

# 클라이언트 예제까지 포함해서 설치 (dev 그룹 — httpx 포함)
uv sync --group dev
```

---

## 환경 변수 설정

`.env.example`을 복사해서 `.env`를 만들고 API 키를 입력합니다.

```bash
cp .env.example .env
```

### 필수 항목

사용하는 provider의 API 키만 입력합니다.

```env
OPENAI_API_KEY=sk-...       # OpenAI 사용 시
GOOGLE_API_KEY=...          # Gemini 사용 시
```

### LLM provider 설정

provider는 **모델 이름으로 자동 감지**됩니다.

| 모델 이름 패턴 | provider | 비고 |
|---|---|---|
| `gemini-*` | Google Generative AI | `GOOGLE_API_KEY` 필요 |
| `gpt-*`, `o1-*`, `o3-*` 등 | OpenAI | `OPENAI_API_KEY` 필요 |
| 그 외 | vLLM / SGLang | `base_url` 필수 |

노드별로 다른 모델을 쓰고 싶다면 `.env`에서 설정합니다.

```env
# supervisor는 Gemini, helper들은 GPT-4o 사용 예시
AGENTS__SUPERVISOR__MODEL=gemini-2.0-flash
AGENTS__CODE_HELPER__MODEL=gpt-4o
AGENTS__TEXT_HELPER__MODEL=gpt-4o
AGENTS__TEXT_HELPER__TEMPERATURE=0.5
```

### vLLM / SGLang 로컬 모델 설정

```env
AGENTS__CODE_HELPER__MODEL=meta-llama/Llama-3.1-8B-Instruct
AGENTS__CODE_HELPER__BASE_URL=http://localhost:8001/v1
AGENTS__CODE_HELPER__API_KEY=EMPTY
```

vLLM/SGLang은 OpenAI-compatible API(`/v1/chat/completions`)를 지원하므로 `base_url`만 변경하면 동일하게 동작합니다.

### 앱 서버 설정 (선택)

```env
APP__RELOAD=true    # 개발 중 코드 변경 시 자동 재시작
APP__WORKERS=4      # 운영 환경 멀티프로세스 (reload=true면 사용 불가)
APP__PORT=8080
```

---

## 실행

### CLI로 직접 실행 (main.py)

토큰이 생성되는 즉시 출력합니다.

```bash
uv run python main.py
```

출력 예시:

```
============================================================
질문: 오늘 날짜를 포함해서 Python으로 현재 시간을 출력하는 코드를 작성해줘
============================================================


[INTAKE] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Python으로 현재 날짜와 시간을 출력하는 코드를 작성해 주세요.

[SUPERVISOR] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[라우팅] CODE — 코드 작성 요청입니다.

[CODE HELPER] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
현재 날짜와 시간은 2026년 03월 09일 14시 23분 05초입니다.
다음과 같이 작성할 수 있습니다: ...
```

### API 서버 실행 (api.py)

```bash
uv run python api.py
```

서버가 뜨면 `http://localhost:8000/docs`에서 Swagger UI로 API를 확인할 수 있습니다.

---

## API 엔드포인트

### POST /run — 결과 일괄 반환

파이프라인 전체가 완료된 후 결과를 한 번에 반환합니다.

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"query": "Python에서 데코레이터가 뭐야?"}'
```

`request_id`를 직접 지정할 수도 있습니다 (미입력 시 서버 자동 생성).

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"query": "블랙홀이 뭐야?", "request_id": "my-debug-id-001"}'
```

응답:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "블랙홀의 개념과 원리를 설명해 주세요.",
  "route": "text",
  "tool_result": "",
  "final_answer": "블랙홀은 중력이 너무 강해서 빛조차 탈출할 수 없는 천체입니다...",
  "status": "success",
  "execution_time": 4.21
}
```

### POST /run/stream — 토큰 단위 SSE 스트리밍

LLM이 토큰을 생성하는 즉시 SSE 이벤트로 전송합니다.

```bash
curl -X POST http://localhost:8000/run/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "오늘 날짜 포함해서 Python 코드 작성해줘"}'
```

SSE 이벤트 형식:

```
data: {"type": "node_start", "request_id": "...", "node": "intake"}

data: {"type": "token",      "request_id": "...", "node": "intake",       "token": "Python으로"}
...
data: {"type": "node_end",   "request_id": "...", "node": "intake"}

data: {"type": "node_start", "request_id": "...", "node": "supervisor"}
...
data: {"type": "node_end",   "request_id": "...", "node": "supervisor"}

data: {"type": "node_start", "request_id": "...", "node": "code_helper"}
...
data: {"type": "node_end",   "request_id": "...", "node": "code_helper"}

data: {"type": "done",       "request_id": "..."}
```

오류 발생 시:

```
data: {"type": "error", "request_id": "...", "error": "..."}
```

### Python 클라이언트 예제 실행

서버를 띄운 상태에서 별도 터미널에서 실행합니다.

```bash
uv run --group dev python examples/client.py
```

---

## 새 분기 노드 추가하는 법

`math_helper`를 추가하는 예시입니다.

### 1. `graph/routing.py` — 분기 조건 추가

```python
def route_from_supervisor(state: AgentState) -> str:
    if state["route"] == "code":
        return "code_helper"
    elif state["route"] == "text":
        return "text_helper"
    elif state["route"] == "math":   # 추가
        return "math_helper"         # 추가
    else:
        raise ValueError(f"Unknown route: {state['route']}")
```

### 2. `graph/state.py` — route 타입 확장

```python
route: Literal["code", "text", "math"]
```

### 3. `agents/math_helper.py` — 노드 구현

```python
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from graph.state import AgentState


def _to_str(content) -> str:
    """AIMessage.content가 list로 반환되는 경우(Gemini 등)를 단일 문자열로 정규화."""
    if isinstance(content, str):
        return content
    return "\n".join(part if isinstance(part, str) else part.get("text", "") for part in content)


class MathHelperNode:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def __call__(self, state: AgentState) -> dict:
        response = await self.llm.ainvoke([HumanMessage(content=state["query"])])
        content = _to_str(response.content)
        return {
            "final_answer": content,
            "messages": [AIMessage(content=content, name="math_helper")],
        }
```

### 4. `agents/__init__.py` — export 추가

```python
from .math_helper import MathHelperNode
```

### 5. `config/settings.py` — LLM 설정 추가

```python
class AgentConfig(BaseModel):
    ...
    math_helper: LLMConfig = LLMConfig()
```

### 6. `graph/builder.py` — 노드 등록 및 END 엣지 추가

```python
builder.add_node("math_helper", MathHelperNode(create_llm(agent_config.math_helper)))
builder.add_edge("math_helper", END)
```

### 7. `agents/supervisor.py` — 분류 프롬프트·타입 수정

`RouteDecision.route` 타입과 프롬프트에 새 값을 추가합니다.

```python
class RouteDecision(BaseModel):
    route: Literal["code", "text", "math"]
    reason: str
```

```python
prompt = (
    "... 수학·통계·공식 계산은 route='math'로, "
    "코드 관련은 route='code'로, 그 외는 route='text'로 분류하세요.\n\n"
    f"질문: {state['query']}"
)
```

### 8. `main.py` — 스트리밍 레이블 추가

```python
NODE_LABELS = {
    ...,
    "math_helper": "MATH HELPER",
}
```

### 9. `backend/routes/run.py` — 스트리밍 노드 추가

```python
_STREAM_NODES = {"intake", "supervisor", "code_helper", "text_helper", "math_helper"}
```

---

### 파일별 수정 범위 요약

| 파일 | 내용 |
|---|---|
| `graph/routing.py` | `elif` 분기 추가 |
| `graph/state.py` | `route` Literal 타입 확장 |
| `agents/math_helper.py` | 노드 로직 구현 |
| `agents/__init__.py` | export 추가 |
| `config/settings.py` | LLM 설정 추가 |
| `graph/builder.py` | `add_node` + `add_edge(END)` 두 줄 추가 |
| `agents/supervisor.py` | `RouteDecision` 타입 + 프롬프트 수정 |
| `main.py` | 스트리밍 레이블 추가 (선택) |
| `backend/routes/run.py` | 스트리밍 노드 추가 (선택) |
