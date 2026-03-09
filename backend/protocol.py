from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    query: str = Field(description="처리할 질문 또는 요청")
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="요청 ID (미입력 시 서버 자동 생성)")


class StreamRunRequest(BaseModel):
    query: str = Field(description="처리할 질문 또는 요청")
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="요청 ID (미입력 시 서버 자동 생성)")


class RunResponse(BaseModel):
    request_id: str = Field(description="요청 ID")
    query: str = Field(description="정제된 질문")
    route: str = Field(description="supervisor 라우팅 결과 (code | text)")
    tool_result: str = Field(description="툴 호출 결과 (없으면 빈 문자열)")
    final_answer: str = Field(description="최종 답변")
    status: Literal["success", "error"] = Field(description="처리 상태")
    execution_time: float = Field(description="실행 시간 (초)")
