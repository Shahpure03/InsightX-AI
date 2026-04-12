from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import ArticleInput, InsightOutput, UserCreate
from agents.pipeline import run_pipeline
from db.supabase_client import (
    create_or_update_user, get_recent_articles, get_article_by_id, log_user_article_interaction,
    upsert_article_enrichment, mark_article_pipeline_success, upsert_article_embedding
)
from pipeline.embedder import embed_text
import asyncio

app = FastAPI(title="InsightX AI - Multi-Agent Core")

# CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/feed")
async def get_feed():
    try:
        articles = await get_recent_articles(limit=20)
        return {"status": "success", "articles": articles}
    except Exception as e:
        print(f"Error fetching feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users/onboard")
async def onboard_user(user: UserCreate):
    """
    Onboard a user by adding their details to the Supabase Users table securely.
    """
    try:
        data = await create_or_update_user(
            email=user.email,
            name=user.name,
            role=user.role,
            interests=user.interests
        )
        return {"status": "success", "user": data}
    except Exception as e:
        print(f"Error onboarding user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze", response_model=InsightOutput)
async def analyze_article(payload: dict):
    """
    Core entrypoint for the multi-agent ingestion and insight pipeline.
    Expects JSON containing at least article_id or url, and target profile.
    """
    article_id = payload.get("article_id")
    url = payload.get("url")
    title = payload.get("title")
    content = payload.get("content")
    profile = payload.get("profile", "general")
    user_id = payload.get("user_id")
    
    # 1. Clear input validation
    if not (article_id or url or content):
        print(f"DEBUG: Invalid payload received: {payload}")
        raise HTTPException(status_code=400, detail="Either 'article_id', 'url', or 'content' must be provided.")
        
    try:
        # Pass clearly to pipeline
        result = await run_pipeline(
            title=title,
            content=content,
            article_id=article_id,
            url=url,
            profile=profile
        )
        
        if article_id:
            async def _background_ml_tasks():
                # 1. Enriched Summary
                await upsert_article_enrichment(article_id, result.model_dump())
                # 2. Pipeline State
                await mark_article_pipeline_success(article_id)
                
                # 3. Embedding (Only if text is provided via content or fetched inside run_pipeline)
                text_to_embed = content
                if not text_to_embed and article_id:
                    db_art = await get_article_by_id(article_id)
                    if db_art:
                        text_to_embed = db_art.get("content", "")

                if text_to_embed and len(text_to_embed) > 50:
                    try:
                        emb = await embed_text(text_to_embed[:500])
                        await upsert_article_embedding(article_id, emb)
                    except Exception as emb_e:
                        print(f"Embedding Generation failed: {emb_e}")
                
                # 4. User Tracking (if applicable)
                if user_id:
                    await log_user_article_interaction(user_id, article_id, profile, "", result.model_dump())
                    
            asyncio.create_task(_background_ml_tasks())
            
        return result
    except ValueError as ve:
        print(f"Validation Error in pipeline: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Internal Server Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze article. Please try again later.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
