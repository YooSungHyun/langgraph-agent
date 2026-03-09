from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    base_url: str | None = None   # vLLM / SGLang 엔드포인트 (로컬 모델 사용 시)
    api_key: str | None = None    # 로컬 서버용 더미 키 (기본 "EMPTY")


class AgentConfig(BaseModel):
    intake: LLMConfig = LLMConfig()
    supervisor: LLMConfig = LLMConfig()
    code_helper: LLMConfig = LLMConfig()
    text_helper: LLMConfig = LLMConfig(temperature=0.3)


class AppConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1


class Settings(BaseSettings):
    app: AppConfig = AppConfig()
    agents: AgentConfig = AgentConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
