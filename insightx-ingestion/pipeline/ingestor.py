"""Ingestion orchestrator for combining, deduplicating, embedding, and storing news."""

from __future__ import annotations

import asyncio
import logging
import time

from db.supabase_client import bulk_insert_articles
from ingestion.gnews import GNewsClient
from ingestion.live_news import LiveNewsClient
from ingestion.newsapi import NewsAPIClient
from models.article import ArticleSource, IngestionResult, RawArticle
from pipeline.deduplicator import deduplicate_within_batch, filter_new_articles
from pipeline.embedder import embed_articles_batch

logger = logging.getLogger(__name__)

ALL_CATEGORIES = [
    "general",
    "world",
    "business",
    "technology",
    "science",
    "health",
    "sports",
    "entertainment",
]


class NewsIngestor:
    """Coordinates fetching from all upstream providers and persisting results."""

    def __init__(self) -> None:
        """Instantiate all upstream source clients."""

        self.newsapi = NewsAPIClient()
        self.gnews = GNewsClient()
        self.live_news = LiveNewsClient()

    async def run_full_ingestion(self) -> IngestionResult:
        """Run the full multi-source ingestion pipeline."""

        start = time.perf_counter()
        errors: list[str] = []
        sources_used: set[ArticleSource] = set()

        tasks = {
            "newsapi_india": self.newsapi.fetch_india_news(),
            "newsapi_world": self.newsapi.fetch_everything(query="world news"),
            "gnews_categories": self.gnews.fetch_by_categories(ALL_CATEGORIES),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        collected: dict[str, list[RawArticle]] = {}
        for name, result in zip(tasks.keys(), results, strict=True):
            if isinstance(result, Exception):
                logger.exception("Ingestion task %s failed", name, exc_info=result)
                errors.append(f"{name}: {result}")
                collected[name] = []
                continue
            collected[name] = result
            for article in result:
                sources_used.add(article.source)

        newsapi_total = len(collected["newsapi_india"]) + len(collected["newsapi_world"])
        if newsapi_total < 5:
            fallback_tasks = {
                "live_latest": self.live_news.fetch_latest(),
                "live_breaking": self.live_news.fetch_breaking(),
            }
            fallback_results = await asyncio.gather(*fallback_tasks.values(), return_exceptions=True)
            for name, result in zip(fallback_tasks.keys(), fallback_results, strict=True):
                if isinstance(result, Exception):
                    logger.exception("Fallback ingestion task %s failed", name, exc_info=result)
                    errors.append(f"{name}: {result}")
                    collected[name] = []
                    continue
                collected[name] = result
                for article in result:
                    sources_used.add(article.source)

        flat_articles = [article for batch in collected.values() for article in batch]
        total_fetched = len(flat_articles)
        batch_deduplicated = deduplicate_within_batch(flat_articles)
        new_articles, duplicates_skipped = await filter_new_articles(batch_deduplicated)
        embedded_articles = await embed_articles_batch(new_articles)
        inserted_count = await bulk_insert_articles(embedded_articles)
        duration = time.perf_counter() - start

        return IngestionResult(
            total_fetched=total_fetched,
            duplicates_skipped=duplicates_skipped + (len(flat_articles) - len(batch_deduplicated)),
            new_articles=inserted_count,
            sources_used=sorted(sources_used, key=lambda source: source.value),
            errors=errors,
            duration_seconds=round(duration, 3),
        )

    async def run_query_ingestion(self, query: str, language: str = "en") -> IngestionResult:
        """Run a targeted ingestion pipeline for a single query."""

        start = time.perf_counter()
        errors: list[str] = []
        sources_used: set[ArticleSource] = set()

        tasks = {
            "newsapi_query": self.newsapi.fetch_everything(query=query, language=language),
            "gnews_query": self.gnews.fetch_search(query=query, language=language),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        collected: list[RawArticle] = []
        for name, result in zip(tasks.keys(), results, strict=True):
            if isinstance(result, Exception):
                logger.exception("Query ingestion task %s failed", name, exc_info=result)
                errors.append(f"{name}: {result}")
                continue
            collected.extend(result)
            for article in result:
                sources_used.add(article.source)

        total_fetched = len(collected)
        batch_deduplicated = deduplicate_within_batch(collected)
        new_articles, duplicates_skipped = await filter_new_articles(batch_deduplicated)
        embedded_articles = await embed_articles_batch(new_articles)
        inserted_count = await bulk_insert_articles(embedded_articles)
        duration = time.perf_counter() - start

        return IngestionResult(
            total_fetched=total_fetched,
            duplicates_skipped=duplicates_skipped + (len(collected) - len(batch_deduplicated)),
            new_articles=inserted_count,
            sources_used=sorted(sources_used, key=lambda source: source.value),
            errors=errors,
            duration_seconds=round(duration, 3),
        )
