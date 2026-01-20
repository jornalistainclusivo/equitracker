import os

# Definição dos arquivos e seus conteúdos corrigidos
files = {
    "frontend/src/components/AddSourceInput.tsx": r'''import { useState } from 'react';
import { ArrowRight, Globe, Loader2, AlertCircle } from 'lucide-react';
import api from '../services/api';

interface AddSourceInputProps {
    onSourceAdded: () => void;
}

interface ApiError {
    response?: {
        data?: {
            detail?: string | Array<{ msg: string }>;
        };
    };
    message?: string;
}

const AddSourceInput = ({ onSourceAdded }: AddSourceInputProps) => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [submittingStatus, setSubmittingStatus] = useState<string>('');
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const extractDomain = (url: string): string => {
        try {
            const hostname = new URL(url).hostname;
            return hostname.replace('www.', '');
        } catch {
            return 'Fonte Desconhecida';
        }
    };

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url.trim()) return;

        setLoading(true);
        setSubmittingStatus('Validando...');
        setErrorMsg(null);

        try {
            const name = extractDomain(url);

            // 1. Create source with full payload required by Backend
            const payload = {
                url: url,
                name: name,
                inclusion_score: 50, // Default initial value (0-100)
                notes: "Adicionado via Dashboard"
            };

            const createRes = await api.post('/sources/', payload);
            const newUid = createRes.data.uid;

            // 2. Trigger analysis
            setSubmittingStatus('Analisando inclusão...');
            await api.post(`/sources/${newUid}/analyze`);

            // 3. Refresh list
            onSourceAdded();
            setUrl('');
        } catch (error: unknown) {
            console.error("Failed to add source:", error);
            const err = error as ApiError;

            let displayMsg = "Erro ao adicionar fonte.";

            if (err.response?.data?.detail) {
                const detail = err.response.data.detail;
                if (Array.isArray(detail)) {
                    displayMsg = detail.map(d => d.msg).join(', ');
                } else {
                    displayMsg = String(detail);
                }
            } else if (err.message) {
                displayMsg = err.message;
            }

            setErrorMsg(displayMsg);
        } finally {
            setLoading(false);
            setSubmittingStatus('');
        }
    };

    return (
        <div className="py-12 px-4 mb-8 bg-gradient-to-b from-gray-50 to-white rounded-xl shadow-sm border border-gray-100 flex flex-col items-center text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                <Globe className="w-6 h-6 text-blue-600" />
                Auditoria de Viés Interseccional
            </h2>
            <p className="text-gray-500 text-sm font-medium mb-6">
                Arquitetura de Cérebro Híbrido para insights sobre viés sistêmico e padrões de exclusão.
            </p>

            <form onSubmit={handleAdd} className="w-full max-w-2xl relative">
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <ArrowRight className="w-5 h-5 text-gray-400" />
                    </div>

                    <input
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="Cole a URL de uma fonte para auditar..."
                        className="w-full pl-12 pr-28 py-3 rounded-lg border border-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    />

                    <button
                        type="submit"
                        disabled={loading}
                        className="absolute right-2 top-1/2 -translate-y-1/2 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-semibold"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>Adicionar</span>}
                    </button>
                </div>

                {submittingStatus && (
                    <div className="mt-3 text-sm text-gray-500">{submittingStatus}</div>
                )}

                {errorMsg && (
                    <div className="mt-3 text-sm text-red-600 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        {errorMsg}
                    </div>
                )}
            </form>
        </div>
    );
};

export default AddSourceInput;
''',

    "frontend/src/pages/HistoryPage.tsx": r'''import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, Globe, Trash2, ArrowLeft, Eye, AlertTriangle } from 'lucide-react';
import api from '../services/api';
import { Source } from '../types';
import StatusBadge from '../components/StatusBadge';

const HistoryPage = () => {
    const [sources, setSources] = useState<Source[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const fetchSources = async () => {
        try {
            setLoading(true);
            const response = await api.get<{ sources: Source[] } | Source[]>('/sources/');
            let data: Source[] = [];
            if (Array.isArray(response.data)) {
                data = response.data;
            } else if (response.data && Array.isArray((response.data as any).sources)) {
                data = (response.data as any).sources;
            }
            // Sort by uid descending as a proxy for date since date is not in types.ts
            setSources(data.sort((a, b) => (b.uid > a.uid ? 1 : -1)));
            setError(null);
        } catch (err: unknown) {
            console.error("Failed to fetch sources:", err);
            setError("Falha ao buscar histórico de fontes.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSources();
    }, []);

    const handleDelete = async (uid: string) => {
        try {
            await api.delete(`/sources/${uid}`);
            setSources(prev => prev.filter(s => s.uid !== uid));
        } catch (err) {
            console.error("Failed to delete source:", err);
            setError("Erro ao excluir fonte.");
        }
    };

    const handleClearAll = async () => {
        if (!confirm("Tem certeza que deseja excluir todas as fontes?")) return;
        try {
            await api.delete(`/sources/`);
            setSources([]);
        } catch (err) {
            console.error("Failed to clear sources:", err);
            setError("Erro ao limpar fontes.");
        }
    };

    return (
        <div className="container mx-auto py-10">
            <div className="mb-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold">Histórico de Análises</h1>
                <div className="flex items-center gap-3">
                    <button onClick={() => navigate('/')} className="text-sm text-gray-600 hover:underline">Voltar</button>
                    <button onClick={fetchSources} className="text-sm text-gray-600 hover:underline">Atualizar</button>
                </div>
            </div>

            <div>
                {loading ? (
                    <div>Carregando...</div>
                ) : null}

                {error ? (
                    <div className="bg-red-50 border border-red-100 p-4 rounded-xl flex items-center gap-3 text-red-600">
                        <ShieldAlert className="w-6 h-6" />
                        {error}
                    </div>
                ) : sources.length === 0 ? (
                    <div className="bg-white border border-gray-100 rounded-2xl p-12 text-center shadow-sm">
                        <div className="bg-gray-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Globe className="w-8 h-8 text-gray-400" />
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">Nenhuma análise encontrada</h2>
                        <p className="text-gray-500 mb-6">Comece adicionando uma nova fonte no dashboard.</p>
                        <button
                            onClick={() => navigate('/')}
                            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Ir para Dashboard
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {sources.map(source => (
                            <div key={source.uid} className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
                                <div>
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="p-2 bg-blue-50 rounded-lg">
                                            <Globe className="w-5 h-5 text-blue-600" />
                                        </div>
                                        <StatusBadge score={source.inclusion_score ?? 0} />
                                    </div>
                                    <h3 className="font-bold text-gray-900 truncate" title={source.name}>{source.name}</h3>
                                    <p className="text-xs text-gray-400 truncate mt-1">{source.url}</p>
                                </div>

                                <div className="flex items-center gap-2 mt-5 pt-4 border-t border-gray-50">
                                    <button
                                        onClick={() => navigate('/', { state: { openChatId: source.uid, openChatName: source.name } })}
                                        className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors text-xs font-semibold"
                                    >
                                        <Eye className="w-3.5 h-3.5" />
                                        Ver
                                    </button>
                                    <button
                                        onClick={() => handleDelete(source.uid)}
                                        className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                                        title="Excluir"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default HistoryPage;
''',

    "backend/app/services/scraper.py": r'''from crawl4ai import AsyncWebCrawler
import logging
from urllib.parse import urlparse
import ipaddress
import socket

# Configure logger
logger = logging.getLogger(__name__)

def _is_public_http_url(url: str) -> bool:
    """
    Validate URL for scraping:
    - scheme must be http or https
    - hostname must resolve
    - resolved IP must not be private, loopback, link-local, multicast or reserved
    This reduces SSRF risk by blocking internal addresses.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            logger.warning("Blocked URL due to invalid scheme: %s", url)
            return False

        host = parsed.hostname
        if not host:
            logger.warning("Blocked URL due to missing hostname: %s", url)
            return False

        # Resolve hostname to IP(s)
        try:
            resolved_ip = socket.gethostbyname(host)
            ip = ipaddress.ip_address(resolved_ip)
        except Exception as e:
            logger.warning("Could not resolve host %s: %s — blocking for safety", host, str(e))
            return False

        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            logger.warning("Blocked URL because IP is private/loopback/link-local/reserved: %s -> %s", host, ip)
            return False

        return True
    except Exception as e:
        logger.exception("Unexpected error during URL validation: %s", str(e))
        return False

class SovereignScraper:
    @staticmethod
    async def scrape_url(url: str) -> str:
        """
        Scrapes the given URL using crawl4ai and returns the markdown content.
        Returns empty string on failure or when URL is considered unsafe.
        """
        try:
            logger.info(f"Starting crawl for URL: {url}")

            # Basic safety checks to mitigate SSRF
            if not _is_public_http_url(url):
                logger.error("URL blocked by SSRF protection: %s", url)
                return ""

            # Initialize with verbose=True for better debugging
            async with AsyncWebCrawler(verbose=True) as crawler:
                # Use arun to fetch content
                result = await crawler.arun(
                    url=url,
                    # Modern user agent to avoid being blocked
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    magic=True,  # Handle dynamic content/waiting
                    # Consider adding a max timeout in crawl4ai args if available
                )

                if not result.success:
                    logger.error(f"Failed to crawl {url}: {getattr(result, 'error_message', 'unknown')}")
                    return ""

                # Check for empty markdown
                if not result.markdown:
                    logger.warning(f"Zero length markdown returned for {url}. Raw HTML length: {len(result.html) if result.html else 0}")
                    return ""

                logger.info(f"Successfully scraped {len(result.markdown)} bytes from {url}")
                return result.markdown

        except Exception:
            logger.exception("Unhandled exception while crawling URL")
            return ""
''',

    "backend/app/api/v1/endpoints/sources.py": r'''from typing import List
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
'''
}

def apply_patches():
    print("🛡️ Iniciando aplicação do Patch de Segurança JINC...")
    base_dir = os.getcwd()
    print(f"📂 Diretório raiz: {base_dir}")

    for file_path, content in files.items():
        full_path = os.path.join(base_dir, file_path)
        dir_name = os.path.dirname(full_path)
        
        if not os.path.exists(dir_name):
            print(f"⚠️ Diretório não encontrado, criando: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)
            
        print(f"📝 Escrevendo: {file_path}")
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Sucesso.")
        except Exception as e:
            print(f"❌ Erro ao escrever {file_path}: {e}")

    print("\n🎉 Patch aplicado! Agora execute:")
    print("1. git add .")
    print("2. git commit -m 'fix(sec): unify inclusion_score and harden scraper against SSRF'")
    print("3. git push origin fix/security-unify-inclusion-ssrf-errors")

if __name__ == "__main__":
    apply_patches()