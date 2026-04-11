"""Async client for GNews."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone

import httpx

from models.article import ArticleSource, RawArticle

logger = logging.getLogger(__name__)


def _parse_datetime(value: str | None) -> datetime:
    """Parse an upstream datetime string into a timezone-aware UTC datetime."""

    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class GNewsClient:
    """Client for fetching articles from GNews."""

    def __init__(self) -> None:
        """Initialize the GNews client from environment configuration."""

        self.api_key = os.getenv("GNEWS_API_KEY", "")
        self.base_url = "https://gnews.io/api/v4"

    def _map_article(self, article: dict, category: str | None = None) -> RawArticle | None:
        """Convert a GNews article payload into a normalized RawArticle."""

        title = article.get("title")
        description = article.get("description") or article.get("content") or ""
        if not title or not description:
            return None
        source_info = article.get("source") or {}
        return RawArticle(
            title=title.strip(),
            content=description.strip(),
            url=article.get("url", "").strip(),
            source=ArticleSource.GNEWS,
            published_at=_parse_datetime(article.get("publishedAt")),
            author=source_info.get("name"),
            image_url=article.get("image"),
            category=category,
            language=language if (language := article.get("lang")) else "en",
            country=article.get("country"),
        )

    async def fetch_top(
        self,
        category: str = "general",
        country: str = "in",
        language: str = "en",
        max_results: int = 50,
    ) -> list[RawArticle]:
        """Fetch top headlines from GNews."""

        params = {
            "category": category,
            "country": country,
            "lang": language,
            "max": max_results,
            "token": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/top-headlines", params=params)
                response.raise_for_status()
            payload = response.json()
            return [
                mapped
                for item in payload.get("articles", [])
                if (mapped := self._map_article(item, category=category)) and mapped.url
            ]
        except httpx.HTTPError as exc:
            logger.error("GNews top-headlines fetch failed for category '%s': %s", category, exc)
            return []

    async def fetch_search(
        self,
        query: str,
        language: str = "en",
        max_results: int = 50,
    ) -> list[RawArticle]:
        """Fetch query-based results from GNews."""

        params = {
            "q": query,
            "lang": language,
            "max": max_results,
            "token": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
            payload = response.json()
            return [
                mapped
                for item in payload.get("articles", [])
                if (mapped := self._map_article(item)) and mapped.url
            ]
        except httpx.HTTPError as exc:
            logger.error("GNews search failed for query '%s': %s", query, exc)
            return []

    async def fetch_by_categories(self, categories: list[str]) -> list[RawArticle]:
        """Fetch top headlines for multiple categories concurrently."""

        results = await asyncio.gather(*(self.fetch_top(category=category) for category in categories))
        return [article for batch in results for article in batch]
