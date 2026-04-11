"""FastAPI routes for ingestion control and article retrieval."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from db.supabase_client import (
    delete_articles_older_than,
    get_article_by_id,
    get_ingestion_logs,
    get_recent_articles_with_source,
    semantic_search,
)

from pipeline.embedder import embed_text
from pipeline.ingestor import NewsIngestor

router = APIRouter()


class QueryIngestionRequest(BaseModel):
    """Request payload for on-demand query ingestion."""

    query: str = Field(..., min_length=1)
    language: str = "en"


def _get_ingestor(request: Request) -> NewsIngestor:
    """Return the shared ingestor instance stored on the FastAPI app state."""

    return request.app.state.ingestor


from datetime import datetime, timezone, timedelta
import os
import logging
from db.supabase_client import log_ingestion_run

logger = logging.getLogger(__name__)

@router.post("/trigger")
async def trigger_ingestion(request: Request) -> dict:
    """Manually trigger a full ingestion run, honoring rate limits."""
    
    interval = int(os.getenv("INGEST_INTERVAL_SECONDS", "3600"))
    logs = await get_ingestion_logs(limit=1)
    
    if logs:
        last_run = datetime.fromisoformat(logs[0]["run_at"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if (now - last_run).total_seconds() < interval:
            logger.info("Ingestion trigger skipped due to rate limit cooldown.")
            return {
                "status": "skipped",
                "reason": "rate_limited",
                "cooldown_seconds_remaining": interval - (now - last_run).total_seconds(),
                "last_run": last_run.isoformat()
            }
            
    result = await _get_ingestor(request).run_full_ingestion()
    await log_ingestion_run(result)
    
    data = result.model_dump()
    data["status"] = "success"
    return data


@router.post("/query")
async def trigger_query_ingestion(payload: QueryIngestionRequest, request: Request) -> dict:
    """Trigger an ingestion run for a specific query."""

    return (await _get_ingestor(request).run_query_ingestion(payload.query, payload.language)).model_dump()


@router.get("/logs")
async def fetch_logs(limit: int = Query(default=20, ge=1, le=100)) -> list[dict]:
    """Return recent ingestion log entries."""

    return await get_ingestion_logs(limit=limit)


@router.get("/articles")
async def fetch_articles(
    limit: int = Query(default=20, ge=1, le=100),
    category: str | None = None,
    language: str = "en",
    source: str | None = None,
) -> list[dict]:
    """Return recent stored articles using the provided filters."""

    return await get_recent_articles_with_source(
        limit=limit,
        category=category,
        language=language,
        source=source,
    )


@router.get("/articles/search")
async def search_articles(
    q: str,
    limit: int = Query(default=10, ge=1, le=50),
    threshold: float = Query(default=0.7, ge=0.0, le=1.0),
    category: str | None = None,
    language: str = "en",
) -> list[dict]:
    """Run semantic search over stored articles using a natural-language query."""

    query_embedding = await embed_text(q)
    return await semantic_search(
        query_embedding=query_embedding,
        threshold=threshold,
        limit=limit,
        category=category,
        language=language,
    )


@router.get("/articles/{article_id}")
async def fetch_article(article_id: UUID) -> dict:
    """Return a single article by its UUID."""

    article = await get_article_by_id(str(article_id))
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/articles/old")
async def delete_old_articles(older_than_days: int = Query(default=30, ge=1)) -> dict:
    """Delete stored articles older than the provided day threshold."""

    deleted = await delete_articles_older_than(older_than_days=older_than_days)
    return {"deleted": deleted}
