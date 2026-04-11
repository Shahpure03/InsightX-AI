"""Common AI tools usable across all user profiles."""

from __future__ import annotations

import json
import asyncio
from io import BytesIO
from gtts import gTTS

from pipeline.embedder import embed_text
from tools.llm import generate_response


async def event_extractor(title: str, content: str) -> dict:
    """Extract Who, What, Where, When, and Why from an article."""
    system_prompt = (
        "You are an objective journalistic engine. Your job is to extract the 5 Ws from the article. "
        "Output valid JSON containing exactly these keys: 'who', 'what', 'where', 'when', 'why'. "
        "Keep each value concise (1-2 sentences max)."
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    response = await generate_response(system_prompt, user_prompt, max_tokens=600, temperature=0.1)
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"who": "Unknown", "what": "Unknown", "where": "Unknown", "when": "Unknown", "why": "Unknown"}


async def ai_summariser(title: str, content: str, length: str = "medium", personalization: str = "") -> str:
    """Summarise a given article based on requested length and active profile context."""
    
    length_rules = {
        "short": "a highly concise, 3-bullet-point summary",
        "medium": "a solid 2-paragraph contextual summary",
        "full": "a comprehensive, detailed summary exploring nuanced angles"
    }
    
    rule = length_rules.get(length.lower(), length_rules["medium"])
    
    system_prompt = (
        f"You are an expert news summariser. Your goal is to compress the provided news article into {rule}. "
        "Ensure the language focuses on the core events and immediate implications."
    )
    if personalization:
        system_prompt += f"\n\nAdapt your tone and depth for this specific active profile: {personalization}"

    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    return await generate_response(system_prompt, user_prompt, max_tokens=1000)


async def cause_effect_chain(title: str, content: str) -> str:
    """Explain why it happened and what follows."""
    system_prompt = (
        "You are an analytical logic engine mapping cause-and-effect chronologies. "
        "Explain exactly what the root cause of this event was, and clearly outline "
        "the domino effects or cascading implications that will likely follow. Use a structured, "
        "step-by-step format."
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    return await generate_response(system_prompt, user_prompt, max_tokens=600)


async def action_suggester(title: str, content: str, personalization: str = "General Reader") -> list[str]:
    """Provide practical next steps based on the event impact."""
    system_prompt = (
        f"Based on the provided event, suggest 3 practical next steps or actions "
        f"that a '{personalization}' could take to protect themselves, capitalize on the event, "
        "or learn more. Output valid JSON containing an array of strings in a key called 'actions'."
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    response = await generate_response(system_prompt, user_prompt, max_tokens=500, temperature=0.2)
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned).get("actions", [])
    except json.JSONDecodeError:
        return []


async def prediction_forecaster(title: str, content: str) -> str:
    """Detect future signals and what to watch next."""
    system_prompt = (
        "You are a predictive intelligence analyst. Identify 2-3 specific 'future signals' "
        "or lagging indicators that readers should watch out for over the coming weeks as a direct "
        "result of this news event. Explain why these signals matter."
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    return await generate_response(system_prompt, user_prompt, max_tokens=600)


async def sentiment_analyser(title: str, content: str) -> dict:
    """Detect the overarching panic vs optimism sentiment."""
    system_prompt = (
        "Analyze the emotional tone and market/societal sentiment of the provided article. "
        "Determine the overall stance as 'Panic', 'Optimism', or 'Neutral'. "
        "Output valid JSON containing:\n"
        '- "sentiment": str ("Panic", "Optimism", "Neutral")\n'
        '- "confidence": int (0-100)\n'
        '- "trigger_words": list of strings (words that contributed to this sentiment)'
    )
    user_prompt = f"TITLE: {title}\n\nCONTENT:\n{content}"
    response = await generate_response(system_prompt, user_prompt, max_tokens=500, temperature=0.1)
    
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"sentiment": "Neutral", "confidence": 0, "trigger_words": []}


async def ai_translation(text: str, target_language: str) -> str:
    """Translate an insight or article segment into a target language."""
    system_prompt = (
        f"You are a native linguistic translator perfectly fluent in '{target_language}'. "
        "Translate the following text accurately without losing nuances. Return ONLY the translated text, "
        "with absolutely no conversational filler."
    )
    user_prompt = f"TEXT:\n{text}"
    return await generate_response(system_prompt, user_prompt, max_tokens=1500, temperature=0.1)


async def text_to_speech(text: str, language_code: str = "en") -> BytesIO:
    """Convert text to speech using Google TTS asynchronously and return a BytesIO MP3 buffer."""
    def _generate() -> BytesIO:
        tts = gTTS(text=text, lang=language_code)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
        
    return await asyncio.to_thread(_generate)

from db.supabase_client import semantic_search

async def fact_check_claim(claim: str) -> dict:
    """Execute a Retrieval-Augmented Generation (RAG) fact check against the Supabase VectorDB."""
    claim_embedding = await embed_text(claim)
    relevant_articles = await semantic_search(query_embedding=claim_embedding, limit=5, threshold=0.7)
    
    if not relevant_articles:
         return {
             "verdict": "Unverified", 
             "explanation": "No relevant historical corroboration found in the database.",
             "sources": []
         }
         
    context_chunks = "\n\n".join(
        f"[Source {idx+1}]: {article.get('title')} - {article.get('content')[:1000]}"
        for idx, article in enumerate(relevant_articles)
    )
    
    system_prompt = (
        "You are an impartial fact-checking engine. Compare the user's claim against the provided database sources. "
        "Determine if the claim is 'True', 'False', or 'Mixed'. "
        "Output valid JSON containing:\n"
        '- "verdict": str ("True", "False", "Mixed")\n'
        '- "explanation": str (A 2 sentence justification referencing the sources by number)'
    )
    user_prompt = f"CLAIM TO VERIFY: {claim}\n\nRETRIEVED CONTEXT:\n{context_chunks}"
    
    response = await generate_response(system_prompt, user_prompt, max_tokens=800, temperature=0.1)
    
    try:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
        result["sources"] = [{"id": article.get("id"), "url": article.get("url")} for article in relevant_articles]
        return result
    except json.JSONDecodeError:
        return {"verdict": "Error", "explanation": "Fact checker format parsing failed.", "sources": []}
