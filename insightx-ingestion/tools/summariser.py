import json
from tools.llm import call_groq

async def summarise(text: str, max_length: int = 130) -> str:
    """Virtual replacement for facebook/bart-large-cnn via Groq"""
    system = "You are a professional news summarizer."
    prompt = f"Summarize the following text in under {max_length} words. Output ONLY the summary.\n\nTEXT:\n{text}"
    return await call_groq(prompt, system)
