"""Investor profile specific AI tools."""

from __future__ import annotations

import json
from tools.llm import generate_response

async def stock_impact_scanner(title: str, content: str) -> dict:
    """Scan news for potential positive/negative impacts on public companies."""
    system_prompt = (
        "You are an elite financial intelligence AI. Your job is to identify specific publicly traded "
        "companies mentioned or heavily implied in the text and predict the event's market impact sentiment. "
        "Output valid JSON containing an array called 'impacts' where each item has:\n"
        '- "company": str\n'
        '- "ticker": str (if known, else null)\n'
        '- "sentiment": str ("Bullish", "Bearish", "Neutral")\n'
        '- "reasoning": str (1 concise sentence)'
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    response = await generate_response(system_prompt, user_prompt, max_tokens=800, temperature=0.1)
    
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"impacts": []}


async def macro_trend_detector(title: str, content: str) -> str:
    """Connects event to inflation, rates, FX signals."""
    system_prompt = (
        "You are a global macroeconomics analyst. Read the provided article and assess whether it indicates "
        "any underlying macroeconomic shifts such as inflation impact, central bank interest rate changes, "
        "or foreign exchange (FX) currency signals. Write a 2-paragraph macro brief summarizing these trends."
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    return await generate_response(system_prompt, user_prompt, max_tokens=500)
