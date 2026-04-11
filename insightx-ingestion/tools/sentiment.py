import json
from tools.llm import call_groq

async def analyse_sentiment(text: str) -> dict:
    """Virtual replacement for cardiffnlp/twitter-roberta-base-sentiment via Groq"""
    system = "You are a specialized sentiment analysis API."
    prompt = (
        "Analyze the sentiment of the following text. "
        "Output ONLY valid JSON containing 'label' (positive, neutral, or negative) and 'score' (0.0 to 1.0).\n\n"
        f"TEXT:\n{text}"
    )
    res = await call_groq(prompt, system)
    try:
        return json.loads(res.replace("```json", "").replace("```", "").strip())
    except:
        return {"label": "neutral", "score": 0.5}
