import React from 'react';
import { QualityAlert } from '../../types';
import { RefreshCw, ExternalLink, AlertTriangle, AlertOctagon, Info, ChevronRight, Activity, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ViolationsTableProps {
    alerts: QualityAlert[];
    loading?: boolean;
    onRefresh?: () => void;
    activeFilter?: 'HIGH' | 'MEDIUM' | 'AFFECTED' | 'RULES' | null;
}

const getSeverityStyles = (severity: string) => {
    switch (severity) {
        case 'HIGH':
            return {
                border: 'border-red-500/40',
                bg: 'bg-red-900/10',
                text: 'text-red-400',
                icon: <AlertOctagon className="w-4 h-4" />,
                pulse: true
            };
        case 'MEDIUM':
            return {
                border: 'border-yellow-500/40',
                bg: 'bg-yellow-900/10',
                text: 'text-yellow-400',
                icon: <AlertTriangle className="w-4 h-4" />,
                pulse: false
            };
        case 'LOW':
            return {
                border: 'border-green-500/40',
                bg: 'bg-green-900/10',
                text: 'text-green-400',
                icon: <Info className="w-4 h-4" />,
                pulse: false
            };
        default:
            return {
                border: 'border-slate-500/40',
                bg: 'bg-slate-800/50',
                text: 'text-slate-400',
                icon: <Info className="w-4 h-4" />,
                pulse: false
            };
    }
};

const ruleName = (ruleId: string) => {
    switch (ruleId) {
        case 'R01': return 'Novo > 24h';
        case 'R02': return 'Novo c/ Técnico > 1h';
        case 'R03': return 'Sem Técnico';
        case 'R04': return 'Sem Grupo';
        case 'R05': return 'Sem Categoria';
        case 'R06': return 'Sem Followup';
        case 'R10': return 'Pendente > 7d';
        case 'R13': return 'S/ Interação 72h';
        default: return ruleName(ruleId) || ruleId;
    }
}

export const ViolationsTable = (props: ViolationsTableProps) => {
    const { alerts, loading, onRefresh, activeFilter } = props;
    const safeAlerts = alerts || [];

    // Filter Logic
    const filteredAlerts = React.useMemo(() => {
        if (activeFilter === 'HIGH') return safeAlerts.filter(a => a.severity === 'HIGH');
        if (activeFilter === 'MEDIUM') return safeAlerts.filter(a => a.severity === 'MEDIUM');
        return safeAlerts;
    }, [safeAlerts, activeFilter]);

    // Grouping Logic for RULES view
    const rulesSummary = React.useMemo(() => {
        if (activeFilter !== 'RULES') return [];
        const groups: Record<string, { count: number, ruleId: string }> = {};
        safeAlerts.forEach(alert => {
            if (!groups[alert.rule_id]) {
                groups[alert.rule_id] = { count: 0, ruleId: alert.rule_id };
            }
            groups[alert.rule_id].count++;
        });
        return Object.values(groups).sort((a, b) => b.count - a.count);
    }, [safeAlerts, activeFilter]);

    // Grouping Logic for AFFECTED TICKETS view
    const affectedTickets = React.useMemo(() => {
        if (activeFilter !== 'AFFECTED') return [];
        const groups: Record<number, { count: number, maxSeverity: string, ticketId: number, title: string, technician: string }> = {};
        safeAlerts.forEach(alert => {
            if (!groups[alert.ticket_id]) {
                groups[alert.ticket_id] = {
                    count: 0,
                    maxSeverity: 'LOW',
                    ticketId: alert.ticket_id,
                    title: alert.titulo || 'Sem título',
                    technician: alert.tecnico || 'Sem técnico'
                };
            }
            groups[alert.ticket_id].count++;
            if (alert.severity === 'HIGH') groups[alert.ticket_id].maxSeverity = 'HIGH';
            else if (alert.severity === 'MEDIUM' && groups[alert.ticket_id].maxSeverity !== 'HIGH') groups[alert.ticket_id].maxSeverity = 'MEDIUM';
        });
        return Object.values(groups).sort((a, b) => b.count - a.count);
    }, [safeAlerts, activeFilter]);

    const getTitle = () => {
        switch (activeFilter) {
            case 'HIGH': return 'Violações Críticas';
            case 'MEDIUM': return 'Violações de Atenção';
            case 'RULES': return 'Regras Mais Violadas';
            case 'AFFECTED': return 'Tickets Mais Afetados';
            default: return 'Todas as Violações';
        }
    };

    // Render Helpers
    const renderRules = () => (
        <motion.div key="view-rules" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {rulesSummary.map((rule) => (
                <div
                    key={rule.ruleId}
                    className="bg-slate-800/50 p-3 rounded border border-slate-700 flex items-center justify-between mb-2"
                >
                    <div className="flex items-center gap-3">
                        <div className="bg-slate-700 p-2 rounded">
                            <Activity className="w-4 h-4 text-purple-400" />
                        </div>
                        <div>
                            <h4 className="font-medium text-slate-200">{ruleName(rule.ruleId)}</h4>
                            <span className="text-xs text-slate-500">{rule.ruleId}</span>
                        </div>
                    </div>
                    <div className="text-xl font-bold text-slate-300">{rule.count}</div>
                </div>
            ))}
            {rulesSummary.length === 0 && <div className="text-slate-500 text-center py-4">Nenhuma regra ativa</div>}
        </motion.div>
    );

    const renderAffected = () => (
        <motion.div key="view-affected" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {affectedTickets.map((ticket) => {
                const styles = getSeverityStyles(ticket.maxSeverity);
                return (
                    <div
                        key={ticket.ticketId}
                        className={`bg-slate-800/50 p-3 rounded border border-slate-700/50 hover:border-slate-600 transition-colors group mb-2`}
                    >
                        <div className="flex justify-between items-start mb-1">
                            <div className="flex items-center gap-2">
                                <span className="text-xs font-mono text-blue-400 bg-blue-400/10 px-1 rounded">#{ticket.ticketId}</span>
                                <span className={`text-[10px] px-1.5 py-0.5 rounded border ${styles.border} ${styles.text} bg-opacity-10`}>
                                    {ticket.count} violações
                                </span>
                            </div>
                            <a
                                href={`http://glpi-dtic.com/front/ticket.form.php?id=${ticket.ticketId}`}
                                target="_blank"
                                rel="noreferrer"
                                className="text-slate-500 hover:text-white transition-colors"
                            >
                                <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                        <div className="text-sm text-slate-300 font-medium truncate mb-1">{ticket.title}</div>
                        <div className="text-xs text-slate-500">{ticket.technician}</div>
                    </div>
                );
            })}
        </motion.div>
    );

    const renderList = () => (
        <motion.div
            key={`view-list-${activeFilter || 'all'}`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-2"
        >
            {filteredAlerts.map((alert, index) => {
                const styles = getSeverityStyles(alert.severity);
                return (
                    <div
                        key={alert.id || `alert-${index}`}
                        className={`
                            relative p-3 rounded-md border ${styles.border} ${styles.bg}
                            hover:bg-opacity-20 transition-all group shrink-0 mb-2
                        `}
                    >
                        {styles.pulse && (
                            <div className="absolute inset-0 bg-red-500/5 rounded-md pointer-events-none animate-pulse" />
                        )}
                        <div className="flex justify-between items-start gap-3 relative z-10">
                            <div className="flex items-start gap-3 min-w-0 flex-1">
                                <div className={`mt-1 shrink-0 ${styles.text}`}>
                                    {styles.icon}
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`text-xs font-bold px-1.5 py-0.5 rounded border border-opacity-30 ${styles.border} ${styles.text}`}>
                                            {alert.severity}
                                        </span>
                                        <span className="text-white font-medium text-sm truncate">
                                            {ruleName(alert.rule_id)}
                                        </span>
                                    </div>
                                    <p className="text-slate-300 text-xs truncate mb-1" title={alert.titulo}>
                                        {alert.titulo || 'Sem título'}
                                    </p>
                                    <div className="flex items-center gap-2 text-[10px] text-slate-500">
                                        <span className="font-mono text-slate-400">#{alert.glpi_id || alert.ticket_id}</span>
                                        <span>•</span>
                                        <span className={alert.tecnico === 'Sem Técnico' ? 'text-orange-400/80 italic' : 'text-slate-400'}>
                                            {alert.tecnico || 'Não atribuído'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div className="shrink-0 flex items-center pt-1 self-center">
                                <a
                                    href={`http://glpi-dtic.com/front/ticket.form.php?id=${alert.ticket_id}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="p-2 rounded-full hover:bg-white/5 text-slate-400 transition-colors"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                </a>
                            </div>
                        </div>
                    </div>
                );
            })}
        </motion.div>
    );

    // Initial Loading
    if (loading && safeAlerts.length === 0) {
        return (
            <div className="flex items-center justify-center h-48 text-slate-400">
                <RefreshCw className="w-6 h-6 animate-spin" />
                <span className="ml-2">Analisando qualidade...</span>
            </div>
        );
    }

    // Empty State
    if (safeAlerts.length === 0) {
        return (
            <div className="bg-[#1e293b]/50 rounded-lg p-6 border border-slate-700 border-dashed text-center">
                <div className="flex justify-center mb-2">
                    <span className="text-4xl">✨</span>
                </div>
                <p className="text-slate-300 font-medium">Nenhuma violação detectada</p>
                <p className="text-slate-500 text-sm">Qualidade 100%!</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full min-h-0 bg-[#1e293b] rounded-lg border border-slate-700 overflow-hidden shadow-lg relative">
            {/* Header */}
            <div className="shrink-0 p-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center backdrop-blur-sm relative z-10">
                <div className="flex items-center gap-2">
                    {activeFilter === 'HIGH' && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
                    {activeFilter === 'MEDIUM' && <div className="w-2 h-2 rounded-full bg-yellow-500" />}
                    {!activeFilter && <div className="w-2 h-2 rounded-full bg-slate-500" />}

                    <h3 className="font-semibold text-slate-100 tracking-wide">{getTitle()}</h3>

                    <span className="bg-slate-700 text-xs px-2 py-0.5 rounded-full text-slate-300">
                        {activeFilter === 'RULES' ? rulesSummary.length :
                            activeFilter === 'AFFECTED' ? affectedTickets.length :
                                filteredAlerts.length}
                    </span>
                </div>
                {onRefresh && (
                    <button
                        onClick={onRefresh}
                        className="p-2 hover:bg-slate-700 rounded-full text-slate-400 hover:text-white transition-colors"
                        title="Executar verificação agora"
                    >
                        <RefreshCw className="w-4 h-4" />
                    </button>
                )}
            </div>

            {/* Scrollable List Area */}
            <div className="flex-1 overflow-y-auto overflow-x-hidden p-2 space-y-2 relative custom-scrollbar max-h-[400px]">
                <AnimatePresence mode="popLayout" initial={false}>
                    {activeFilter === 'RULES' ? renderRules() :
                        activeFilter === 'AFFECTED' ? renderAffected() :
                            renderList()}
                </AnimatePresence>
            </div>
        </div>
    );
};
