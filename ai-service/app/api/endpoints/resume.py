from typing import Any

from app.core.llm import llm_client
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str | None = None


class AnalyzeResponse(BaseModel):
    ats_score: int
    analysis_results: dict[str, Any]


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_resume(request: AnalyzeRequest):
    try:
        # TODO: integrate real LLM here
        # For now, use the mock
        result = llm_client.analyze_resume(request.resume_text)
        return AnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
