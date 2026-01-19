import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ShieldAlert, Globe, ArrowRight, History } from 'lucide-react';
import api from '../services/api';
import SourceCard from '../components/SourceCard';
import AddSourceInput from '../components/AddSourceInput';
import ChatConsole from '../components/ChatConsole';
import { Source } from '../types';

const Dashboard = () => {
    const [sources, setSources] = useState<Source[]>([]);
    const [activeChatSource, setActiveChatSource] = useState<{ id: string, name: string } | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const location = useLocation();
    const navigate = useNavigate();

    // Check if we navigated back from History with a source to open
    useEffect(() => {
        if (location.state?.openChatId) {
            setActiveChatSource({
                id: location.state.openChatId,
                name: location.state.openChatName
            });
            // Clear location state to avoid re-opening on refresh
            window.history.replaceState({}, document.title);
        }
    }, [location]);

    const fetchSources = async () => {
        try {
            const response = await api.get<{ sources: Source[] } | Source[]>('/sources/');
            let data: Source[] = [];
            if (Array.isArray(response.data)) {
                data = response.data;
            } else if (response.data && Array.isArray(response.data.sources)) {
                data = response.data.sources;
            }

            // Sort by UID descending (proxies for newest first)
            setSources(data.reverse());
        } catch (err) {
            console.error("🔥 FULL NETWORK ERROR:", err);
            setError("Falha na conexão: Verifique o console (F12)");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSources();
    }, []);

    const handleAnalyze = async (uid: string) => {
        try {
            await api.post(`/sources/${uid}/analyze`);
            await fetchSources();
        } catch (err) {
            console.error("Error analyzing source:", err);
            alert("Erro ao iniciar análise. Verifique o console.");
        }
    };

    const handleChatOpen = (uid: string, name: string) => {
        setActiveChatSource({ id: uid, name });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-50" aria-live="polite">
                <div className="text-lg text-gray-600 animate-pulse">Carregando fontes...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-50" role="alert">
                <div className="text-lg text-red-600 flex items-center gap-2">
                    <ShieldAlert className="w-6 h-6" aria-hidden="true" />
                    {error}
                </div>
            </div>
        );
    }

    // Limit to 3 latest
    const recentSources = sources.slice(0, 3);

    return (
        <div className="min-h-screen bg-gray-50 p-8 pb-32">
            <main className="max-w-4xl mx-auto">
                <header className="mb-8 flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <Globe className="w-8 h-8 text-blue-600" aria-hidden="true" />
                            EquiTracker SoberanAI
                        </h1>
                        <p className="text-gray-500 mt-2">Monitoramento Inteligente de Equidade e Inclusão</p>
                        <p className="text-gray-500 mt-1 text-sm">Arquitetura de Cérebro Híbrido (Grafos + IA Local) para insights sobre viés sistêmico e padrões de exclusão.</p>
                    </div>
                </header>

                <AddSourceInput onSourceAdded={fetchSources} />

                <section className="mt-12">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-bold text-gray-800">Análises Recentes</h2>
                        {sources.length > 3 && (
                            <button
                                onClick={() => navigate('/history')}
                                className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-semibold transition-colors"
                            >
                                <History className="w-4 h-4" />
                                Ver Tudo ({sources.length})
                            </button>
                        )}
                    </div>

                    {recentSources.length > 0 ? (
                        <>
                            <div
                                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                                role="list"
                                aria-label="Lista de fontes monitoradas"
                            >
                                {recentSources.map((source) => (
                                    <div key={source.uid || source.name} role="listitem">
                                        <SourceCard
                                            source={source}
                                            onAnalyze={handleAnalyze}
                                            onChatOpen={handleChatOpen}
                                            isActiveChat={activeChatSource?.id === source.uid}
                                        />
                                    </div>
                                ))}
                            </div>

                            <div className="mt-10 flex justify-center">
                                <button
                                    onClick={() => navigate('/history')}
                                    className="flex items-center gap-2 px-8 py-3 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-blue-200 hover:text-blue-600 transition-all shadow-sm font-semibold group"
                                >
                                    Ver todas as análises anteriores
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="text-center py-12 bg-white rounded-2xl border border-dashed border-gray-300">
                            <p className="text-gray-400">Nenhuma análise recente disponível.</p>
                        </div>
                    )}
                </section>

                {activeChatSource && (
                    <ChatConsole
                        sourceId={activeChatSource.id}
                        sourceName={activeChatSource.name}
                        onClose={() => setActiveChatSource(null)}
                    />
                )}
            </main>
        </div>
    );
};

export default Dashboard;
