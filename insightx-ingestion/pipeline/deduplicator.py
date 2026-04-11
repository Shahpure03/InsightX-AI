"""Deduplication helpers — updated to use bulk hash check (single DB round-trip)."""

from __future__ import annotations

from hashlib import sha256

from db.supabase_client import filter_existing_hashes
from models.article import RawArticle


def compute_hash(article: RawArticle) -> str:
    """Compute the canonical article content hash used across the pipeline."""
    normalized = f"{article.title.strip().lower()}{article.content[:200]}"
    return sha256(normalized.encode("utf-8")).hexdigest()


async def filter_new_articles(articles: list[RawArticle]) -> tuple[list[RawArticle], int]:
    """
    Filter out articles that already exist in the database.
    CHANGED: single bulk SELECT WHERE content_hash = ANY(...) instead of N round-trips.
    """
    if not articles:
        return [], 0

    hashes = [compute_hash(article) for article in articles]
    existing_hashes = await filter_existing_hashes(hashes)

    new_articles = [
        article for article, h in zip(articles, hashes)
        if h not in existing_hashes
    ]
    duplicates_skipped = len(articles) - len(new_articles)
    return new_articles, duplicates_skipped


def deduplicate_within_batch(articles: list[RawArticle]) -> list[RawArticle]:
    """Remove duplicates within a fetched batch by URL and content hash."""
    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()
    deduplicated: list[RawArticle] = []
    for article in articles:
        content_hash = compute_hash(article)
        if article.url in seen_urls or content_hash in seen_hashes:
            continue
        seen_urls.add(article.url)
        seen_hashes.add(content_hash)
        deduplicated.append(article)
    return deduplicated