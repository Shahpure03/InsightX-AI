"""Pydantic models for InsightX ingestion entities."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class ArticleSource(str, Enum):
    """Supported upstream article providers."""

    NEWSAPI = "newsapi"
    GNEWS = "gnews"
    LIVE_NEWS = "live_news"
    YOUTUBE = "youtube"


class RawArticle(BaseModel):
    """Normalized article payload fetched from an upstream source."""

    title: str
    content: str
    url: str
    source: ArticleSource
    published_at: datetime
    author: str | None = None
    image_url: str | None = None
    category: str | None = None
    language: str = "en"
    country: str | None = None
    video_id: str | None = None
    thumbnail: str | None = None


class EmbeddedArticle(RawArticle):
    """Article payload enriched with an embedding vector."""

    embedding: list[float]
    content_hash: str
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IngestionResult(BaseModel):
    """Summary of a completed ingestion run."""

    total_fetched: int
    duplicates_skipped: int
    new_articles: int
    sources_used: list[ArticleSource]
    errors: list[str] = Field(default_factory=list)
    duration_seconds: float
