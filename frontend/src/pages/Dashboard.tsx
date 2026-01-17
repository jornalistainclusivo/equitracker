import { useEffect, useState } from 'react';
import { ShieldAlert, Globe } from 'lucide-react';
import api from '../services/api';
import SourceCard from '../components/SourceCard';
import AddSourceInput from '../components/AddSourceInput';
import { Source } from '../types';

const Dashboard = () => {
    const [sources, setSources] = useState<Source[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchSources = async () => {
        try {
            // Strictly typed API response
            const response = await api.get<{ sources: Source[] } | Source[]>('/sources/');

            // Handle potential response variations safely
            let data: Source[] = [];
            if (Array.isArray(response.data)) {
                data = response.data;
            } else if (response.data && Array.isArray(response.data.sources)) {
                data = response.data.sources;
            }

            setSources(data);
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
            // Initial crawl/analysis might just kick off a process, ensuring we refetch to get latest state/score
            // Using a slight delay or optimistic update could be better, but refetching is safe first step
            await fetchSources();
        } catch (err) {
            console.error("Error analyzing source:", err);
            // Optionally set error state or show toast
            alert("Erro ao iniciar análise. Verifique o console.");
        }
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

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <main className="max-w-4xl mx-auto">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <Globe className="w-8 h-8 text-blue-600" aria-hidden="true" />
                        Monitor de Fontes
                    </h1>
                    <p className="text-gray-500 mt-2">Rastreamento de confiabilidade jornalística</p>
                </header>

                <AddSourceInput onSourceAdded={fetchSources} />

                <div
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    role="list"
                    aria-label="Lista de fontes monitoradas"
                >
                    {sources.map((source) => (
                        <div key={source.uid || source.name} role="listitem">
                            <SourceCard source={source} onAnalyze={handleAnalyze} />
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
