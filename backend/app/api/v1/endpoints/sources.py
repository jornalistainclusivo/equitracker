from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.source import SourceCreate, SourceResponse
from app.repositories.source_repo import SourceRepository

router = APIRouter()
repo = SourceRepository()

@router.post("/", response_model=SourceResponse)
async def create_source(source_in: SourceCreate):
    """
    Create a new source.
    """
    try:
        return await repo.create_source(source_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[SourceResponse])
async def read_sources():
    """
    Retrieve all sources.
    """
    try:
        return await repo.get_all_sources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
