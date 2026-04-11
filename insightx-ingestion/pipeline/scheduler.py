"""Async scheduler for recurring ingestion runs."""

from __future__ import annotations

import asyncio
import logging
import os

from db.supabase_client import log_ingestion_run
from pipeline.ingestor import NewsIngestor

logger = logging.getLogger(__name__)


async def start_scheduler(ingestor: NewsIngestor) -> None:
    """Run the ingestion pipeline forever at the configured interval."""

    interval = int(os.getenv("INGEST_INTERVAL_SECONDS", "900"))
    while True:
        try:
            result = await ingestor.run_full_ingestion()
            logger.info("Scheduled ingestion completed: %s", result.model_dump())
            await log_ingestion_run(result)
        except Exception:
            logger.exception("Scheduled ingestion failed")
        await asyncio.sleep(interval)
