"""FastAPI router mapped to the Agent Builder Orchestration Pipeline."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from agents.orchestrator import run_agent_pipeline

router = APIRouter()

class PipelineRequest(BaseModel):
    title: str
    content: str
    profile: str = "Explorer"

@router.post("/run")
async def execute_pipeline(payload: PipelineRequest) -> dict:
    """Trigger the multi-stage Event->Reasoning->Action agent->Prediction workflow."""
    results = await run_agent_pipeline(payload.title, payload.content, payload.profile)
    return results
