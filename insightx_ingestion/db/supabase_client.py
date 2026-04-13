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
        "content_hash": article.content_hash,
        "img_url":      article.image_url,
    }


def _embedding_payload(article_id: str, article: EmbeddedArticle) -> dict[str, Any]:
    """Build article_embeddings row."""
    return {
        "article_id": article_id,
        "embedding":  article.embedding,
    }


def _pipeline_state_payload(article_id: str) -> dict[str, Any]:
    """Build initial article_pipeline_states row — all stages false."""
    return {
        "article_id":            article_id,
        "event_done":            False,
        "reasoning_done":        False,
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

CAT_MAP = {
    "general": "Global Trends",
    "world": "Global Trends",
    "business": "Economy",
    "technology": "Tech Innovation",
    "science": "Science",
    "health": "Lifestyle",
    "sports": "Sports",
    "entertainment": "Entertainment",
}

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

    # Insert enrichment payload to save category
    enrichment_payloads = []
    for article_id, article in id_map.items():
        mapped_cat = CAT_MAP.get((article.category or "general").lower(), "Global Trends")
        enrichment_payloads.append({
            "article_id": article_id,
            "categories": [mapped_cat],
        })
    if enrichment_payloads:
        def _insert_enrichment() -> None:
            supabase.table("articles_enriched").upsert(
                enrichment_payloads, on_conflict="article_id"
            ).execute()
        await asyncio.to_thread(_insert_enrichment)

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
        fetch_limit = 150 if category and category != "All" else limit
        q = (
            supabase.table("articles_raw")
            .select("id,title,url,source,published_at,articles_enriched(categories)")
            .order("published_at", desc=True)
            .limit(fetch_limit)
        )
        if source:
            q = q.eq("source", source)
        
        data = q.execute().data or []
        results = []
        def build_query(include_image: bool):
            sel = "id,title,url,source,published_at,articles_enriched(categories)"
            if include_image:
                sel = "id,title,url,source,published_at,img_url,articles_enriched(categories)"
            
            q = (
                supabase.table("articles_raw")
                .select(sel)
                .order("published_at", desc=True)
                .limit(limit)
            )
            if source:
                q = q.eq("source", source)
            return q

        try:
            data = build_query(include_image=True).execute().data or []
        except Exception as e:
            if "Could not find" in str(e) or "img_url" in str(e) or "image_url" in str(e):
                data = build_query(include_image=False).execute().data or []
            else:
                raise e
        for d in data:
            if d.get("articles_enriched"):
                categories = d["articles_enriched"].get("categories", [])
                if categories:
                    d["category"] = categories[0]
            if "articles_enriched" in d:
                del d["articles_enriched"]
                
            # Perform Python side filtering
            if category and category != "All":
                if d.get("category") != category:
                    continue
                    
            results.append(d)
            if len(results) >= limit:
                break
        return results

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

async def get_pending_articles(stage: str = "event_done", batch_size: int = 20) -> list[dict]:
    """
    Return article_ids where the given pipeline stage is not yet done.
    stage must be one of: event_done, reasoning_done
    """
    def _query() -> list[dict]:
        return (
            supabase.table("article_pipeline_states")
            .select("article_id")
            .eq(stage, False)
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
            "name": name,
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

async def log_user_article_interaction(user_id: str, article_id: str, profile_type: str, category: str, insight: dict) -> None:
    """Logs the article read event, caches the AI insight output, and updates topic history."""
    if not user_id or not article_id:
        return
        
    def _db_call() -> None:
        # 1. Upsert into insights cache
        insight_payload = {
            "article_id": article_id,
            "user_id": user_id,
            "profile_type": profile_type,
            "personalization_output": insight.get("profile_specific_insights", {}),
            "action_output": {"next_steps": insight.get("next_steps", []), "quiz": insight.get("quiz", [])},
            "prediction_output": {"future_predictions": insight.get("future_predictions", [])},
            "hallucination_score": 1.0, 
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        try:
            supabase.table("insights").upsert(insight_payload, on_conflict="article_id, user_id, profile_type").execute()
        except Exception as e:
            print(f"Failed to upsert insight: {e}")

        # 2. Insert into user_reading_history
        history_payload = {
            "user_id": user_id,
            "article_id": article_id,
            "completed": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        try:
            supabase.table("user_reading_history").insert(history_payload).execute()
        except Exception as e:
            print(f"Failed to insert user_reading_history: {e}")

        # 3. Upsert into user_topic_history (increment read_count)
        category_val = category
        if not category_val:
            try:
                art = supabase.table("articles_raw").select("category").eq("id", article_id).execute()
                if art.data and art.data[0].get("category"):
                    category_val = art.data[0]["category"]
            except Exception:
                pass

        if category_val:
            try:
                res = supabase.table("user_topic_history").select("read_count").eq("user_id", user_id).eq("topic", category_val).execute()
                current_count = 0
                if res.data:
                    current_count = res.data[0].get("read_count", 0)
                
                topic_payload = {
                    "user_id": user_id,
                    "topic": category_val,
                    "read_count": current_count + 1,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                supabase.table("user_topic_history").upsert(topic_payload, on_conflict="user_id, topic").execute()
            except Exception as e:
                print(f"Failed to update user_topic_history: {e}")

    await asyncio.to_thread(_db_call)

async def upsert_article_enrichment(article_id: str, insight: dict) -> None:
    def _db_call():
        # Preserve existing categories if they were assigned during ingestion
        try:
            existing = supabase.table("articles_enriched").select("categories").eq("article_id", article_id).execute()
            cats = existing.data[0].get("categories") if existing.data and existing.data[0].get("categories") else ["General"]
        except Exception:
            cats = ["General"]
            
        payload = {
            "article_id": article_id,
            "categories": cats,
            "entities": [],
            "sentiment": 0.0,
            "event_output": insight.get("event_context", {}),
            "reasoning_output": insight.get("cause_effect", {})
        }
        try:
            supabase.table("articles_enriched").upsert(payload, on_conflict="article_id").execute()
        except Exception as e:
            print(f"Failed to upsert articles_enriched: {e}")
    await asyncio.to_thread(_db_call)

async def mark_article_pipeline_success(article_id: str) -> None:
    def _db_call():
        payload = {
            "article_id": article_id,
            "event_done": True,
            "reasoning_done": True,
            "error": None
        }
        try:
            supabase.table("article_pipeline_states").upsert(payload, on_conflict="article_id").execute()
        except Exception as e:
            print(f"Failed to upsert article_pipeline_states: {e}")
    await asyncio.to_thread(_db_call)

async def upsert_article_embedding(article_id: str, embedding: list[float], model_used: str = "nomic-embed-text-v1_5") -> None:
    def _db_call():
        payload = {
            "article_id": article_id,
            "embedding": embedding
        }
        try:
            supabase.table("article_embeddings").upsert(payload, on_conflict="article_id").execute()
        except Exception as e:
            print(f"Failed to upsert article_embeddings: {e}")
    await asyncio.to_thread(_db_call)