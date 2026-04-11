"""Async client for NewsAPI.org."""

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


class NewsAPIClient:
    """Client for fetching articles from NewsAPI."""

    def __init__(self) -> None:
        """Initialize the NewsAPI client from environment configuration."""

        self.api_key = os.getenv("NEWSAPI_KEY", "")
        self.base_url = "https://newsapi.org/v2"

    def _map_article(self, article: dict, category: str | None = None) -> RawArticle | None:
        """Convert a NewsAPI article payload into a normalized RawArticle."""

        title = article.get("title")
        content = article.get("content")
        if not title or content in (None, "", "[Removed]"):
            return None
        source_info = article.get("source") or {}
        return RawArticle(
            title=title.strip(),
            content=content.strip(),
            url=article.get("url", "").strip(),
            source=ArticleSource.NEWSAPI,
            published_at=_parse_datetime(article.get("publishedAt")),
            author=article.get("author"),
            image_url=article.get("urlToImage"),
            category=category,
            language="en",
            country=source_info.get("country"),
        )

    async def fetch_top_headlines(
        self,
        country: str = "in",
        category: str | None = None,
        page_size: int = 50,
    ) -> list[RawArticle]:
        """Fetch top headlines from NewsAPI."""

        params = {
            "country": country,
            "category": category,
            "pageSize": page_size,
            "apiKey": self.api_key,
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
            logger.error("NewsAPI top-headlines fetch failed: %s", exc)
            return []

    async def fetch_everything(
        self,
        query: str,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 50,
    ) -> list[RawArticle]:
        """Fetch articles from the NewsAPI everything endpoint."""

        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "apiKey": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/everything", params=params)
                response.raise_for_status()
            payload = response.json()
            return [
                mapped
                for item in payload.get("articles", [])
                if (mapped := self._map_article(item)) and mapped.url
            ]
        except httpx.HTTPError as exc:
            logger.error("NewsAPI everything fetch failed for query '%s': %s", query, exc)
            return []

    async def fetch_india_news(self) -> list[RawArticle]:
        """Fetch India-focused headlines and search results, deduplicated by URL."""

        top_headlines, india_search = await asyncio.gather(
            self.fetch_top_headlines(country="in"),
            self.fetch_everything(query="India", language="en"),
        )
        seen_urls: set[str] = set()
        combined: list[RawArticle] = []
        for article in [*top_headlines, *india_search]:
            if article.url in seen_urls:
                continue
            seen_urls.add(article.url)
            combined.append(article)
        return combined
