from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.schemas.source import SourceCreate, SourceResponse
from app.schemas.analysis import AnalysisResult, ChatRequest
from app.repositories.source_repo import SourceRepository
from app.services.scraper import SovereignScraper
from app.services.llm import DynamicLLMService
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
    Summarize a source by UID using dynamic LLM service.
    """
    try:
        source = await repo.get_source_by_uid(uid)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        content = await repo.get_source_content(uid)
        if not content:
             raise HTTPException(status_code=400, detail="Source has no content to summarize. Please crawl it first.")

        reasoning = await DynamicLLMService.summarize(content)
        await repo.update_analysis_results(uid, source.inclusion_score or 50, source.suggested_prompts or [], reasoning)
        
        return {"status": "success", "summary_length": len(reasoning), "preview": reasoning[:100] + "..."}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to summarize source")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{uid}/analyze")
async def analyze_source(uid: str, force: bool = Query(False, description="Force re-analysis, bypassing cache")):
    """
    Analyze inclusion of a source by UID.
    Uses Neo4j cache to avoid redundant LLM calls.
    Pass ?force=true to bypass cache and force re-analysis.
    """
    from app.services.knowledge_base import KnowledgeBase
    from app.services.extractor import EntityExtractor

    try:
        source = await repo.get_source_by_uid(uid)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        if not source.url:
             raise HTTPException(status_code=400, detail="Source has no URL for analysis")

        # ─── Cache Check ───────────────────────────────────────
        if not force:
            cached = await repo.get_cached_analysis(uid)
            if cached:
                logger.info(f"Cache HIT for source {uid}. Skipping LLM.")
                return {
                    "inclusion_score": cached["inclusion_score"],
                    "suggested_prompts": cached["suggested_prompts"],
                    "reasoning": cached["reasoning"],
                    "cached": True,
                }

        # ─── Full Analysis Pipeline ────────────────────────────
        logger.info(f"Cache MISS for source {uid}. Running full pipeline.")

        # 1. Scrape content
        content = await SovereignScraper.scrape_url(source.url)
        await repo.update_content(uid, content)
        
        # 2. Vectorize & Store
        kb = KnowledgeBase()
        await kb.vectorize_and_store(content, uid)

        # 2.5 Entity Extraction (GraphRAG)
        extractor = EntityExtractor()
        # Truncate content for extraction to avoid LLM limits on heavy graphs
        extraction = await extractor.extract(content[:6000])
        await repo.store_extraction(uid, extraction)

        # 3. Inclusion Analysis (LLM)
        analysis_result = await DynamicLLMService.analyze_article(content)
        
        # 4. Save Results (now includes reasoning for cache)
        await repo.update_analysis_results(
            uid, 
            analysis_result.inclusion_score, 
            analysis_result.suggested_prompts,
            analysis_result.reasoning,
        )
        
        return {
            "inclusion_score": analysis_result.inclusion_score,
            "suggested_prompts": analysis_result.suggested_prompts,
            "reasoning": analysis_result.reasoning,
            "cached": False,
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to analyze source")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{uid}/chat")
async def chat_with_source(uid: str, chat_request: ChatRequest):
    """
    Interact with a specific source using Hybrid Search (GraphRAG).
    """
    from app.services.knowledge_base import KnowledgeBase

    try:
        source = await repo.get_source_by_uid(uid)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        kb = KnowledgeBase()
        context = await kb.hybrid_search(chat_request.prompt, uid)

        system_prompt = """Você é o Cérebro Híbrido do EquiTracker, um auditor editorial especializado em ética jornalística e análise de viés interseccional. Você não é um assistente de IA genérico.
Sua função é receber o [CONTEXTO] extraído da base de grafos/vetores de uma matéria jornalística e responder à [PERGUNTA] do usuário com extremo rigor técnico.
DIRETRIZES FUNDAMENTAIS:
ESCOPO ESTRITO: Responda APENAS focando em métricas de inclusão, equidade, e padrões de exclusão (raça, gênero, classe, capacitismo, LGBTQIA+, marcadores territoriais).
RIGOR JORNALÍSTICO: Identifique fenômenos como Viés de Omissão, Falsa Equivalência, Tokenismo e Enquadramento estigmatizante.
ZERO ALUCINAÇÃO: Baseie 100% de suas afirmações nos dados do [CONTEXTO]. Se faltarem dados, declare: "Os dados extraídos da fonte são insuficientes para esta avaliação."
TOM: Clínico, objetivo e imparcial. Apresente os vieses como falhas técnicas de reportagem.
ACESSIBILIDADE: Responda em parágrafos curtos, diretos e com bullet points quando aplicável."""

        user_prompt = f"[CONTEXTO]:\n{context}\n\n[PERGUNTA]:\n{chat_request.prompt}"

        # We want markdown response, not JSON for the chat
        answer = await DynamicLLMService._call_provider(system_prompt, user_prompt, response_format="text")

        return {"answer": answer}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to process chat")
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
