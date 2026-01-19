import React from 'react';
import { ShieldCheck, ShieldAlert, Shield } from 'lucide-react';

interface StatusBadgeProps {
    score?: number;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ score }) => {
    // Handle null, undefined, or invalid scores
    if (score === undefined || score === null || isNaN(score)) {
        return (
            <div
                className="flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-600"
                role="status"
                aria-label="Inclusão: Pendente"
            >
                <Shield className="w-4 h-4" aria-hidden="true" />
                <span>Pendente</span>
            </div>
        );
    }

    // Score is 0-100
    // 0-20: Critical
    // 21-50: Warning
    // 51-80: Good
    // 81-100: Excellent

    let colorClass = 'bg-gray-100 text-gray-800';
    let icon = <Shield className="w-4 h-4" />;
    let label = 'Desconhecido';

    if (score >= 80) {
        colorClass = 'bg-green-100 text-green-800';
        icon = <ShieldCheck className="w-4 h-4" />;
        label = 'Excelente';
    } else if (score >= 50) {
        colorClass = 'bg-blue-100 text-blue-800';
        icon = <ShieldCheck className="w-4 h-4" />;
        label = 'Bom';
    } else if (score >= 20) {
        colorClass = 'bg-yellow-100 text-yellow-800';
        icon = <ShieldAlert className="w-4 h-4" />;
        label = 'Atenção';
    } else {
        colorClass = 'bg-red-100 text-red-800';
        icon = <ShieldAlert className="w-4 h-4" />;
        label = 'Crítico';
    }

    return (
        <div
            className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${colorClass}`}
            role="status"
            aria-label={`Índice de Inclusão: ${score} - ${label}`}
            title="Índice de Inclusão (0-100)"
        >
            {icon}
            <span>{score}</span>
            <span className="sr-only">{label}</span>
        </div>
    );
};

export default StatusBadge;
