import React from 'react';
import { QualityAlert } from '../../types';
import { RefreshCw, ExternalLink } from 'lucide-react';

interface ViolationsTableProps {
    alerts: QualityAlert[];
    loading?: boolean;
    onRefresh?: () => void;
}

const severityColor = (severity: string) => {
    switch (severity) {
        case 'HIGH': return 'bg-red-500/10 text-red-400 border-red-500/20';
        case 'MEDIUM': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
        case 'LOW': return 'bg-green-500/10 text-green-400 border-green-500/20';
        default: return 'bg-slate-500/10 text-slate-400';
    }
};

const ruleName = (ruleId: string) => {
    switch (ruleId) {
        case 'R01': return 'Novo > 24h';
        case 'R03': return 'Sem Técnico';
        case 'R04': return 'Sem Grupo';
        case 'R10': return 'Pendente > 7d';
        case 'R06': return 'Sem Followup';
        default: return ruleId;
    }
}

export const ViolationsTable: React.FC<ViolationsTableProps> = ({ alerts, loading, onRefresh }) => {
    // Safety check for undefined alerts
    const safeAlerts = alerts || [];

    if (loading && safeAlerts.length === 0) {
        return <div className="text-center text-slate-400 p-8">Carregando violações...</div>;
    }

    if (safeAlerts.length === 0) {
        return (
            <div className="bg-[#1e293b] rounded-lg p-6 border border-slate-700 text-center">
                <p className="text-slate-400">Nenhuma violação de qualidade detectada ativos. Parabéns!</p>
            </div>
        );
    }

    return (
        <div className="bg-[#1e293b] rounded-lg border border-slate-700 overflow-hidden">
            <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-800/50">
                <h3 className="font-semibold text-slate-100">Violações Recentes</h3>
                {onRefresh && (
                    <button
                        onClick={onRefresh}
                        className="p-2 hover:bg-slate-700 rounded-full text-slate-400 transition-colors"
                        title="Executar verificação agora"
                    >
                        <RefreshCw className="w-4 h-4" />
                    </button>
                )}
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="bg-slate-800/80 text-slate-400 uppercase text-xs">
                        <tr>
                            <th className="px-4 py-3">Gravidade</th>
                            <th className="px-4 py-3">Regra</th>
                            <th className="px-4 py-3">Ticket</th>
                            <th className="px-4 py-3">Título</th>
                            <th className="px-4 py-3">Responsável</th>
                            <th className="px-4 py-3 text-right">Ação</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/50">
                        {safeAlerts.map((alert) => (
                            <tr key={alert.id} className="hover:bg-slate-700/30 transition-colors">
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-1 rounded text-xs font-medium border ${severityColor(alert.severity)}`}>
                                        {alert.severity}
                                    </span>
                                </td>
                                <td className="px-4 py-3 font-medium text-slate-300">
                                    {ruleName(alert.rule_id)}
                                </td>
                                <td className="px-4 py-3 text-slate-400">#{alert.glpi_id || alert.ticket_id}</td>
                                <td className="px-4 py-3 text-slate-300 max-w-xs truncate" title={alert.titulo}>
                                    {alert.titulo || 'Sem título'}
                                </td>
                                <td className="px-4 py-3 text-slate-400">
                                    {alert.tecnico !== 'Sem Técnico' ? alert.tecnico : <span className="text-orange-400/80 italic">Não atribuído</span>}
                                </td>
                                <td className="px-4 py-3 text-right">
                                    <a
                                        href={`http://glpi-dtic.com/front/ticket.form.php?id=${alert.ticket_id}`} // Adjust URL as needed
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 text-xs"
                                    >
                                        Ver <ExternalLink className="w-3 h-3" />
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
