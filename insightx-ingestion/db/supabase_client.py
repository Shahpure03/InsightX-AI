"""Supabase helpers for storing and retrieving ingested content."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from supabase import Client, create_client

from models.article import EmbeddedArticle, IngestionResult


def _require_env(name: str) -> str:
    """Return a required environment variable or raise a clear error."""

    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


SUPABASE_URL = _require_env("SUPABASE_URL")
SUPABASE_KEY = _require_env("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def _article_payload(article: EmbeddedArticle) -> dict[str, Any]:
    """Convert an embedded article model into a database payload."""

    return {
        "title": article.title,
        "content": article.content,
        "url": article.url,
        "source": article.source.value,
        "published_at": article.published_at.astimezone(timezone.utc).isoformat(),
        "author": article.author,
        "image_url": article.image_url,
        "category": article.category,
        "language": article.language,
        "country": article.country,
        "video_id": article.video_id,
        "thumbnail": article.thumbnail,
        "content_hash": article.content_hash,
        "embedding": article.embedding,
        "ingested_at": article.ingested_at.astimezone(timezone.utc).isoformat(),
    }


async def article_exists(content_hash: str) -> bool:
    """Return whether an article with the provided content hash already exists."""

    def _query() -> bool:
        response = (
            supabase.table("articles")
            .select("id")
            .eq("content_hash", content_hash)
            .limit(1)
            .execute()
        )
        return bool(response.data)

    return await asyncio.to_thread(_query)


async def insert_article(article: EmbeddedArticle) -> str:
    """Insert a single embedded article and return its inserted row id."""

    payload = _article_payload(article)

    def _insert() -> str:
        response = (
            supabase.table("articles")
            .upsert(
                payload,
                on_conflict="content_hash",
                ignore_duplicates=True,
            )
            .execute()
        )
        if response.data:
            return response.data[0]["id"]
        return ""

    return await asyncio.to_thread(_insert)


async def bulk_insert_articles(articles: list[EmbeddedArticle]) -> int:
    """Insert multiple embedded articles with conflict handling on content hash."""

    if not articles:
        return 0

    payloads = [_article_payload(article) for article in articles]

    def _insert_many() -> int:
        response = (
            supabase.table("articles")
            .upsert(
                payloads,
                on_conflict="content_hash",
                ignore_duplicates=True,
            )
            .execute()
        )
        return len(response.data or [])

    return await asyncio.to_thread(_insert_many)


async def log_ingestion_run(result: IngestionResult) -> None:
    """Persist a completed ingestion summary to the ingestion logs table."""

    payload = {
        "total_fetched": result.total_fetched,
        "duplicates_skipped": result.duplicates_skipped,
        "new_articles": result.new_articles,
        "sources_used": [source.value for source in result.sources_used],
        "errors": result.errors,
        "duration_seconds": result.duration_seconds,
    }

    def _insert_log() -> None:
        supabase.table("ingestion_logs").insert(payload).execute()

    await asyncio.to_thread(_insert_log)


async def semantic_search(
    query_embedding: list[float],
    threshold: float = 0.7,
    limit: int = 10,
    category: str | None = None,
    language: str = "en",
) -> list[dict]:
    """Execute the pgvector semantic search RPC and return matching rows."""

    payload = {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": limit,
        "filter_category": category,
        "filter_language": language,
    }

    def _search() -> list[dict]:
        response = supabase.rpc("search_articles", payload).execute()
        return response.data or []

    return await asyncio.to_thread(_search)


async def get_recent_articles(
    limit: int = 50,
    category: str | None = None,
    language: str = "en",
) -> list[dict]:
    """Return recent articles with optional category and language filters."""

    def _query() -> list[dict]:
        query = (
            supabase.table("articles")
            .select("*")
            .eq("language", language)
            .order("published_at", desc=True)
            .limit(limit)
        )
        if category:
            query = query.eq("category", category)
        response = query.execute()
        return response.data or []

    return await asyncio.to_thread(_query)


async def get_ingestion_logs(limit: int = 20) -> list[dict]:
    """Return the most recent ingestion log entries."""

    def _query() -> list[dict]:
        response = (
            supabase.table("ingestion_logs")
            .select("*")
            .order("run_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    return await asyncio.to_thread(_query)


async def get_article_by_id(article_id: str) -> dict | None:
    """Return a single article row by its UUID."""

    def _query() -> dict | None:
        response = (
            supabase.table("articles")
            .select("*")
            .eq("id", article_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    return await asyncio.to_thread(_query)


async def get_recent_articles_with_source(
    limit: int = 20,
    category: str | None = None,
    language: str = "en",
    source: str | None = None,
) -> list[dict]:
    """Return recent articles with optional category, language, and source filters."""

    def _query() -> list[dict]:
        query = (
            supabase.table("articles")
            .select("*")
            .eq("language", language)
            .order("published_at", desc=True)
            .limit(limit)
        )
        if category:
            query = query.eq("category", category)
        if source:
            query = query.eq("source", source)
        response = query.execute()
        return response.data or []

    return await asyncio.to_thread(_query)


async def delete_articles_older_than(older_than_days: int = 30) -> int:
    """Delete articles older than the provided age threshold and return the count."""

    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)

    def _delete() -> int:
        response = (
            supabase.table("articles")
            .delete()
            .lt("published_at", cutoff.isoformat())
            .execute()
        )
        return len(response.data or [])

    return await asyncio.to_thread(_delete)
