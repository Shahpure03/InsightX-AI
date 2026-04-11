import json
from tools.llm import call_groq

async def check_facts(claim: str, source_text: str) -> dict:
    """Virtual replacement for facebook/bart-large-mnli via Groq"""
    system = "You are an NLI (Natural Language Inference) zero-shot classification model."
    prompt = (
        "Compare the CLAIM against the SOURCE_TEXT. Determine if the claim is Entailment, Neutral, or Contradiction. "
        "Output ONLY valid JSON containing 'verdict' (entailment, neutral, contradiction) and 'score' (0.0 to 1.0 confidence).\n\n"
        f"CLAIM:\n{claim}\n\nSOURCE_TEXT:\n{source_text}"
    )
    res = await call_groq(prompt, system)
    try:
        return json.loads(res.replace("```json", "").replace("```", "").strip())
    except:
        return {"verdict": "neutral", "score": 0.5}
