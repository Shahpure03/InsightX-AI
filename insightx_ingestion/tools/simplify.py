from tools.llm import call_groq

async def simplify_text(text: str, strict: bool = False) -> str:
    """Virtual replacement for google/flan-t5-base via Groq"""
    system = "You are a text simplification model."
    target = "a highly simplified, 6th-grade reading level (Flesch-Kincaid > 70)" if strict else "clear, easy-to-read language"
    prompt = f"Rewrite the following text into {target}. Output ONLY the rewritten text.\n\nTEXT:\n{text}"
    return await call_groq(prompt, system)
