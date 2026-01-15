import React from 'react';
import { Globe } from 'lucide-react';
import { Source } from '../types';
import StatusBadge from './StatusBadge';

interface SourceCardProps {
    source: Source;
}

const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
    return (
        <article className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
                <div className="p-2 bg-blue-50 rounded-lg">
                    <Globe className="w-6 h-6 text-blue-600" aria-hidden="true" />
                </div>
                <StatusBadge score={source.reliability_score} />
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">{source.name}</h3>
            <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-gray-500 hover:text-blue-600 truncate block"
                aria-label={`Visit ${source.name} at ${source.url}`}
            >
                {source.url}
            </a>

            <button
                className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                aria-label={`Analyze ${source.name} reliability`}
            >
                Analyze
            </button>
        </article>
    );
};

export default SourceCard;
