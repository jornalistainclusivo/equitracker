from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.source import SourceCreate, SourceResponse
from app.schemas.analysis import AnalysisResult
from app.repositories.source_repo import SourceRepository
from app.services.scraper import SovereignScraper
from app.services.llm import OllamaService
import logging

router = APIRouter()
repo = SourceRepository()
logger = logging.getLogger(__name__)

@router.post("/", response_model=SourceResponse)
async def create_source(source_in: SourceCreate):
    """
    Create a new source.
    """
    try:
        return await repo.create_source(source_in)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create source")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[SourceResponse])
async def read_sources():
    """
    Retrieve all sources.
    """
    try:
        return await repo.get_all_sources()
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to read sources")
        raise HTTPException(status_code=500, detail="Internal server error")

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
    except Exception:
        logger.exception("Failed to crawl source")
        raise HTTPException(status_code=500, detail="Internal server error")

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
    except Exception:
        logger.exception("Failed to summarize source")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{uid}/analyze")
async def analyze_source(uid: str):
    """
    Analyze inclusion of a source by UID.
    Flow: Scrape -> Analysis -> Update DB
    """
    from app.services.knowledge_base import KnowledgeBase

    try:
        source = await repo.get_source_by_uid(uid)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # 1. Scrape content
        if not source.url:
             raise HTTPException(status_code=400, detail="Source has no URL for analysis")

        content = await SovereignScraper.scrape_url(source.url)
        # Put content in DB
        await repo.update_content(uid, content)
        
        # 2. Vectorize & Store (Wait, do we need this for 1-click analysis? Maybe yes for RAG later)
        kb = KnowledgeBase()
        await kb.vectorize_and_store(content, uid)

        # 3. Inclusion Analysis (Real LLM)
        analysis_result = await OllamaService.analyze_article(content)
        
        # 4. Save Results
        await repo.update_analysis_results(
            uid, 
            analysis_result.inclusion_score, 
            analysis_result.suggested_prompts
        )
        
        return analysis_result
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to analyze source")
        raise HTTPException(status_code=500, detail="Internal server error")

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
    except Exception:
        logger.exception("Failed to delete source")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/")
async def delete_all_sources():
    """
    Delete ALL sources.
    """
    try:
        count = await repo.delete_all_sources()
        return {"status": "success", "message": f"Deleted {count} sources"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to delete all sources")
        raise HTTPException(status_code=500, detail="Internal server error")
