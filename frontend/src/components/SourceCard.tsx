import React, { useState } from 'react';
import { Globe, MessageSquare } from 'lucide-react';
import { Source } from '../types';
import StatusBadge from './StatusBadge';
import SourceChat from './SourceChat';

interface SourceCardProps {
    source: Source;
    onAnalyze: (uid: string) => Promise<void>;
}

const SourceCard: React.FC<SourceCardProps> = ({ source, onAnalyze }) => {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isChatOpen, setIsChatOpen] = useState(false);

    const handleAnalyzeClick = async () => {
        setIsAnalyzing(true);
        try {
            await onAnalyze(source.uid);
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <article className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
                <div className="p-2 bg-blue-50 rounded-lg">
                    <Globe className="w-6 h-6 text-blue-600" aria-hidden="true" />
                </div>
                {/* Fixed: Access reliability instead of reliability_score */}
                <StatusBadge score={source.reliability} />
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">{source.name}</h3>
            <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-gray-500 hover:text-blue-600 truncate block"
                aria-label={`Visitar ${source.name} em ${source.url}`}
            >
                {source.url}
            </a>

            <div className="flex gap-2 mt-4">
                <button
                    onClick={handleAnalyzeClick}
                    disabled={isAnalyzing}
                    className={`flex-1 px-4 py-2 text-white rounded-lg transition-colors text-sm font-medium ${isAnalyzing ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                        }`}
                    aria-label={`Analisar confiabilidade de ${source.name}`}
                >
                    {isAnalyzing ? 'Analisando...' : 'Analisar'}
                </button>

                <button
                    onClick={() => setIsChatOpen(!isChatOpen)}
                    className={`px-4 py-2 rounded-lg transition-colors text-sm font-medium border ${isChatOpen
                            ? 'bg-blue-50 border-blue-200 text-blue-700'
                            : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                        }`}
                    aria-label={`Chat com ${source.name}`}
                >
                    <MessageSquare className="w-5 h-5" />
                </button>
            </div>

            {isChatOpen && (
                <SourceChat
                    sourceUid={source.uid}
                    sourceName={source.name}
                    onClose={() => setIsChatOpen(false)}
                />
            )}
        </article>
    );
};

export default SourceCard;
