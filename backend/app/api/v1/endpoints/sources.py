from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.source import SourceCreate, SourceResponse
from app.repositories.source_repo import SourceRepository
from app.services.scraper import SovereignScraper
from app.services.llm import OllamaService

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

        content = await SovereignScraper.scrape_url(source.url)
        await repo.update_content(uid, content)
        
        return {"status": "success", "length": len(content)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{uid}/summarize")
async def summarize_source(uid: str):
    """
    Summarize a source by UID using Ollama.
    """
    try:
        source = await repo.get_source_by_uid(uid)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        content = await repo.get_source_content(uid)
        if not content:
             raise HTTPException(status_code=400, detail="Source has no content to summarize. Please crawl it first.")

        summary = await OllamaService.summarize(content)
        await repo.update_summary(uid, summary)
        
        return {"status": "success", "summary_length": len(summary), "preview": summary[:100] + "..."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{uid}/analyze")
async def analyze_source(uid: str):
    """
    Analyze reliability of a source by UID.
    Flow: Scrape -> Vectorize -> Reliability Analysis
    """
    import random
    from app.services.knowledge_base import KnowledgeBase

    try:
        source = await repo.get_source_by_uid(uid)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # 1. Scrape content
        # We ensure content is fresh or at least available.
        # If url is missing, we can't scrape, but if content exists we might rely on it.
        # Assuming URL is required for scraping.
        if not source.url:
             raise HTTPException(status_code=400, detail="Source has no URL for analysis")

        content = await SovereignScraper.scrape_url(source.url)
        # Put content in DB
        await repo.update_content(uid, content)
        
        # 2. Vectorize & Store
        kb = KnowledgeBase()
        await kb.vectorize_and_store(content, uid)

        # 3. Reliability Analysis (Mock)
        # Mock analysis logic: valid sources are mostly reliable
        # In a real scenario, this would call an LLM or Check logic
        mock_score = random.uniform(0.7, 0.95)
        
        await repo.update_reliability(uid, mock_score)
        
        return {
            "status": "success", 
            "reliability": mock_score,
            "vectorization": "completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{uid}")
async def delete_source(uid: str):
    """
    Delete a source by UID.
    """
    try:
        success = await repo.delete_source(uid)
        if not success:
            raise HTTPException(status_code=404, detail="Source not found")
        return {"status": "success", "message": "Source deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/")
async def delete_all_sources():
    """
    Delete ALL sources.
    """
    try:
        count = await repo.delete_all_sources()
        return {"status": "success", "message": f"Deleted {count} sources"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
