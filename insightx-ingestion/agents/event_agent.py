from models.schemas import AgentContext
from tools.llm import call_groq
from tools.fact_check import check_facts
import json

async def run(context: AgentContext) -> AgentContext:
    """Event Agent: Extracts what happened and runs a fact check."""
    
    # 1. Event Structuring (Shared)
    system = "You are a journalistic extraction API."
    prompt = (
        "Extract the core 5Ws (Who, What, Where, When, Why) from the provided article text. "
        "Output ONLY a JSON object with keys 'who', 'what', 'where', 'when', 'why'. "
        "Keep the values concise.\n\n"
        f"TEXT:\n{context.article_text}"
    )
    
    res = await call_groq(prompt, system)
    try:
        context.event_facts = json.loads(res.replace("```json", "").replace("```", "").strip())
    except:
        context.event_facts = {"who": "Unknown", "what": "Failed to extract", "where": "Unknown", "when": "Unknown", "why": "Unknown"}
        
    # 2. Fact Check Layer (Shared)
    claim = context.event_facts.get("what", "Unknown event.")
    context.fact_check = await check_facts(claim, context.article_text)
    
    return context
