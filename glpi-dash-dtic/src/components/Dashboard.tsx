import React, { useState } from 'react';
import {
  Activity, Clock, AlertCircle, CheckCircle,
  Calendar, RotateCw, Filter, Trophy, Medal, User,
  MoreHorizontal
} from 'lucide-react';
import { useDashboardData } from '../hooks/useDashboardData';
import { MetricsCarousel } from './Charts/MetricsCarousel';
import { TechnicianModal } from './TechnicianModal';
import { TicketDetailModal } from './Modals/TicketDetailModal';
import { DateRangePicker } from './DateRangePicker';
import { TicketNovo, TecnicoRanking, TechnicianDetails } from '../types';
import { getMockTechnicianDetails } from '../constants';

const Dashboard: React.FC = () => {
  // Helper to get default date range (last 30 days)
  const getDefaultDateRange = () => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    };
  };

  const [dateRange, setDateRange] = useState(getDefaultDateRange());
  const { data, loading, refresh } = useDashboardData(dateRange.start, dateRange.end);

  // State for Modals
  const [selectedTech, setSelectedTech] = useState<TechnicianDetails | null>(null);
  const [isTechModalOpen, setIsTechModalOpen] = useState(false);

  // V4: Store only the ID, let the modal fetch the data
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [isTicketModalOpen, setIsTicketModalOpen] = useState(false);

  // Handler for technician click
  const handleTechClick = (techName: string) => {
    const details = getMockTechnicianDetails(techName);
    setSelectedTech(details);
    setIsTechModalOpen(true);
  };

  // Handler for ticket click (V4)
  const handleTicketClick = (ticketId: number) => {
    setSelectedTicketId(ticketId);
    setIsTicketModalOpen(true);
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-screen bg-dtic-bg text-slate-400">
        <RotateCw className="w-8 h-8 animate-spin mr-2" />
        <span>Carregando Dashboard DTIC...</span>
      </div>
    );
  }

  if (!data) return null;

  const currentDate = new Date();
  const dateString = currentDate.toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long' }).toUpperCase();
  const timeString = currentDate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  return (
    <>
      <div className="flex flex-col h-screen p-4 gap-4 overflow-hidden relative">

        {/* --- HEADER --- */}
        <header className="flex justify-between items-center bg-blue-600/10 border-b border-blue-500/20 p-4 rounded-lg shrink-0">
          <div className="flex items-center gap-3">
            <Activity className="w-8 h-8 text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold text-white tracking-wide">DTIC - Dashboard de Métricas</h1>
              <p className="text-xs text-blue-200">Departamento de Tecnologia da Informação - Monitoramento em Tempo Real</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <DateRangePicker
              startDate={dateRange.start}
              endDate={dateRange.end}
              onChange={(start, end) => setDateRange({ start, end })}
            />

            <div className="text-right">
              <div className="text-2xl font-bold font-mono tracking-widest">{timeString}</div>
              <div className="text-[10px] text-slate-400 tracking-wider">{dateString}</div>
            </div>

            <button onClick={refresh} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
              <RotateCw className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* --- TOP METRICS CARDS --- */}
        <div className="grid grid-cols-4 gap-4 h-32 shrink-0">
          <MetricCard
            icon={<Activity className="w-8 h-8" />}
            value={data.metrics.novos}
            label="Novos"
            color="blue"
          />
          <MetricCard
            icon={<Clock className="w-8 h-8" />}
            value={data.metrics.em_progresso}
            label="Em Progresso"
            color="orange"
          />
          <MetricCard
            icon={<AlertCircle className="w-8 h-8" />}
            value={data.metrics.pendentes}
            label="Pendentes"
            color="yellow"
          />
          <MetricCard
            icon={<CheckCircle className="w-8 h-8" />}
            value={data.metrics.resolvidos}
            label="Resolvidos"
            color="green"
          />
        </div>

        {/* --- MAIN CONTENT GRID --- */}
        <div className="grid grid-cols-12 gap-4 flex-1 min-h-0">

          {/* LEFT COLUMN: CAROUSEL + RANKING */}
          <div className="col-span-9 flex flex-col gap-4 min-h-0 h-full">

            {/* CAROUSEL SECTION */}
            <div className="flex-1 min-h-0">
              <MetricsCarousel data={data.carouselData} />
            </div>

            {/* BOTTOM RANKING SECTION */}
            <div className="h-48 bg-dtic-card rounded-lg border border-dtic-border p-4 flex flex-col shrink-0">
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2 text-slate-200 font-semibold">
                  <Trophy className="w-5 h-5 text-blue-400" />
                  <h2>Ranking de Técnicos</h2>
                </div>
                <span className="text-xs text-slate-500 italic">** Clique no card para detalhes</span>
              </div>

              <div className="flex gap-4 h-full overflow-x-auto items-center pb-2 px-1">
                {data.ranking.map((tech, idx) => (
                  <TechnicianCard
                    key={idx}
                    tech={tech}
                    rank={idx + 1}
                    onClick={() => handleTechClick(tech.tecnico)}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: NEW TICKETS LIST */}
          <div className="col-span-3 bg-dtic-card rounded-lg border border-dtic-border flex flex-col min-h-0">
            <div className="p-4 border-b border-dtic-border flex justify-between items-center bg-slate-800/50 rounded-t-lg">
              <div className="flex items-center gap-2 font-semibold text-slate-200">
                <MoreHorizontal className="w-5 h-5" />
                <span>Tickets Novos</span>
              </div>
              <div className="flex gap-2">
                <button className="text-xs flex items-center gap-1 text-slate-400 hover:text-white">
                  <Filter className="w-3 h-3" /> Todas
                </button>
                <span className="bg-blue-600 text-xs px-2 py-0.5 rounded-full text-white">{data.newTickets.length} tickets</span>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar">
              {data.newTickets.map((ticket) => (
                <TicketCard
                  key={ticket.id}
                  ticket={ticket}
                  onClick={() => handleTicketClick(ticket.id)}
                />
              ))}

              {/* Recent Activity List */}
              <div className="mt-6 pt-4 border-t border-dtic-border px-2">
                <div className="flex items-center gap-2 text-green-400 text-sm font-semibold mb-3">
                  <Activity className="w-4 h-4" /> Atividade Recente
                </div>
                <div className="space-y-2 opacity-60 text-xs">
                  {[1, 2, 3, 4, 5].map(i => (
                    <div key={i} className="flex justify-between text-slate-400">
                      <span>Atualizou Chamado #{11820 + i}</span>
                      <span>há {i * 10}min</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* --- MODALS --- */}
      <TechnicianModal
        isOpen={isTechModalOpen}
        onClose={() => setIsTechModalOpen(false)}
        technician={selectedTech}
      />

      <TicketDetailModal
        isOpen={isTicketModalOpen}
        onClose={() => setIsTicketModalOpen(false)}
        ticketId={selectedTicketId}
      />

      {/* Global CSS for animations */}
      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes scaleUp { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
      `}</style>
    </>
  );
};

/* --- SUB COMPONENTS --- */

interface MetricCardProps {
  icon: React.ReactNode;
  value: number;
  label: string;
  color: 'blue' | 'orange' | 'yellow' | 'green';
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, value, label, color }) => {
  const colorMap = {
    blue: 'bg-blue-600 border-blue-500 text-white',
    orange: 'bg-orange-500 border-orange-400 text-white',
    yellow: 'bg-yellow-500 border-yellow-400 text-white',
    green: 'bg-green-500 border-green-400 text-white'
  };

  return (
    <div className={`relative rounded-lg p-4 flex items-center justify-between shadow-lg overflow-hidden border-b-4 ${colorMap[color].replace('bg-', 'border-').split(' ')[1]} bg-dtic-card`}>
      <div className={`absolute left-0 top-0 bottom-0 w-2 ${colorMap[color].split(' ')[0]}`} />
      <div className="ml-4 z-10">
        <div className="flex items-center gap-2 mb-1">
          <div className="opacity-80">{icon}</div>
          <span className="text-4xl font-bold text-white">{value}</span>
        </div>
        <div className="text-sm font-medium text-slate-300 ml-10">{label}</div>
      </div>
      <div className={`absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-white/5 to-transparent pointer-events-none`} />
    </div>
  );
};

interface TechnicianCardProps {
  tech: TecnicoRanking;
  rank: number;
  onClick: () => void;
}

const TechnicianCard: React.FC<TechnicianCardProps> = ({ tech, rank, onClick }) => {
  const isTop3 = rank <= 3;
  const cursorClass = "cursor-pointer transform hover:scale-105 transition-transform duration-200 active:scale-95";

  if (isTop3) {
    const medalColor = rank === 1 ? 'text-yellow-400 border-yellow-500/50' : rank === 2 ? 'text-slate-300 border-slate-400/50' : 'text-orange-400 border-orange-500/50';
    const bgGradient = rank === 1 ? 'from-yellow-500/10' : rank === 2 ? 'from-slate-500/10' : 'from-orange-500/10';

    return (
      <div
        onClick={onClick}
        className={`min-w-[140px] h-full rounded-lg bg-gradient-to-b ${bgGradient} to-transparent border ${medalColor.split(' ')[1]} p-3 flex flex-col items-center justify-center relative ${cursorClass}`}
      >
        <div className={`absolute top-2 right-2 ${medalColor.split(' ')[0]}`}>
          <Medal className="w-4 h-4" />
        </div>
        <div className={`w-12 h-12 rounded-full border-2 ${medalColor.split(' ')[1]} flex items-center justify-center text-lg font-bold bg-slate-800 mb-2`}>
          {tech.tecnico.substring(0, 2).toUpperCase()}
        </div>
        <div className="text-[10px] text-center font-bold text-slate-300 mb-1 leading-tight line-clamp-2 h-8 flex items-center justify-center">
          #{rank} {tech.tecnico}
        </div>
        <div className={`text-xl font-bold ${medalColor.split(' ')[0]}`}>{tech.tickets}</div>
      </div>
    );
  }

  // Normal List Item style
  return (
    <div
      onClick={onClick}
      className={`min-w-[200px] h-[80%] bg-slate-800/50 rounded border border-slate-700 p-2 flex items-center gap-3 ${cursorClass} hover:bg-slate-700`}
    >
      <div className="w-6 h-6 bg-slate-700 rounded flex items-center justify-center text-xs text-slate-400 font-mono">
        {rank}
      </div>
      <div className="flex-1 overflow-hidden">
        <div className="text-xs text-slate-300 truncate font-medium">{tech.tecnico}</div>
        <div className="w-full bg-slate-700 h-1.5 rounded-full mt-1">
          <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: `${Math.min((tech.tickets / 100) * 100, 100)}%` }} />
        </div>
      </div>
      <div className="text-sm font-bold text-blue-400">{tech.tickets}</div>
    </div>
  );
};

interface TicketCardProps {
  ticket: TicketNovo;
  onClick: () => void;
}

const TicketCard: React.FC<TicketCardProps> = ({ ticket, onClick }) => {
  const priorityColor =
    ticket.prioridade === 'Alta' ? 'text-red-400 bg-red-900/20 border-red-900/50' :
      ticket.prioridade === 'Média' ? 'text-yellow-400 bg-yellow-900/20 border-yellow-900/50' :
        'text-blue-400 bg-blue-900/20 border-blue-900/50';

  return (
    <div
      onClick={onClick}
      className="bg-slate-800/40 p-3 rounded border border-slate-700/50 hover:bg-slate-800 transition-colors cursor-pointer group hover:border-slate-600"
    >
      <div className="flex justify-between items-start mb-1">
        <span className="bg-blue-600 text-[10px] font-bold px-1.5 py-0.5 rounded text-white group-hover:bg-blue-500 transition-colors">#{ticket.id}</span>
        <span className={`text-[10px] px-2 py-0.5 rounded-full border ${priorityColor} font-medium`}>
          {ticket.prioridade}
        </span>
      </div>
      <h4 className="text-sm text-slate-200 font-medium leading-tight mb-2 line-clamp-2 group-hover:text-blue-300 transition-colors">
        {ticket.titulo}
      </h4>
      <div className="flex items-center gap-2 text-[10px] text-slate-500">
        <User className="w-3 h-3" />
        <span className="truncate max-w-[100px]">{ticket.solicitante}</span>
        <span className="ml-auto flex items-center gap-1">
          <Clock className="w-3 h-3" /> 4d
        </span>
      </div>
    </div>
  );
};

export default Dashboard;