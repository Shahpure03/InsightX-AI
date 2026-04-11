from models.schemas import AgentContext, Profile
from tools.llm import call_groq
from tools.translation import translate
from tools.summariser import summarise
import json

async def run(context: AgentContext) -> AgentContext:
    """Personalization Agent: Frames for the user context and translates/summarizes."""
    
    # 1. Topic Deep-Dive (Shared)
    system = f"You are writing a personalized deep-dive for a(n) {context.profile.value} audience."
    prompt = f"Explain the core concept behind this news event in one concise paragraph tailored to their interests.\n\nTEXT:\n{context.article_text}"
    context.topic_deep_dive = await call_groq(prompt, system)
    
    # 2. AI Translation (Shared, assuming english default if not specified elsewhere. Just a stub translate to placeholder or if logic passed)
    # We will simulate the request logic, translating the deep dive to Hindi as an example.
    context.translation = await translate(context.topic_deep_dive, target_lang="hi")
    
    # 3. AI Summariser (Shared)
    context.summary_short = await summarise(context.article_text, max_length=50)
    context.summary_long = await summarise(context.article_text, max_length=150)
    
    # Profile Specific Customizations
    if context.profile == Profile.student:
        sys_stud = "You are a career counselor."
        prmpt_stud = f"Map the events in this text to specific job sectors, skills, and hiring demand. Output valid JSON with a 'sectors' array.\n\nTEXT:\n{context.article_text}"
        res = await call_groq(prmpt_stud, sys_stud)
        try:
            context.career_impact = json.loads(res.replace("```json", "").replace("```", "").strip())
        except:
            context.career_impact = {"sectors": []}
            
    elif context.profile == Profile.investor:
        sys_inv = "You are a global macroeconomics analyst."
        prmpt_inv = f"Connect this event to inflation, interest rates, and FX signals in 1 paragraph.\n\nTEXT:\n{context.article_text}"
        context.macro_trend = await call_groq(prmpt_inv, sys_inv)
        
    return context
