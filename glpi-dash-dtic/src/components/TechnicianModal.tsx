import React, { useMemo } from 'react';
import { X, Star, Clock, CheckCircle, Briefcase, User } from 'lucide-react';
import { TechnicianDetails } from '../types';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';
import { CHART_COLORS } from '../constants';

interface TechnicianModalProps {
    technician: TechnicianDetails | null;
    isOpen: boolean;
    onClose: () => void;
}

export const TechnicianModal: React.FC<TechnicianModalProps> = ({ technician, isOpen, onClose }) => {
    if (!isOpen || !technician) return null;

    // Validação preventiva dos dados de performance
    const safePerformanceHistory = useMemo(() => {
        return (technician.performanceHistory || []).filter(item =>
            item &&
            typeof item.count === 'number' &&
            !isNaN(item.count)
        );
    }, [technician.performanceHistory]);

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop with Blur */}
            <div
                className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm transition-opacity duration-300"
                onClick={onClose}
            />

            {/* Modal Content */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl shadow-2xl w-full max-w-2xl relative overflow-hidden animate-[scaleUp_0.3s_ease-out]">

                {/* Header Background Gradient */}
                <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-r from-blue-900/50 to-slate-800/0 pointer-events-none" />

                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-slate-400 hover:text-white hover:bg-slate-700/50 p-1 rounded-full transition-colors z-10"
                >
                    <X size={24} />
                </button>

                <div className="p-6 relative z-0">
                    {/* Header: Avatar & Name */}
                    <div className="flex items-start gap-4 mb-8">
                        <div className="w-20 h-20 rounded-full border-4 border-slate-700 bg-slate-600 flex items-center justify-center text-3xl font-bold text-slate-300 shadow-lg relative">
                            {technician.name.substring(0, 2).toUpperCase()}
                            <div className={`absolute bottom-0 right-0 w-5 h-5 rounded-full border-4 border-slate-800 ${technician.status === 'online' ? 'bg-green-500' : 'bg-red-500'}`} />
                        </div>
                        <div className="mt-2">
                            <h2 className="text-2xl font-bold text-white">{technician.name}</h2>
                            <div className="flex items-center gap-2 text-slate-400 text-sm mt-1">
                                <Briefcase size={14} />
                                <span>{technician.role}</span>
                                <span className="text-slate-600">•</span>
                                <span className={`uppercase text-[10px] font-bold tracking-wider px-2 py-0.5 rounded-full ${technician.status === 'online' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                                    {technician.status}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Main Stats Grid */}
                    <div className="grid grid-cols-3 gap-4 mb-8">
                        <StatBox
                            label="Tempo Médio"
                            value={technician.stats.avgResolutionTime}
                            icon={<Clock size={18} className="text-blue-400" />}
                            bg="bg-blue-500/10"
                        />
                        <StatBox
                            label="Satisfação (CSAT)"
                            value={technician.stats.satisfactionScore.toFixed(1)}
                            subValue="/ 5.0"
                            icon={<Star size={18} className="text-yellow-400" />}
                            bg="bg-yellow-500/10"
                        />
                        <StatBox
                            label="Total Resolvido"
                            value={technician.stats.totalSolved.toString()}
                            icon={<CheckCircle size={18} className="text-green-400" />}
                            bg="bg-green-500/10"
                        />
                    </div>

                    {/* Performance & Recent Tickets Split */}
                    <div className="grid grid-cols-2 gap-6">

                        {/* Left: Sparkline Chart */}
                        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
                            <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                                Performance (7 dias)
                            </h3>
                            <div className="h-32 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={safePerformanceHistory}>
                                        <defs>
                                            <linearGradient id="gradTech" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor={CHART_COLORS.blue} stopOpacity={0.4} />
                                                <stop offset="95%" stopColor={CHART_COLORS.blue} stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '4px' }}
                                            itemStyle={{ color: '#fff' }}
                                            cursor={{ stroke: '#475569' }}
                                        />
                                        <Area type="monotone" dataKey="count" stroke={CHART_COLORS.blue} fill="url(#gradTech)" strokeWidth={2} />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Right: Recent Activity */}
                        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50 flex flex-col">
                            <h3 className="text-sm font-semibold text-slate-300 mb-3">Últimos Tickets</h3>
                            <div className="flex-1 space-y-3">
                                {technician.lastTickets.map((ticket, idx) => (
                                    <div key={idx} className="flex items-center justify-between text-xs border-b border-slate-800 pb-2 last:border-0 last:pb-0">
                                        <div className="flex items-center gap-2 overflow-hidden">
                                            <div className="min-w-[4px] h-4 bg-green-500 rounded-full" />
                                            <div className="truncate">
                                                <span className="text-slate-400 block text-[10px]">#{ticket.id}</span>
                                                <span className="text-slate-200 truncate">{ticket.title}</span>
                                            </div>
                                        </div>
                                        <div className="text-slate-500 whitespace-nowrap ml-2">{ticket.date.split(',')[1]}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const StatBox = ({ label, value, subValue, icon, bg }: any) => (
    <div className={`p-3 rounded-lg border border-slate-700/50 ${bg} flex flex-col justify-between`}>
        <div className="flex justify-between items-start mb-2">
            <span className="text-xs text-slate-400 font-medium">{label}</span>
            {icon}
        </div>
        <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-white tracking-tight">{value}</span>
            {subValue && <span className="text-xs text-slate-500">{subValue}</span>}
        </div>
    </div>
);