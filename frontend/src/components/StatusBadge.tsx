import React from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

interface StatusBadgeProps {
    score: number;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ score }) => {
    const isReliable = score >= 0.8;
    const percentage = Math.round(score * 100);

    return (
        <div
            className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${isReliable ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}
            role="status"
            aria-label={`Reliability Score: ${percentage}% - ${isReliable ? 'Good' : 'Needs Attention'}`}
        >
            {isReliable ? <ShieldCheck className="w-4 h-4" aria-hidden="true" /> : <ShieldAlert className="w-4 h-4" aria-hidden="true" />}
            <span>{percentage}%</span>
            <span className="sr-only">{isReliable ? 'Reliable' : 'Caution'}</span>
        </div>
    );
};

export default StatusBadge;
