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
async def analyze_article(payload: ArticleInput):
    """
    Core entrypoint for the multi-agent ingestion and insight pipeline.
    Expects JSON containing URL and target Profile.
    """
    return await run_pipeline(payload)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
