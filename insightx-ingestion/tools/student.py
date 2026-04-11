"""Student profile specific AI tools."""

from __future__ import annotations

import json
from tools.llm import generate_response

async def career_impact_analyser(title: str, content: str, major: str = "General") -> str:
    """Analyze how a news event might impact future career prospects for a specific major."""
    system_prompt = (
        f"You are a career advisory AI specifically analyzing news for a student majoring in '{major}'. "
        "Extract exactly 3 clear, actionable insights on how the events described in this article "
        "might impact future job markets, emerging required skills, or industry shifts related to their major."
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    return await generate_response(system_prompt, user_prompt, max_tokens=600)


async def concept_linker(title: str, content: str) -> dict:
    """Links news to textbook concepts — economics, history, science."""
    system_prompt = (
        "You are an academic curriculum alignment AI. Your job is to link the events in the provided article "
        "to foundational textbook concepts in subjects like Economics, History, Science, or Civics. "
        "Output valid JSON containing an array called 'concepts', where each item has:\n"
        "- 'subject': str (e.g. 'Macroeconomics', 'Biology')\n"
        "- 'concept': str (the textbook concept name)\n"
        "- 'connection': str (1-sentence explanation of how the news demonstrates this concept)"
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    response = await generate_response(system_prompt, user_prompt, max_tokens=800, temperature=0.1)
    
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"concepts": []}
