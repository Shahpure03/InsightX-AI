"""Groq embedding helpers for article ingestion and semantic search."""

from __future__ import annotations

import asyncio
import os

from groq import AsyncGroq

from models.article import EmbeddedArticle, RawArticle
from pipeline.deduplicator import compute_hash


def _require_env(name: str) -> str:
    """Return a required environment variable or raise a clear error."""

    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


groq_client = AsyncGroq(api_key=_require_env("GROQ_API_KEY"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text-v1.5")


async def embed_text(text: str) -> list[float]:
    """Generate an embedding vector for the provided text via Groq."""

    for attempt in range(2):
        try:
            response = await groq_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
            return list(response.data[0].embedding)
        except Exception:
            if attempt == 0:
                await asyncio.sleep(1)
                continue
            raise
    raise RuntimeError("Embedding generation failed unexpectedly")


async def embed_article(article: RawArticle) -> EmbeddedArticle:
    """Embed a single article and return the enriched payload."""

    embedding_input = f"{article.title}. {article.content[:500]}"
    embedding = await embed_text(embedding_input)
    content_hash = compute_hash(article)
    return EmbeddedArticle(
        **article.model_dump(),
        embedding=embedding,
        content_hash=content_hash,
    )


async def embed_articles_batch(articles: list[RawArticle], concurrency: int = 5) -> list[EmbeddedArticle]:
    """Embed multiple articles concurrently while respecting a concurrency cap."""

    semaphore = asyncio.Semaphore(concurrency)

    async def _embed(article: RawArticle) -> EmbeddedArticle:
        async with semaphore:
            return await embed_article(article)

    return await asyncio.gather(*(_embed(article) for article in articles))
