import { useEffect, useState } from 'react';
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
