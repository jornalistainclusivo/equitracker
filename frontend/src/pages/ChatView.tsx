import React, { useState, useEffect } from 'react';
import { Menu, Send, Globe, Loader2 } from 'lucide-react';
import { getSources, createSource, analyzeSource } from '../api';
import { Source } from '../types';

export default function ChatView() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [prompt, setPrompt] = useState('');
  const [history, setHistory] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeSource, setActiveSource] = useState<Source | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await getSources();
      setHistory(data);
    } catch (error) {
      console.error('Failed to fetch history', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    const url = prompt.trim();
    setPrompt('');
    
    try {
      // 1. Create source
      const newSource = await createSource(url);
      setActiveSource(newSource);
      
      // 2. Trigger analysis
      const analysis = await analyzeSource(newSource.uid);
      
      // 3. Update view with results
      const updatedSource = { 
          ...newSource, 
          inclusion_score: analysis.inclusion_score, 
          reasoning: analysis.reasoning 
      };
      
      setActiveSource(updatedSource);
      await fetchHistory();
    } catch (error) {
      console.error('Analysis failed', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans overflow-hidden">
      
      {/* ================= SIDEBAR ================= */}
      <aside 
        className={`${isSidebarOpen ? 'w-72' : 'w-0'} transition-all duration-300 bg-white border-r border-gray-200 flex flex-col`}
        aria-label="Histórico de análises"
      >
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <h1 className="text-lg font-bold text-gray-800 flex items-center gap-2">
            <Globe className="text-blue-600 w-5 h-5" />
            EquiTracker
          </h1>
        </div>
        <nav className="flex-1 overflow-y-auto p-3 space-y-2">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 px-2">
            Fontes Analisadas
          </div>
          {history.map((item) => (
            <button 
              key={item.uid}
              onClick={() => setActiveSource(item)}
              className={`w-full text-left px-3 py-3 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-600 transition-colors flex justify-between items-center group ${activeSource?.uid === item.uid ? 'bg-blue-50' : ''}`}
            >
              <span className="truncate text-sm font-medium text-gray-700 group-hover:text-gray-900 flex-1">
                {item.name}
              </span>
              {item.inclusion_score !== undefined && item.inclusion_score !== null && (
                <span className="text-xs font-bold px-2 py-1 bg-green-100 text-green-800 rounded-full ml-2">
                  {item.inclusion_score}
                </span>
              )}
            </button>
          ))}
        </nav>
      </aside>

      {/* ================= MAIN AREA ================= */}
      <main className="flex-1 flex flex-col h-full bg-white relative">
        <header className="h-14 border-b border-gray-200 flex items-center px-4">
          <button 
            onClick={() => setSidebarOpen(!isSidebarOpen)}
            className="p-2 -ml-2 rounded-md hover:bg-gray-100 focus:ring-2 focus:ring-blue-600 focus:outline-none text-gray-600"
            aria-label={isSidebarOpen ? "Fechar painel" : "Abrir painel"}
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="ml-4 font-semibold text-gray-700">
            {activeSource ? activeSource.name : "Nova Análise"}
          </span>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-8 flex justify-center" aria-live="polite" aria-atomic="true">
          {!activeSource && !loading && (
            <div className="max-w-3xl w-full flex flex-col items-center justify-center text-center space-y-6 mt-12">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                <Globe className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Auditoria de Viés Interseccional</h2>
              <p className="text-gray-600 max-w-lg">
                Cole a URL de uma matéria. O Cérebro Híbrido analisará padrões de exclusão e equidade.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full mt-8">
                <button 
                    className="p-4 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50 focus:ring-2 focus:ring-blue-600 transition-all text-left"
                    onClick={() => setPrompt("https://example.com/noticia1")}
                >
                  <strong className="block text-gray-800 mb-1">Verificar Fatos ⚖️</strong>
                  Extraia as alegações centrais.
                </button>
                <button 
                    className="p-4 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50 focus:ring-2 focus:ring-blue-600 transition-all text-left"
                    onClick={() => setPrompt("https://example.com/noticia2")}
                >
                  <strong className="block text-gray-800 mb-1">Resumo Inclusivo 📝</strong>
                  Quais vozes estão ausentes?
                </button>
              </div>
            </div>
          )}

          {loading && (
             <div className="flex flex-col items-center justify-center mt-20 space-y-4" role="status">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                <p className="text-gray-500 font-medium">O Cérebro Híbrido está analisando a fonte...</p>
             </div>
          )}

          {activeSource && !loading && (
              <div className="max-w-3xl w-full flex flex-col space-y-6 mt-8" role="log">
                {/* User Prompt Bubble */}
                <div className="self-end bg-gray-100 text-gray-900 px-6 py-4 rounded-2xl rounded-tr-sm max-w-[85%]">
                    <p className="text-sm break-all font-medium">
                        URL Analisada: <a href={activeSource.url} target="_blank" rel="noreferrer" className="text-blue-600 underline focus:ring-2 focus:ring-blue-600">{activeSource.url}</a>
                    </p>
                </div>

                {/* AI Response Bubble */}
                <div className="self-start flex flex-col w-full">
                    <div className="flex items-center gap-3 mb-2">
                         <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                             <Globe className="w-5 h-5 text-blue-600" />
                         </div>
                         <span className="font-semibold text-gray-800">EquiTracker Engine</span>
                    </div>
                    
                    <div className="bg-white border border-gray-200 p-6 rounded-2xl rounded-tl-sm shadow-sm space-y-4">
                        {activeSource.inclusion_score !== undefined ? (
                            <div className="flex items-center gap-3 border-b border-gray-100 pb-4 mb-4">
                                <div className="flex flex-col">
                                    <span className="text-xs text-gray-500 font-bold uppercase tracking-wider">Score de Inclusão</span>
                                    <div className="flex items-baseline gap-2">
                                        <span className={`text-4xl font-black ${
                                            activeSource.inclusion_score >= 80 ? 'text-green-600' :
                                            activeSource.inclusion_score >= 50 ? 'text-yellow-600' : 'text-red-600'
                                        }`}>
                                            {activeSource.inclusion_score}
                                        </span>
                                        <span className="text-sm font-medium text-gray-400">/ 100</span>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <p className="text-gray-500 italic">Score não disponível.</p>
                        )}
                        
                        <div>
                            <h3 className="text-sm font-bold text-gray-900 mb-2">Análise Interseccional</h3>
                            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                                {activeSource.reasoning || "Nenhuma justificativa disponível."}
                            </p>
                        </div>
                    </div>
                </div>
              </div>
          )}
        </div>

        <div className="p-4 bg-white border-t border-transparent bg-gradient-to-t from-white via-white to-transparent">
          <div className="max-w-3xl mx-auto relative">
            <form onSubmit={handleSubmit}>
              <input 
                type="url"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Cole uma URL para analisar..."
                disabled={loading}
                required
                className="w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-2xl py-4 pl-4 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-600 shadow-sm disabled:opacity-50 transition-shadow"
              />
              <button 
                type="submit"
                disabled={!prompt.trim() || loading}
                aria-label="Analisar Fonte"
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 disabled:bg-gray-300 transition-colors"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
