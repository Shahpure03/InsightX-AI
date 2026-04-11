"""Shared Groq LLM client logic for the new Multi-Agent pipeline."""

from __future__ import annotations

from groq import AsyncGroq
from config import config

MODEL_NAME = "llama-3.3-70b-versatile"

def _get_client() -> AsyncGroq:
    """Return Groq client lazily to ensure env vars are loaded."""
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY missing in config.")
    return AsyncGroq(api_key=config.GROQ_API_KEY)

async def call_groq(prompt: str, system: str = "") -> str:
    """Core LLM call function used globally by all agents."""
    client = _get_client()
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ] if system else [{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        print(f"LLM Generation failed: {exc}")
        return ""
