"""FastAPI entrypoint for the InsightX ingestion layer."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pipeline.ingestor import NewsIngestor
from pipeline.scheduler import start_scheduler
from routers.ingestion import router as ingestion_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize background ingestion tasks during the app lifespan."""

    ingestor = NewsIngestor()
    app.state.ingestor = ingestor
    initial_task = asyncio.create_task(ingestor.run_full_ingestion())
    scheduler_task = asyncio.create_task(start_scheduler(ingestor))
    app.state.initial_ingestion_task = initial_task
    app.state.scheduler_task = scheduler_task
    logger.info("InsightX ingestion layer started")
    yield
    initial_task.cancel()
    scheduler_task.cancel()
    await asyncio.gather(initial_task, scheduler_task, return_exceptions=True)


app = FastAPI(title="InsightX Ingestion Layer", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ingestion_router, prefix="/api/ingestion")


@app.get("/health")
async def health() -> dict:
    """Return a simple healthcheck payload."""

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
