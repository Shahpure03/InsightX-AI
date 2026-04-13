from models.schemas import AgentContext, Profile
from tools.llm import call_groq
from tools.tts import generate_audio
from tools.quiz import generate_quiz
import json

async def run(context: AgentContext) -> AgentContext:
    """Action Agent: Suggests actionable next steps based on the profile context."""
    
    # 1. Action Suggestion (Shared)
    system = f"You are an AI assistant advising a(n) {context.profile.value}."
    prompt = (
        "Generate 2-3 practical, actionable next steps they should take based on this news event. "
        "Output ONLY a valid JSON array of strings.\n\n"
        f"TEXT:\n{context.article_text}"
    )
    res = await call_groq(prompt, system)
    try:
        context.action_suggestions = json.loads(res.replace("```json", "").replace("```", "").strip())
    except:
        context.action_suggestions = []
        
    # 2. Text-to-speech (Shared)
    # We convert the personalized deep_dive into audio
    audio_text = context.topic_deep_dive if context.topic_deep_dive else context.article_title
    context.tts_audio_path = await generate_audio(audio_text)
    
    # 3. Quiz generator (Profile specific: Explorer)
    if context.profile == Profile.explorer:
        context.quiz = await generate_quiz(context.article_text, num_questions=3)
        
    return context
