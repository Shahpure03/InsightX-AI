import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import ArticleInput, InsightOutput
from agents.pipeline import run_pipeline

app = FastAPI(title="InsightX AI - Multi-Agent Core")

# CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze", response_model=InsightOutput)
async def analyze_article(payload: ArticleInput):
    """
    Core entrypoint for the multi-agent ingestion and insight pipeline.
    Expects JSON containing URL and target Profile.
    """
    return await run_pipeline(payload)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
