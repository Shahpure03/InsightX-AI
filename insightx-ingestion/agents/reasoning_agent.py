from models.schemas import AgentContext, Profile
from tools.llm import call_groq
from tools.sentiment import analyse_sentiment
from tools.simplify import simplify_text
import json

async def run(context: AgentContext) -> AgentContext:
    """Reasoning Agent: Builds cause-effect, analyses sentiment, simplifies text, and links concepts (Student)."""
    
    # 1. Cause-effect chain (Shared)
    system = "You are an analytical logic engine."
    prompt = (
        "Based on these event facts, generate a 3-step cause-and-effect chain forecasting the immediate outcomes. "
        "Output ONLY a valid JSON array of 3 strings.\n\n"
        f"FACTS:\n{json.dumps(context.event_facts)}"
    )
    res = await call_groq(prompt, system)
    try:
        context.cause_effect_chain = {"steps": json.loads(res.replace("```json", "").replace("```", "").strip())}
    except:
        context.cause_effect_chain = {"steps": []}
        
    # 2. Sentiment analyser (Shared)
    context.sentiment = await analyse_sentiment(context.article_text)
    
    # 3. Simplified language (Shared)
    is_explorer = context.profile == Profile.explorer
    context.simplified_text = await simplify_text(context.article_text, strict=is_explorer)
    
    # 4. Concept linker (Profile Specific)
    if context.profile == Profile.student:
        system_student = "You are an academic curriculum alignment AI."
        prompt_student = (
            "Link the events in the provided text to foundational textbook concepts (e.g. Economics, Science). "
            "Output JSON with a list of 'concepts' containing 'subject' and 'concept'.\n\n"
            f"TEXT:\n{context.article_text}"
        )
        res_stud = await call_groq(prompt_student, system_student)
        try:
            context.concept_links = json.loads(res_stud.replace("```json", "").replace("```", "").strip())
        except:
            context.concept_links = {"concepts": []}
            
    return context
