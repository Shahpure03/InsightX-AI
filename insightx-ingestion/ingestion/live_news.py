"""Async fallback client for the Live News API."""

from __future__ import annotations

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


class LiveNewsClient:
    """Client for the Live News API fallback source."""

    def __init__(self) -> None:
        """Initialize the Live News client from environment configuration."""

        self.api_key = os.getenv("LIVE_NEWS_API_KEY", "")
        self.base_url = "https://live-news-api.tk.gg/api/v1"

    def _map_article(self, article: dict, category: str | None = None) -> RawArticle | None:
        """Convert a Live News API payload into a normalized RawArticle."""

        title = article.get("title")
        content = article.get("content") or article.get("description") or ""
        if not title or not content:
            return None
        return RawArticle(
            title=title.strip(),
            content=content.strip(),
            url=article.get("url", "").strip(),
            source=ArticleSource.LIVE_NEWS,
            published_at=_parse_datetime(article.get("publishedAt") or article.get("published_at")),
            author=article.get("author"),
            image_url=article.get("image") or article.get("image_url"),
            category=article.get("category") or category,
            language=article.get("language", "en"),
            country=article.get("country"),
        )

    async def fetch_latest(
        self,
        category: str | None = None,
        language: str = "en",
        limit: int = 50,
    ) -> list[RawArticle]:
        """Fetch the latest articles from the Live News API."""

        params = {
            "category": category,
            "language": language,
            "limit": limit,
            "apikey": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/news", params=params)
                response.raise_for_status()
            payload = response.json()
            items = payload.get("articles") or payload.get("data") or []
            return [
                mapped
                for item in items
                if (mapped := self._map_article(item, category=category)) and mapped.url
            ]
        except httpx.HTTPError as exc:
            logger.warning("Live News latest fetch failed: %s", exc)
            return []

    async def fetch_breaking(self) -> list[RawArticle]:
        """Fetch breaking-news entries from the Live News API."""

        params = {"apikey": self.api_key}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/breaking", params=params)
                response.raise_for_status()
            payload = response.json()
            items = payload.get("articles") or payload.get("data") or []
            return [mapped for item in items if (mapped := self._map_article(item)) and mapped.url]
        except httpx.HTTPError as exc:
            logger.warning("Live News breaking fetch failed: %s", exc)
            return []
