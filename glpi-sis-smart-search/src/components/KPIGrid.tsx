import React from 'react';
import { Mail, Clock, Calendar, AlertCircle, CheckCircle, LucideIcon } from 'lucide-react';
import { KPIStats, TicketStatus } from '../types';

interface KPICardProps {
  label: string;
  count: number;
  icon: LucideIcon;
  colorClass: string;
  onClick: () => void;
  isActive: boolean;
}

const KPICard: React.FC<KPICardProps> = ({ label, count, icon: Icon, colorClass, onClick, isActive }) => {
  return (
    <button
      onClick={onClick}
      className={`${colorClass} relative overflow-hidden rounded-xl p-5 text-left text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-white ${
        isActive ? 'ring-4 ring-white/30 scale-105' : 'opacity-90 hover:opacity-100'
      }`}
    >
      <div className="flex flex-col h-full justify-between relative z-10">
        <Icon size={32} className="mb-4 opacity-80" />
        <div>
          <span className="text-4xl font-bold block mb-1">{count}</span>
          <span className="text-sm font-medium uppercase tracking-wider opacity-90">{label}</span>
        </div>
      </div>
      {/* Decorative circle */}
      <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-white/10 blur-xl pointer-events-none"></div>
    </button>
  );
};

interface KPIGridProps {
  stats: KPIStats;
  selectedStatus: TicketStatus | 'resolved' | null;
  onFilterChange: (status: TicketStatus | 'resolved' | null) => void;
}

const KPIGrid: React.FC<KPIGridProps> = ({ stats, selectedStatus, onFilterChange }) => {
  const handleFilter = (status: TicketStatus | 'resolved') => {
    if (selectedStatus === status) {
      onFilterChange(null); // Deselect
    } else {
      onFilterChange(status);
    }
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8 -mt-20 relative z-10">
      <KPICard
        label="Novos"
        count={stats.new}
        icon={Mail}
        colorClass="bg-green-600"
        isActive={selectedStatus === TicketStatus.NEW}
        onClick={() => handleFilter(TicketStatus.NEW)}
      />
      <KPICard
        label="Em Andamento"
        count={stats.processing}
        icon={Clock}
        colorClass="bg-blue-600"
        isActive={selectedStatus === TicketStatus.PROCESSING}
        onClick={() => handleFilter(TicketStatus.PROCESSING)}
      />
      <KPICard
        label="Planejado"
        count={stats.planned}
        icon={Calendar}
        colorClass="bg-cyan-600"
        isActive={selectedStatus === TicketStatus.PLANNED}
        onClick={() => handleFilter(TicketStatus.PLANNED)}
      />
      <KPICard
        label="Pendentes"
        count={stats.pending}
        icon={AlertCircle}
        colorClass="bg-orange-600"
        isActive={selectedStatus === TicketStatus.PENDING}
        onClick={() => handleFilter(TicketStatus.PENDING)}
      />
      <KPICard
        label="Resolvidos"
        count={stats.resolved}
        icon={CheckCircle}
        colorClass="bg-slate-700"
        isActive={selectedStatus === 'resolved'}
        onClick={() => handleFilter('resolved')}
      />
    </div>
  );
};

export default KPIGrid;