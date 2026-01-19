from typing import List
from pydantic import BaseModel, Field

class AnalysisResult(BaseModel):
    inclusion_score: int = Field(..., ge=0, le=100, description="Inclusion Index score (0-100)")
    suggested_prompts: List[str] = Field(..., description="Context-aware follow-up questions")
    summary: str = Field(..., description="Brief summary of the analysis")
