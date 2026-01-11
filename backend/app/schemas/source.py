from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

class SourceCreate(BaseModel):
    name: str = Field(..., description="The name of the source")
    url: Optional[str] = Field(None, description="The URL of the source")
    reliability: float = Field(..., ge=0.0, le=1.0, description="Reliability score between 0.0 and 1.0")
    notes: Optional[str] = Field(None, description="Optional notes about the source")

class SourceResponse(SourceCreate):
    uid: str = Field(..., description="Unique identifier for the source")
    created_at: datetime = Field(..., description="Timestamp when the source was created")

    class Config:
        from_attributes = True
