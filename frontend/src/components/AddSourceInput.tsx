import { useState } from 'react';
import { Plus, Search, Loader2 } from 'lucide-react';
import api from '../services/api';

interface AddSourceInputProps {
    onSourceAdded: () => void;
}

const AddSourceInput = ({ onSourceAdded }: AddSourceInputProps) => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [submittingStatus, setSubmittingStatus] = useState<string>('');

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url.trim()) return;

        setLoading(true);
        setSubmittingStatus('Adicionando...');

        try {
            // 1. Create source
            const createRes = await api.post('/sources/', { url });
            const newUid = createRes.data.uid;

            // 2. Trigger analysis
            setSubmittingStatus('Analisando...');
            await api.post(`/sources/${newUid}/analyze`);

            // 3. Refresh list
            onSourceAdded();
            setUrl('');
        } catch (error) {
            console.error("Failed to add source:", error);
            alert("Erro ao adicionar fonte. Verifique a URL e tente novamente.");
        } finally {
            setLoading(false);
            setSubmittingStatus('');
        }
    };

    return (
        <form onSubmit={handleAdd} className="mb-8 w-full max-w-2xl mx-auto">
            <div className="relative flex items-center">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                    type="url"
                    className="block w-full pl-10 pr-32 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 sm:text-sm shadow-sm transition-all"
                    placeholder="Cole a URL da notícia ou site..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={loading}
                    required
                />
                <button
                    type="submit"
                    disabled={loading}
                    className="absolute inset-y-1 right-1 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            {submittingStatus}
                        </>
                    ) : (
                        <>
                            <Plus className="w-4 h-4" />
                            Adicionar e Analisar
                        </>
                    )}
                </button>
            </div>
        </form>
    );
};

export default AddSourceInput;
