from langchain_core.language_models import BaseChatModel

from config.settings import LLMConfig

# 모델 이름 prefix로 provider를 자동 감지한다.
_GOOGLE_PREFIXES = ("gemini-",)
_OPENAI_PREFIXES = ("gpt-", "o1-", "o3-", "o4-")


def _detect_provider(model: str) -> str:
    for prefix in _GOOGLE_PREFIXES:
        if model.startswith(prefix):
            return "google"
    for prefix in _OPENAI_PREFIXES:
        if model.startswith(prefix):
            return "openai"
    return "local"  # vLLM / SGLang 등 OpenAI-compatible 로컬 서버


def create_llm(cfg: LLMConfig) -> BaseChatModel:
    """모델 이름에서 provider를 자동 감지해 LLM 인스턴스를 생성한다.

    - gemini-*        → ChatGoogleGenerativeAI
    - gpt-* / o1-* 등 → ChatOpenAI (OpenAI)
    - 그 외           → ChatOpenAI (base_url로 vLLM / SGLang 연결)
    """
    provider = _detect_provider(cfg.model)

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=cfg.model, temperature=cfg.temperature)

    # openai 또는 local (vLLM / SGLang) — 둘 다 ChatOpenAI로 처리
    from langchain_openai import ChatOpenAI

    kwargs: dict = {"model": cfg.model, "temperature": cfg.temperature}
    if cfg.base_url:
        kwargs["base_url"] = cfg.base_url
        kwargs["api_key"] = cfg.api_key or "EMPTY"
    elif cfg.api_key:
        kwargs["api_key"] = cfg.api_key

    return ChatOpenAI(**kwargs)
