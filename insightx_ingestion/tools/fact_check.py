import json
from tools.llm import call_groq


def clean(res: str):
    return res.replace("```json", "").replace("```", "").strip()


async def model_1(claim, source_text):
    system = "You are an expert fact-checker."
    
    prompt = f"""
Check authenticity of the claim.

Return JSON:
{{
  "verdict": "credible | suspicious | false",
  "confidence": float
}}

CLAIM: {claim}
SOURCE: {source_text}
"""
    res = await call_groq(prompt, system)
    try:
        return json.loads(clean(res))
    except:
        return {"verdict": "credible", "confidence": 0.9}


async def model_2(claim, source_text):
    system = "You are a strict misinformation detector."

    prompt = f"""
Analyze if the claim is misleading or false.

Return JSON:
{{
  "verdict": "credible | suspicious | false",
  "confidence": float
}}

CLAIM: {claim}
SOURCE: {source_text}
"""
    res = await call_groq(prompt, system)
    try:
        return json.loads(clean(res))
    except:
        return {"verdict": "credible", "confidence": 0.9}


async def check_news_authenticity(claim, source_text):
    res1 = await model_1(claim, source_text)
    res2 = await model_2(claim, source_text)

    # Combine confidence
    final_score = (res1["confidence"] + res2["confidence"]) / 2

    # Final verdict
    if final_score > 0.7:
        verdict = "credible"
    elif final_score < 0.4:
        verdict = "false"
    else:
        verdict = "suspicious"

    return {
        "final_verdict": verdict,
        "final_confidence": round(final_score, 2),
        "model_1": res1,
        "model_2": res2
    }
