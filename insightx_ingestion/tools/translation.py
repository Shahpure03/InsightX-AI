from tools.llm import call_groq

async def translate(text: str, target_lang: str) -> str:
    """Virtual replacement for Helsinki-NLP/opus-mt via Groq"""
    if target_lang.lower() in ("en", "english"):
        return text
        
    system = "You are an expert bilingual translation model."
    prompt = (
        f"Translate the following text flawlessly to {target_lang}. "
        "Output ONLY the translated text, with no introductory dialogue.\n\n"
        f"TEXT:\n{text}"
    )
    return await call_groq(prompt, system)
