"""Async client for YouTube news video discovery."""

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


class YouTubeNewsClient:
    """Client for searching news videos on YouTube Data API v3."""

    def __init__(self) -> None:
        """Initialize the YouTube client from environment configuration."""

        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def _map_video(self, item: dict) -> RawArticle | None:
        """Convert a YouTube search result item into a normalized RawArticle."""

        snippet = item.get("snippet") or {}
        video_id = (item.get("id") or {}).get("videoId")
        title = snippet.get("title")
        description = snippet.get("description") or ""
        if not video_id or not title:
            return None
        thumbnails = snippet.get("thumbnails") or {}
        thumbnail = (
            (thumbnails.get("high") or {}).get("url")
            or (thumbnails.get("medium") or {}).get("url")
            or (thumbnails.get("default") or {}).get("url")
        )
        return RawArticle(
            title=title.strip(),
            content=description.strip(),
            url=f"https://youtube.com/watch?v={video_id}",
            source=ArticleSource.YOUTUBE,
            published_at=_parse_datetime(snippet.get("publishedAt")),
            author=snippet.get("channelTitle"),
            image_url=thumbnail,
            category="news",
            language=snippet.get("defaultLanguage") or "en",
            country=None,
            video_id=video_id,
            thumbnail=thumbnail,
        )

    async def search_news_videos(
        self,
        query: str = "news today India",
        max_results: int = 20,
        published_after: datetime | None = None,
    ) -> list[RawArticle]:
        """Search for recent news videos on YouTube."""

        params = {
            "part": "snippet",
            "type": "video",
            "videoCategoryId": "25",
            "order": "date",
            "maxResults": max_results,
            "q": query,
            "key": self.api_key,
        }
        if published_after is not None:
            params["publishedAfter"] = published_after.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
            payload = response.json()
            return [mapped for item in payload.get("items", []) if (mapped := self._map_video(item))]
        except httpx.HTTPError as exc:
            logger.error("YouTube news search failed for query '%s': %s", query, exc)
            return []

    async def fetch_live_news_streams(self) -> list[RawArticle]:
        """Fetch currently live news streams from YouTube."""

        params = {
            "part": "snippet",
            "type": "video",
            "videoCategoryId": "25",
            "order": "date",
            "maxResults": 20,
            "q": "live news",
            "eventType": "live",
            "key": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
            payload = response.json()
            return [mapped for item in payload.get("items", []) if (mapped := self._map_video(item))]
        except httpx.HTTPError as exc:
            logger.error("YouTube live news search failed: %s", exc)
            return []
