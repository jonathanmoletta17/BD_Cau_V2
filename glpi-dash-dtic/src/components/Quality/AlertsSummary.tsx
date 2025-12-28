import React from 'react';
import { AlertTriangle, CheckCircle, AlertCircle, Shield } from 'lucide-react';
import { QualityStats } from '../../types';

interface AlertsSummaryProps {
    stats: QualityStats | null;
    loading?: boolean;
    activeFilter?: 'HIGH' | 'MEDIUM' | 'AFFECTED' | 'RULES' | null;
    onFilterClick?: (filter: 'HIGH' | 'MEDIUM' | 'AFFECTED' | 'RULES' | null) => void;
}

export const AlertsSummary: React.FC<AlertsSummaryProps> = ({ stats, loading, activeFilter, onFilterClick }) => {
    if (loading) {
        return <div className="animate-pulse bg-gray-800 rounded-lg p-6 h-32 w-full"></div>;
    }

    if (!stats) return null;

    return (
        <div className="bg-[#1e293b] rounded-lg p-6 border border-slate-700 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
                <Shield className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-slate-100">Monitoramento de Qualidade</h3>
            </div>

            <div className="grid grid-cols-4 gap-4">
                <div
                    className={`bg-red-500/10 border rounded-lg p-4 flex flex-col items-center cursor-pointer transition-all hover:bg-red-500/20 ${activeFilter === 'HIGH' ? 'border-red-500 ring-2 ring-red-500/50' : 'border-red-500/20'
                        }`}
                    onClick={() => onFilterClick?.(activeFilter === 'HIGH' ? null : 'HIGH')}
                >
                    <div className="flex items-center gap-2 text-red-500 mb-1">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Críticos</span>
                    </div>
                    <span className="text-2xl font-bold text-red-400">{stats.high}</span>
                </div>

                <div
                    className={`bg-yellow-500/10 border rounded-lg p-4 flex flex-col items-center cursor-pointer transition-all hover:bg-yellow-500/20 ${activeFilter === 'MEDIUM' ? 'border-yellow-500 ring-2 ring-yellow-500/50' : 'border-yellow-500/20'
                        }`}
                    onClick={() => onFilterClick?.(activeFilter === 'MEDIUM' ? null : 'MEDIUM')}
                >
                    <div className="flex items-center gap-2 text-yellow-500 mb-1">
                        <AlertTriangle className="w-4 h-4" />
                        <span className="text-sm font-medium">Atenção</span>
                    </div>
                    <span className="text-2xl font-bold text-yellow-400">{stats.medium}</span>
                </div>

                <div
                    className={`bg-blue-500/10 border rounded-lg p-4 flex flex-col items-center cursor-pointer transition-all hover:bg-blue-500/20 ${activeFilter === 'AFFECTED' ? 'border-blue-500 ring-2 ring-blue-500/50' : 'border-blue-500/20'
                        }`}
                    onClick={() => onFilterClick?.(activeFilter === 'AFFECTED' ? null : 'AFFECTED')}
                >
                    <div className="flex items-center gap-2 text-blue-500 mb-1">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Tickets Afetados</span>
                    </div>
                    <span className="text-2xl font-bold text-blue-400">{stats.affected_tickets}</span>
                </div>

                <div
                    className={`bg-slate-700/30 border rounded-lg p-4 flex flex-col items-center cursor-pointer transition-all hover:bg-slate-700/50 ${activeFilter === 'RULES' ? 'border-slate-400 ring-2 ring-slate-400/50' : 'border-slate-600'
                        }`}
                    onClick={() => onFilterClick?.(activeFilter === 'RULES' ? null : 'RULES')}
                >
                    <div className="text-slate-400 text-sm mb-1">Regras Ativas</div>
                    <span className="text-xl font-bold text-slate-200">{stats.active_rules}</span>
                </div>
            </div>
        </div>
    );
};
