from typing import Any, Optional

from fastapi import HTTPException


class AgentException(Exception):

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class GraphBuildException(AgentException):
    pass


class GraphInvokeException(AgentException):
    pass


def agent_exception_handler(exc: AgentException) -> HTTPException:

    status_code = 500

    if isinstance(exc, GraphBuildException):
        status_code = 503
    elif isinstance(exc, GraphInvokeException):
        status_code = 500

    return HTTPException(
        status_code=status_code,
        detail={"error": exc.__class__.__name__, "message": exc.message, "details": exc.details},
    )
