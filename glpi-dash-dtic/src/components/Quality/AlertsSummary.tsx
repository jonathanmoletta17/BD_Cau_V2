import React from 'react';
import { AlertTriangle, CheckCircle, AlertCircle, Shield } from 'lucide-react';
import { QualityStats } from '../../types';

interface AlertsSummaryProps {
    stats: QualityStats | null;
    loading?: boolean;
}

export const AlertsSummary: React.FC<AlertsSummaryProps> = ({ stats, loading }) => {
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
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex flex-col items-center">
                    <div className="flex items-center gap-2 text-red-500 mb-1">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Críticos</span>
                    </div>
                    <span className="text-2xl font-bold text-red-400">{stats.high}</span>
                </div>

                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 flex flex-col items-center">
                    <div className="flex items-center gap-2 text-yellow-500 mb-1">
                        <AlertTriangle className="w-4 h-4" />
                        <span className="text-sm font-medium">Atenção</span>
                    </div>
                    <span className="text-2xl font-bold text-yellow-400">{stats.medium}</span>
                </div>

                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 flex flex-col items-center">
                    <div className="flex items-center gap-2 text-blue-500 mb-1">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Tickets Afetados</span>
                    </div>
                    <span className="text-2xl font-bold text-blue-400">{stats.affected_tickets}</span>
                </div>

                <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 flex flex-col items-center">
                    <div className="text-slate-400 text-sm mb-1">Regras Ativas</div>
                    <span className="text-xl font-bold text-slate-200">{stats.active_rules}</span>
                </div>
            </div>
        </div>
    );
};
