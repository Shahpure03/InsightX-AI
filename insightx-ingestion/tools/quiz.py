import json
from tools.llm import call_groq

async def generate_quiz(text: str, num_questions: int = 3) -> list[dict]:
    """Virtual replacement for iarfmoose/t5-base-question-generator via Groq"""
    system = "You are an educational assessment generator."
    prompt = (
        f"Generate exactly {num_questions} multiple-choice questions based on the text. "
        "Output ONLY a valid JSON array where each object has:\n"
        "- 'question': str\n"
        "- 'options': list of 4 strings (including the right answer)\n"
        "- 'answer': str (the exact correct option)\n\n"
        f"TEXT:\n{text}"
    )
    res = await call_groq(prompt, system)
    try:
        return json.loads(res.replace("```json", "").replace("```", "").strip())
    except:
        return []
