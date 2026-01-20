import { useState } from 'react';
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
