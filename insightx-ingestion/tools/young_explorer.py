"""Young Explorer profile specific AI tools."""

from __future__ import annotations

import json
from tools.llm import generate_response

async def quiz_generator(title: str, content: str) -> dict:
    """Auto-builds fun comprehension quizzes from articles."""
    system_prompt = (
        "You are a fun, educational AI. Your job is to create a short, interactive reading "
        "comprehension quiz based on the provided article tailored for a young learner (age 8-13). "
        "Output valid JSON containing a 'quiz' object with a 'question', an array of 3 'options', "
        "and the 'answer_index' (0, 1, or 2)."
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    response = await generate_response(system_prompt, user_prompt, max_tokens=600, temperature=0.2)
    
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "quiz": {
                "question": "Failed to generate quiz.",
                "options": [],
                "answer_index": 0
            }
        }


async def mini_glossary(title: str, content: str) -> dict:
    """Highlights and explains every difficult word inline."""
    system_prompt = (
        "You are an educational dictionary AI. Scan the provided article for complex, technical, "
        "or difficult words that a young learner (age 8-13) might not know. "
        "Output valid JSON containing an array called 'glossary', where each item has:\n"
        "- 'word': str (the difficult word)\n"
        "- 'definition': str (a simple, kid-friendly explanation)\n"
        "- 'example': str (a fun example sentence using the word)"
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    response = await generate_response(system_prompt, user_prompt, max_tokens=800, temperature=0.1)
    
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"glossary": []}
