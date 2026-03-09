import logging
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from backend import AgentException, agent_exception_handler, run_router
from config import get_settings
from graph import build_graph

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Building agent graph...")
    app.state.graph = build_graph()
    logger.info("Startup completed successfully")
    yield
    logger.info("Shutdown completed successfully")


app = FastAPI(title="Supervisor Agent API", lifespan=lifespan)
app.include_router(run_router)


@app.exception_handler(AgentException)
async def handle_agent_exception(request, exc: AgentException):
    http_exc = agent_exception_handler(exc)
    return JSONResponse(status_code=http_exc.status_code, content=http_exc.detail)


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "api:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
        workers=settings.app.workers,
    )
