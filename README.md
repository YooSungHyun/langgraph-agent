# H-FIT

LangGraph 기반 멀티 에이전트 시스템 (researcher → analyzer → writer)

## 환경 설정

### uv 설치

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 가상환경 생성 및 의존성 설치

```bash
# 가상환경 생성 + 의존성 설치 (pyproject.toml 기준)
uv sync
```

### 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 OpenAI API 키를 입력합니다.

```bash
OPENAI_API_KEY=sk-...
```

## 실행

```bash
uv run python main.py
```
