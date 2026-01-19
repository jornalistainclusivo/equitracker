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
                reliability: 0.5, // Default initial value required by schema
                notes: "Adicionado via Dashboard"
            };

            const createRes = await api.post('/sources/', payload);
            const newUid = createRes.data.uid;

            // 2. Trigger analysis
            setSubmittingStatus('Analisando confiabilidade...');
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
                        <Globe className="h-6 w-6 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                    </div>
                    <input
                        type="url"
                        className="block w-full pl-12 pr-36 h-14 text-lg border-2 border-gray-200 rounded-full leading-5 bg-white placeholder-gray-400 focus:outline-none focus:placeholder-gray-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all shadow-sm"
                        placeholder="Cole a URL para rastrear aqui..."
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        disabled={loading}
                        required
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="absolute inset-y-1.5 right-1.5 px-6 rounded-full text-base font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-md hover:shadow-lg"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                {submittingStatus || 'Processando'}
                            </>
                        ) : (
                            <>
                                Analisar
                                <ArrowRight className="w-5 h-5" />
                            </>
                        )}
                    </button>
                </div>
            </form>

            {errorMsg && (
                <div className="mt-4 flex items-center gap-2 text-red-600 bg-red-50 px-4 py-2 rounded-lg text-sm font-medium animate-in fade-in slide-in-from-top-2">
                    <AlertCircle className="w-4 h-4" />
                    {errorMsg}
                </div>
            )}
        </div>
    );
};

export default AddSourceInput;
