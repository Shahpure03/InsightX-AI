"""Main orchestration pipeline executing the AI agent multi-step workflow."""

from __future__ import annotations

import json
from typing import Any

from tools.llm import generate_response
from tools.common import event_extractor, prediction_forecaster, action_suggester
from tools.student import career_impact_analyser
from tools.investor import stock_impact_scanner

async def run_agent_pipeline(title: str, content: str, profile: str) -> dict[str, Any]:
    """
    Executes the multi-stage Agent Pipeline derived from the architecture diagram:
    Event -> Reasoning -> Personalised -> Action Agent -> Prediction
    """
    
    # 1. EVENT & REASONING STAGE
    # We leverage our common extractor to establish the foundational 5Ws
    event_data = await event_extractor(title, content)
    
    # Custom reasoning abstraction based on the raw event data
    system_reasoning = (
        "You are the inner reasoning monolog of an AI processing breaking news. "
        "Briefly contextualize the historical significance or broader meaning of this event in exactly 1 crisp sentence."
    )
    user_reasoning = f"EVENT DATA: {json.dumps(event_data)}"
    reasoning_context = await generate_response(system_reasoning, user_reasoning, max_tokens=150)
    
    
    # 2. PERSONALISATION STAGE
    # Based on the requested profile, we rewrite the core narrative.
    system_personalise = (
        f"You are the personalization engine. Rewrite a summary of the event strictly "
        f"for this profile archetype: '{profile}'. Use their vernacular. If 'Young Explorer', keep it simple and gamified. "
        "If 'Investor', focus on market dynamics. If 'Student', focus on academic/career hooks."
    )
    user_personalise = f"RAW EVENT: {json.dumps(event_data)}\nREASONING: {reasoning_context}"
    personalized_summary = await generate_response(system_personalise, user_personalise, max_tokens=400)
    
    
    # 3. ACTION AGENT STAGE
    # Select and run specific backend tools dependent strictly on the active user profile
    action_data: dict[str, Any] = {}
    
    if profile.lower() == "student":
        action_data["career_impact"] = await career_impact_analyser(title, content, major="General")
    elif profile.lower() == "investor":
        action_data["stock_impact"] = await stock_impact_scanner(title, content)
    elif profile.lower() in ["young explorer", "young_explorer"]:
        from tools.young_explorer import quiz_generator, mini_glossary
        action_data["quiz"] = await quiz_generator(title, content)
        action_data["glossary"] = await mini_glossary(title, content)
    else:  # General Default
        action_data["suggested_actions"] = await action_suggester(title, content, personalization=profile)


    # 4. PREDICTION STAGE
    # Append the future signals
    forecast = await prediction_forecaster(title, content)
    
    
    # 5. ASSEMBLE PIPELINE OUTPUT
    return {
        "event_summary": event_data,
        "reasoning": reasoning_context,
        "personalized_insight": personalized_summary,
        "actions_and_tools": action_data,
        "prediction": forecast
    }
