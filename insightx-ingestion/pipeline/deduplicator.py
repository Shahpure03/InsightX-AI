"""Deduplication helpers for ingestion batches."""

from __future__ import annotations

import asyncio
from hashlib import sha256

from db.supabase_client import article_exists
from models.article import RawArticle


def compute_hash(article: RawArticle) -> str:
    """Compute the canonical article content hash used across the pipeline."""

    normalized = f"{article.title.strip().lower()}{article.content[:200]}"
    return sha256(normalized.encode("utf-8")).hexdigest()


async def filter_new_articles(articles: list[RawArticle]) -> tuple[list[RawArticle], int]:
    """Filter out articles that already exist in the database."""

    hashes = [compute_hash(article) for article in articles]
    exists_results = await asyncio.gather(*(article_exists(content_hash) for content_hash in hashes))
    new_articles = [article for article, exists in zip(articles, exists_results, strict=True) if not exists]
    duplicates_skipped = sum(1 for exists in exists_results if exists)
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
