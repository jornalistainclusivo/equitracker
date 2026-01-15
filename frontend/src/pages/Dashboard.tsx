import { useEffect, useState } from 'react';
import { ShieldAlert, Globe } from 'lucide-react';
import api from '../services/api';
import SourceCard from '../components/SourceCard';
import { Source } from '../types';

const Dashboard = () => {
    const [sources, setSources] = useState<Source[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
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
                setError("Connection Failed: Check Console (F12)");
            } finally {
                setLoading(false);
            }
        };

        fetchSources();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-50" aria-live="polite">
                <div className="text-lg text-gray-600 animate-pulse">Loading sources...</div>
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
                        Source Monitor
                    </h1>
                    <p className="text-gray-500 mt-2">Tracking data source reliability and status</p>
                </header>

                <div
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    role="list"
                    aria-label="List of monitored data sources"
                >
                    {sources.map((source, index) => (
                        <div key={index} role="listitem">
                            <SourceCard source={source} />
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
