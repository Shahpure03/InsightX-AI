import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import ArticleInput, InsightOutput, UserCreate
from agents.pipeline import run_pipeline
from db.supabase_client import create_or_update_user, get_recent_articles

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
        return result
    except ValueError as ve:
        print(f"Validation Error in pipeline: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Internal Server Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze article. Please try again later.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
