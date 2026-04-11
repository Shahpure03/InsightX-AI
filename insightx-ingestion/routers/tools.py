"""FastAPI router exposing AI Tool Services for different profiles."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from tools.common import (
    ai_summariser, sentiment_analyser, fact_check_claim,
    event_extractor, cause_effect_chain, action_suggester,
    prediction_forecaster, ai_translation, text_to_speech
)
from tools.student import career_impact_analyser, concept_linker
from tools.investor import stock_impact_scanner, macro_trend_detector


router = APIRouter()


class ArticleRequest(BaseModel):
    title: str
    content: str


class SummariserRequest(ArticleRequest):
    length: str = "medium"
    personalization: str = ""


class FactCheckRequest(BaseModel):
    claim: str = Field(..., min_length=5)


class CareerImpactRequest(ArticleRequest):
    major: str = "General"


class ActionSuggestRequest(ArticleRequest):
    personalization: str = "General Reader"


class TranslateRequest(BaseModel):
    text: str
    target_language: str


class TTSRequest(BaseModel):
    text: str
    language_code: str = "en"


# COMMON TOOLS ========================================================

@router.post("/common/event-extractor")
async def run_event_extractor(payload: ArticleRequest) -> dict:
    return await event_extractor(payload.title, payload.content)

@router.post("/common/summarise")
async def run_summariser(payload: SummariserRequest) -> dict:
    summary = await ai_summariser(payload.title, payload.content, payload.length, payload.personalization)
    return {"summary": summary}

@router.post("/common/cause-effect")
async def run_cause_effect(payload: ArticleRequest) -> dict:
    chain = await cause_effect_chain(payload.title, payload.content)
    return {"cause_effect_chain": chain}

@router.post("/common/action-suggester")
async def run_action_suggester(payload: ActionSuggestRequest) -> dict:
    actions = await action_suggester(payload.title, payload.content, payload.personalization)
    return {"actions": actions}

@router.post("/common/prediction")
async def run_prediction(payload: ArticleRequest) -> dict:
    forecast = await prediction_forecaster(payload.title, payload.content)
    return {"forecast": forecast}

@router.post("/common/sentiment")
async def run_sentiment_analyser(payload: ArticleRequest) -> dict:
    return await sentiment_analyser(payload.title, payload.content)

@router.post("/common/fact-check")
async def run_fact_check(payload: FactCheckRequest) -> dict:
    return await fact_check_claim(payload.claim)

@router.post("/common/translate")
async def run_ai_translation(payload: TranslateRequest) -> dict:
    translation = await ai_translation(payload.text, payload.target_language)
    return {"translation": translation}

@router.post("/common/tts")
async def run_text_to_speech(payload: TTSRequest):
    audio_buffer = await text_to_speech(payload.text, payload.language_code)
    return StreamingResponse(audio_buffer, media_type="audio/mpeg")


# STUDENT TOOLS =======================================================

@router.post("/student/career-impact")
async def run_career_impact(payload: CareerImpactRequest) -> dict:
    insights = await career_impact_analyser(payload.title, payload.content, payload.major)
    return {"career_impact": insights}

@router.post("/student/concept-linker")
async def run_concept_linker(payload: ArticleRequest) -> dict:
    return await concept_linker(payload.title, payload.content)


# INVESTOR TOOLS ======================================================

@router.post("/investor/stock-impact")
async def run_stock_impact(payload: ArticleRequest) -> dict:
    return await stock_impact_scanner(payload.title, payload.content)

@router.post("/investor/macro-trend")
async def run_macro_trend(payload: ArticleRequest) -> dict:
    trend_brief = await macro_trend_detector(payload.title, payload.content)
    return {"macro_trend": trend_brief}


# YOUNG EXPLORER TOOLS ================================================

from tools.young_explorer import quiz_generator, mini_glossary

@router.post("/young-explorer/quiz")
async def run_quiz_generator(payload: ArticleRequest) -> dict:
    return await quiz_generator(payload.title, payload.content)

@router.post("/young-explorer/glossary")
async def run_mini_glossary(payload: ArticleRequest) -> dict:
    return await mini_glossary(payload.title, payload.content)
