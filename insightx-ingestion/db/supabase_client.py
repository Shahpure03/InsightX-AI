"""Supabase helpers — updated for split article_embeddings + archive pattern."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any

from supabase import Client, create_client

from models.article import EmbeddedArticle, IngestionResult
from config import config

if not config.SUPABASE_URL or not config.SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE credentials in .env")

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


# ──────────────────────────────────────────────
# PAYLOAD BUILDERS
# ──────────────────────────────────────────────

def _article_payload(article: EmbeddedArticle) -> dict[str, Any]:
    """Build articles_raw row — embedding NOT included (lives in article_embeddings)."""
    return {
        "title":        article.title,
        "content":      article.content,
        "url":          article.url,
        "source":       article.source.value,
        "published_at": article.published_at.astimezone(timezone.utc).isoformat(),
        "author":       article.author,
        "image_url":    article.image_url,
        "category":     article.category,
        "language":     article.language,
        "country":      article.country,
        "video_id":     article.video_id,
        "thumbnail":    article.thumbnail,
        "content_hash": article.content_hash,
        "ingested_at":  article.ingested_at.astimezone(timezone.utc).isoformat(),
        "status":       "active",
    }


def _embedding_payload(article_id: str, article: EmbeddedArticle) -> dict[str, Any]:
    """Build article_embeddings row."""
    return {
        "article_id": article_id,
        "embedding":  article.embedding,
        "model_used": os.getenv("EMBEDDING_MODEL", "nomic-embed-text-v1_5"),
    }


def _pipeline_state_payload(article_id: str) -> dict[str, Any]:
    """Build initial article_pipeline_states row — all stages false."""
    return {
        "article_id":            article_id,
        "event_extracted":       False,
        "reasoning_done":        False,
        "enrichment_done":       False,
        "action_template_done":  False,
        "prediction_done":       False,
        "retry_count":           0,
    }


# ──────────────────────────────────────────────
# DEDUPLICATION — BULK (replaces N individual round-trips)
# ──────────────────────────────────────────────

async def filter_existing_hashes(content_hashes: list[str]) -> set[str]:
    """
    Return the set of hashes that already exist in articles_raw.
    Single DB round-trip using IN clause — replaces N individual article_exists() calls.
    """
    if not content_hashes:
        return set()

    def _query() -> set[str]:
        response = (
            supabase.table("articles_raw")
            .select("content_hash")
            .in_("content_hash", content_hashes)
            .execute()
        )
        return {row["content_hash"] for row in (response.data or [])}

    return await asyncio.to_thread(_query)


# Keep for backward compatibility with deduplicator.py
async def article_exists(content_hash: str) -> bool:
    """Single-hash check — prefer filter_existing_hashes() for batches."""
    existing = await filter_existing_hashes([content_hash])
    return content_hash in existing


# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

async def bulk_insert_articles(articles: list[EmbeddedArticle]) -> int:
    """
    Insert articles_raw rows, then article_embeddings, then pipeline state rows.
    Returns count of newly inserted articles.
    """
    if not articles:
        return 0

    article_payloads = [_article_payload(a) for a in articles]

    def _insert_articles() -> list[dict]:
        response = (
            supabase.table("articles_raw")
            .upsert(article_payloads, on_conflict="content_hash", ignore_duplicates=True)
            .execute()
        )
        return response.data or []

    inserted_rows = await asyncio.to_thread(_insert_articles)
    inserted_count = len(inserted_rows)

    if not inserted_rows:
        return 0

    # Build id → article map by matching content_hash
    id_map: dict[str, EmbeddedArticle] = {}
    hash_to_article = {a.content_hash: a for a in articles}
    for row in inserted_rows:
        article = hash_to_article.get(row.get("content_hash", ""))
        if article:
            id_map[row["id"]] = article

    # Insert embeddings
    embedding_payloads = [
        _embedding_payload(article_id, article)
        for article_id, article in id_map.items()
    ]
    if embedding_payloads:
        def _insert_embeddings() -> None:
            supabase.table("article_embeddings").upsert(
                embedding_payloads, on_conflict="article_id", ignore_duplicates=True
            ).execute()
        await asyncio.to_thread(_insert_embeddings)

    # Insert pipeline state rows
    state_payloads = [_pipeline_state_payload(article_id) for article_id in id_map]
    if state_payloads:
        def _insert_states() -> None:
            supabase.table("article_pipeline_states").upsert(
                state_payloads, on_conflict="article_id", ignore_duplicates=True
            ).execute()
        await asyncio.to_thread(_insert_states)

    return inserted_count


# ──────────────────────────────────────────────
# READS
# ──────────────────────────────────────────────

async def get_recent_articles(
    limit: int = 50,
    category: str | None = None,
    language: str = "en",
    source: str | None = None,
) -> list[dict]:
    def _query() -> list[dict]:
        q = (
            supabase.table("articles_raw")
            .select("id,title,url,source,published_at")
            .order("published_at", desc=True)
            .limit(limit)
        )
        if source:
            q = q.eq("source", source)
        return q.execute().data or []

    return await asyncio.to_thread(_query)


async def get_recent_articles_with_source(
    limit: int = 20,
    category: str | None = None,
    language: str = "en",
    source: str | None = None,
) -> list[dict]:
    return await get_recent_articles(limit=limit, category=category, language=language, source=source)


async def get_article_by_id(article_id: str) -> dict | None:
    def _query() -> dict | None:
        response = (
            supabase.table("articles_raw")
            .select("*")
            .eq("id", article_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    return await asyncio.to_thread(_query)


async def semantic_search(
    query_embedding: list[float],
    threshold: float = 0.7,
    limit: int = 10,
    category: str | None = None,
    language: str = "en",
    active_only: bool = True,           # False = search archive too (historical analogy)
) -> list[dict]:
    """Execute the pgvector semantic search RPC."""
    payload = {
        "query_embedding":  query_embedding,
        "match_threshold":  threshold,
        "match_count":      limit,
        "filter_category":  category,
        "filter_language":  language,
        "active_only":      active_only,
    }

    def _search() -> list[dict]:
        return supabase.rpc("search_articles", payload).execute().data or []

    return await asyncio.to_thread(_search)


# ──────────────────────────────────────────────
# PIPELINE STATE HELPERS
# ──────────────────────────────────────────────

async def get_pending_articles(stage: str = "event_extracted", batch_size: int = 20) -> list[dict]:
    """
    Return article_ids where the given pipeline stage is not yet done.
    stage must be one of: event_extracted, reasoning_done, enrichment_done,
                          action_template_done, prediction_done
    """
    def _query() -> list[dict]:
        return (
            supabase.table("article_pipeline_states")
            .select("article_id")
            .eq(stage, False)
            .lt("retry_count", 3)
            .order("last_processed_at", desc=False, nullsfirst=True)
            .limit(batch_size)
            .execute()
            .data or []
        )

    return await asyncio.to_thread(_query)


async def mark_pipeline_stage(article_id: str, stage: str, error: str | None = None) -> None:
    """Mark a pipeline stage as complete (or failed) for an article."""
    payload: dict[str, Any] = {
        "last_processed_at": datetime.now(timezone.utc).isoformat(),
    }
    if error:
        payload["error"] = error
        payload["retry_count"] = supabase.rpc(
            "increment_retry", {"p_article_id": article_id}
        )  # handled DB-side or read-then-write
    else:
        payload[stage] = True
        payload["error"] = None

    def _update() -> None:
        supabase.table("article_pipeline_states").update(payload).eq("article_id", article_id).execute()

    await asyncio.to_thread(_update)


# ──────────────────────────────────────────────
# ARCHIVE — replaces delete_articles_older_than()
# ──────────────────────────────────────────────

async def run_archive_job(older_than_days: int = 7) -> int:
    """
    Archive articles older than older_than_days.
    Calls the run_archive_job() SQL function which:
      1. Snapshots rows to article_archive
      2. Flips status to 'archived'
      3. Does NOT touch article_embeddings (vectors survive)
    Returns count of archived articles.
    """
    def _archive() -> int:
        response = supabase.rpc("run_archive_job", {"older_than_days": older_than_days}).execute()
        return response.data or 0

    return await asyncio.to_thread(_archive)


async def delete_articles_older_than(older_than_days: int = 30) -> int:
    """Backwards-compatible wrapper for the old delete endpoint."""
    return await run_archive_job(older_than_days)


# ──────────────────────────────────────────────
# LOGS
# ──────────────────────────────────────────────

async def log_ingestion_run(result: IngestionResult) -> None:
    payload = {
        "total_fetched":      result.total_fetched,
        "duplicates_skipped": result.duplicates_skipped,
        "new_articles":       result.new_articles,
        "sources_used":       [s.value for s in result.sources_used],
        "errors":             result.errors,
        "duration_seconds":   result.duration_seconds,
    }

    def _insert() -> None:
        supabase.table("ingestion_logs").insert(payload).execute()

    await asyncio.to_thread(_insert)


async def get_ingestion_logs(limit: int = 20) -> list[dict]:
    def _query() -> list[dict]:
        return (
            supabase.table("ingestion_logs")
            .select("*")
            .order("run_at", desc=True)
            .limit(limit)
            .execute()
            .data or []
        )

    return await asyncio.to_thread(_query)

# ──────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────

async def create_or_update_user(email: str, name: str, role: str, interests: list[str]) -> dict:
    """Creates a user or updates them if they exist."""
    
    def _db_call() -> dict:
        # 1. Upsert into users table
        user_payload = {
            "email": email,
            # "display_name": name, # Temporarily bypassed to prevent PGRST204 schema cache error
            "active_profile": role
        }
        res = supabase.table("users").upsert(user_payload, on_conflict="email").execute()
        user_row = res.data[0]
        user_id = user_row["id"]
        
        # 2. Upsert into user_interest_profiles
        profile_payload = {
            "user_id": user_id,
            "profile_type": role,
            "selected_topics": interests
        }
        # Note: on_conflict requires unique index constraint `user_id, profile_type`.
        prof_res = supabase.table("user_interest_profiles").upsert(
            profile_payload, on_conflict="user_id, profile_type"
        ).execute()
        
        return user_row
        
    return await asyncio.to_thread(_db_call)