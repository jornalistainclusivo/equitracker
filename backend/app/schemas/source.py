from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

class SourceCreate(BaseModel):
    name: str = Field(..., description="The name of the source")
    url: Optional[str] = Field(None, description="The URL of the source")
    inclusion_score: Optional[int] = Field(None, ge=0, le=100, description="Inclusion Index score (0-100)")
    reasoning: Optional[str] = Field(None, description="Paragraph justifying the score")

class SourceResponse(SourceCreate):
    uid: str = Field(..., description="Unique identifier for the source")
    created_at: datetime = Field(..., description="Timestamp when the source was created")
    suggested_prompts: Optional[List[str]] = Field(default=[], description="Suggested follow-up prompts for chat")

    class Config:
        from_attributes = True
