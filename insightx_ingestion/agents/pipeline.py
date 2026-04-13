import json
import logging
import asyncio
from typing import Dict, Any

from models.schemas import InsightOutput
from tools.news import fetch_article
from db.supabase_client import get_article_by_id
from tools.llm import call_groq
from tools.fact_check import check_news_authenticity

logger = logging.getLogger(__name__)

async def run_pipeline(title: str = None, content: str = None, article_id: str = None, url: str = None, profile: str = "general") -> InsightOutput:
    """
    Executes the optimized multi-agent architecture in a single LLM call.
    Accepts explicit inputs and falls back to Supabase/fetching if needed.
    """
    
    # 1. Input Handling and Validation
    if not (content or article_id or url):
        logger.error("Missing required input variables.")
        raise ValueError("Either url, article_id, or content must be provided")

    news_data = {"text": content or "", "title": title or "", "url": url or ""}

    try:
        if article_id and not news_data["text"]:
            db_article = await get_article_by_id(article_id)
            if db_article:
                news_data["text"] = db_article.get("content", "")
                news_data["title"] = db_article.get("title", "")
                news_data["url"] = db_article.get("url", "")
            else:
                logger.warning(f"Article with DB ID {article_id} not found.")
                
        elif url and not news_data["text"]:
            fetched = await fetch_article(url)
            news_data["text"] = fetched.get("text", "")
            news_data["title"] = fetched.get("title", "")
            news_data["url"] = url
            
    except Exception as e:
        logger.error(f"Error fetching article data: {e}")
        # Continue and try processing with whatever content we have
        
    article_text = news_data["text"]
    article_title = news_data["title"]
    article_url = news_data["url"]
    
    if not article_text:
        raise ValueError("Could not extract any content to analyze.")

    # 2. Optimized Single LLM Call
    system_prompt = (
        "You are an expert AI news analyst API. Process the provided article and return ONLY a valid JSON object. "
        "Do not include any markdown block formatting (no ```json text).\n\n"
        "Required JSON schema:\n"
        "{\n"
        "  \"summary\": \"A short 2-3 sentence summary\",\n"
        "  \"event_facts\": {\"who\": \"...\", \"what\": \"...\", \"where\": \"...\", \"when\": \"...\", \"why\": \"...\"},\n"
        "  \"sentiment_label\": \"positive\",\n"
        "  \"cause_effect\": [{\"text\": \"Event name\", \"description\": \"Short reason\", \"direction\": \"up|down|neutral\"}],\n"
        "  \"simplified_explainer\": \"Gamified/simple explanation\",\n"
        "  \"deep_dive\": \"Historical/broader context of the event\",\n"
        "  \"action_data\": {},\n"
        "  \"future_predictions\": [\"Prediction 1\", \"Prediction 2\"]\n"
        "}\n\n"
        "Profile-specific action_data rules:\n"
        "EVERY profile MUST contain 'suggested_actions': [\"action 1\", \"action 2\"]\n"
        "- student: also inject {\"career_impact\": [\"impact 1\", \"impact 2\", \"impact 3\"]}\n"
        "- investor: also inject {\"stock_impact\": [\"impact 1\", \"impact 2\", \"impact 3\"]}\n"
        "- youngExplorer: also inject {\"young_explorer_impact\": [\"impact 1\", \"impact 2\", \"impact 3\"], \"quiz\": {\"question\": \"...\", \"options\": [\"A\",\"B\",\"C\",\"D\"], \"answer_index\": 0}}\n"
        "- general: also inject {\"general_impact\": [\"impact 1\", \"impact 2\", \"impact 3\"]}"
    )
    
    user_prompt = f"PROFILE: {profile}\n\nTITLE: {article_title}\n\nCONTENT:\n{article_text[:6000]}"
    
    parsed = {}
    fact_check_res = {}
    try:
        main_task = call_groq(user_prompt, system_prompt)
        fact_task = check_news_authenticity(article_title, article_text[:3000])
        res, fact_check_result = await asyncio.gather(main_task, fact_task)
        
        # Clean potential markdown wrapping
        res_clean = res.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(res_clean)
        fact_check_res = fact_check_result
    except json.JSONDecodeError as decode_err:
        logger.error(f"Failed to parse LLM Output into JSON: {decode_err} - Raw Output: {res}")
    except Exception as e:
        logger.error(f"Error during optimized LLM generation: {e}")

    # 3. Assemble and Structure Output
    action_data = parsed.get("action_data", {})
    
    custom_insights = {}
    next_steps = []
    quiz_list = []
    
    # Map profile-specific actions explicitly
    if "career_impact" in action_data:
        custom_insights["career_impact"] = action_data["career_impact"]
    if "stock_impact" in action_data:
        custom_insights["portfolio_signals"] = action_data["stock_impact"]
    if "young_explorer_impact" in action_data:
        custom_insights["fun_facts"] = action_data["young_explorer_impact"]
    if "general_impact" in action_data:
        custom_insights["general_impact"] = action_data["general_impact"]
        
    if "suggested_actions" in action_data:
        next_steps = action_data["suggested_actions"]
    if "quiz" in action_data:
        quiz_data = action_data["quiz"]
        if isinstance(quiz_data, dict):
            quiz_list = [quiz_data]
            
    # Default fallbacks
    safe_summary = parsed.get("summary", "Summary unavailable.")
    safe_event_facts = parsed.get("event_facts", {"who": "?", "what": "Failed to parse", "where": "?", "when": "?", "why": "?"})
    
    confidence_str = "high"
    if fact_check_res and "final_confidence" in fact_check_res:
        conf_pct = int(fact_check_res["final_confidence"] * 100)
        verdict = fact_check_res.get("final_verdict", "unknown").capitalize()
        confidence_str = f"{conf_pct}% ({verdict})"
    
    output = InsightOutput(
        profile_used=profile,
        title=article_title,
        original_url=article_url,
        summary=safe_summary,
        event_context=safe_event_facts,
        fact_check_confidence=confidence_str, 
        sentiment_label=parsed.get("sentiment_label", "neutral"),
        cause_effect=(parsed.get("cause_effect") if isinstance(parsed.get("cause_effect"), list) else [{"text": "Impact", "description": "Analyzing implications...", "direction": "neutral"}]),
        simplified_explainer=parsed.get("simplified_explainer", "Content too complex to simplify."),
        deep_dive=parsed.get("deep_dive", "No deeper contextual insight generated."),
        translated_context="",
        profile_specific_insights=custom_insights,
        next_steps=next_steps,
        future_predictions=parsed.get("future_predictions", []),
        quiz=quiz_list,
        audio_path=""
    )
    
    return output
