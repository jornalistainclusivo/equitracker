import { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert, Globe } from 'lucide-react';
import api from '../services/api';

interface Source {
    name: string;
    url: string;
    reliability_score: number;
}

const Dashboard = () => {
    const [sources, setSources] = useState<Source[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSources = async () => {
            try {
                const response = await api.get<{ sources: Source[] }>('/sources/');
                // Handle potentially different response structures if needed, 
                // strictly following instructions to fetch "list of sources".
                // Assuming the API returns { sources: [...] } or just [...]
                // Based on typical backend patterns, let's assume it returns the list directly or in a wrapper.
                // We might need to adjust based on the actual backend response.
                // For now, I'll assume standard DRF/FastAPI pattern. 
                // If the backend returns a list directly:
                const data = Array.isArray(response.data) ? response.data : response.data.sources || [];
                setSources(data);
            } catch (err) {
                console.error("🔥 FULL NETWORK ERROR:", err);
                setError("Connection Failed: Check Console (F12)");
            } finally {
                setLoading(false);
            }
        };

        fetchSources();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-50">
                <div className="text-lg text-gray-600 animate-pulse">Loading sources...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-50">
                <div className="text-lg text-red-600 flex items-center gap-2">
                    <ShieldAlert className="w-6 h-6" />
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-4xl mx-auto">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <Globe className="w-8 h-8 text-blue-600" />
                        Source Monitor
                    </h1>
                    <p className="text-gray-500 mt-2">Tracking data source reliability and status</p>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {sources.map((source, index) => (
                        <div
                            key={index}
                            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="p-2 bg-blue-50 rounded-lg">
                                    <Globe className="w-6 h-6 text-blue-600" />
                                </div>
                                <div className={`flex items-center gap-1 text-sm font-medium ${source.reliability_score >= 0.8 ? 'text-green-600' : 'text-yellow-600'
                                    }`}>
                                    <ShieldCheck className="w-4 h-4" />
                                    {Math.round(source.reliability_score * 100)}%
                                </div>
                            </div>

                            <h3 className="text-lg font-semibold text-gray-900 mb-2">{source.name}</h3>
                            <a
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-gray-500 hover:text-blue-600 truncate block"
                            >
                                {source.url}
                            </a>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
