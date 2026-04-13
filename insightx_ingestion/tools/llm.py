"""Shared Groq LLM client logic for the new Multi-Agent pipeline."""

from __future__ import annotations

import asyncio
from groq import AsyncGroq
from config import config

MODEL_NAME = "llama-3.1-8b-instant"

def _get_client() -> AsyncGroq:
    """Return Groq client lazily to ensure env vars are loaded."""
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY missing in config.")
    return AsyncGroq(api_key=config.GROQ_API_KEY)

async def call_groq(prompt: str, system: str = "") -> str:
    """Core LLM call function with exponential backoff retry for rate limits."""
    client = _get_client()
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ] if system else [{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            print(f"LLM Generation failed (Attempt {attempt + 1}/{max_retries}): {exc}")
            if attempt < max_retries - 1:
                # Exponential backoff: 2s, 4s
                await asyncio.sleep(2 ** (attempt + 1))
            else:
                print("Max retries reached for LLM generation.")
                return ""
