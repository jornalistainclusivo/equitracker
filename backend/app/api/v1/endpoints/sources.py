from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.source import SourceCreate, SourceResponse
from app.repositories.source_repo import SourceRepository
from app.services.crawler import CrawlerService

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

@router.post("/{uid}/crawl")
async def crawl_source(uid: str):
    """
    Crawl a source by UID.
    """
    try:
        source = await repo.get_source_by_uid(uid)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Ensure URL is present
        if not source.url:
             raise HTTPException(status_code=400, detail="Source has no URL")

        content = await CrawlerService.scrape_url(source.url)
        await repo.update_content(uid, content)
        
        return {"status": "success", "length": len(content)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
