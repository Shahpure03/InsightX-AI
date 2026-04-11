from models.schemas import ArticleInput, AgentContext, InsightOutput
from tools.news import fetch_article
from db.supabase_client import get_article_by_id
from agents import event_agent, reasoning_agent, personalization_agent, action_agent, prediction_agent

async def run_pipeline(article_input: ArticleInput) -> InsightOutput:
    """Executes the multi-agent architecture in sequence."""
    
    # 1. Fetch text
    if article_input.article_id:
        db_article = await get_article_by_id(article_input.article_id)
        if not db_article:
            raise ValueError(f"Article with DB ID {article_input.article_id} not found")
        news_data = {
            "text": db_article.get("content", ""),
            "title": db_article.get("title", ""),
            "url": db_article.get("url", "")
        }
        url_to_use = news_data["url"]
    elif article_input.url:
        news_data = await fetch_article(article_input.url)
        url_to_use = article_input.url
    else:
        raise ValueError("Either url or article_id must be provided")

    # Initialize the immutable-style Agent Context
    context = AgentContext(
        article_text=news_data.get("text", ""),
        article_title=news_data.get("title", ""),
        article_url=url_to_use,
        profile=article_input.profile
    )
    
    # 2. Sequential Multi-Agent Execution
    context = await event_agent.run(context)
    context = await reasoning_agent.run(context)
    context = await personalization_agent.run(context)
    context = await action_agent.run(context)
    context = await prediction_agent.run(context)
    
    # 3. Assemble InsightOutput
    
    # Dynamic insight packaging based on what the agents populated
    custom_insights = {}
    if context.career_impact: custom_insights["career_impact"] = context.career_impact
    if context.concept_links: custom_insights["concept_links"] = context.concept_links
    if context.macro_trend: custom_insights["macro_trend"] = context.macro_trend
    if context.portfolio_signals: custom_insights["portfolio_signals"] = context.portfolio_signals
    
    output = InsightOutput(
        profile_used=context.profile,
        title=context.article_title,
        original_url=context.article_url,
        summary=context.summary_short,
        event_context=context.event_facts,
        fact_check_confidence=str(context.fact_check.get("verdict", "unknown")),
        sentiment_label=str(context.sentiment.get("label", "neutral")),
        cause_effect=context.cause_effect_chain,
        simplified_explainer=context.simplified_text,
        deep_dive=context.topic_deep_dive,
        translated_context=context.translation,
        profile_specific_insights=custom_insights,
        next_steps=context.action_suggestions,
        future_predictions=context.predictions,
        quiz=context.quiz,
        audio_path=context.tts_audio_path
    )
    
    return output
