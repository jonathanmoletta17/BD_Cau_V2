import React from 'react';
import { Charger, Ticket } from '../types';
import { User, Trophy, Clock, Medal, Hash } from 'lucide-react';
import { format, differenceInHours, differenceInMinutes, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// --- Helper Functions ---
const formatTimeElapsed = (dateString: string | null | undefined) => {
  if (!dateString) return "0h 0m";
  const date = parseISO(dateString);
  const now = new Date();
  const hours = differenceInHours(now, date);
  const minutes = differenceInMinutes(now, date) % 60;
  return `${hours}h ${minutes}m`;
};

// --- Column 1: Available List ---
interface AvailableListProps {
  chargers: Charger[];
}

export const AvailableList: React.FC<AvailableListProps> = ({ chargers }) => {
  return (
    <div className="flex flex-col h-full bg-slate-900/50 rounded-xl border border-slate-800/50 backdrop-blur-sm">
      <div className="p-4 border-b border-slate-800 flex justify-between items-center">
        <h3 className="text-green-500 font-semibold flex items-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          Disponíveis
        </h3>
        <span className="bg-green-500/20 text-green-400 text-xs px-2 py-0.5 rounded">
          {chargers.length}
        </span>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-3 custom-scrollbar">
        {chargers.map((charger) => (
          <div key={charger.id} className="bg-slate-800/80 p-4 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-3">
                <div className="bg-slate-700 p-2 rounded-full">
                  <User size={16} className="text-slate-400" />
                </div>
                <span className="font-medium text-slate-200">{charger.name}</span>
              </div>
              {charger.lastTicket?.solvedate && (
                <div className="flex items-center gap-1 text-green-500 text-xs font-mono bg-green-950/30 px-2 py-1 rounded">
                  <Clock size={12} />
                  {formatTimeElapsed(charger.lastTicket.solvedate)}
                </div>
              )}
            </div>

            <div className="text-xs text-slate-500 pl-[44px]">
              {charger.lastTicket ? (
                <>
                  <p className="line-clamp-1 mb-0.5">
                    <span className="text-slate-600">Último:</span> #{charger.lastTicket.id} - {charger.lastTicket.name}
                  </p>
                </>
              ) : (
                <span className="text-slate-600 italic">Sem histórico recente</span>
              )}
            </div>
          </div>
        ))}
        {chargers.length === 0 && (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm italic">
            Nenhum carregador disponível.
          </div>
        )}
      </div>
    </div>
  );
};

// --- Column 2: Occupied List ---
interface OccupiedListProps {
  chargers: Charger[];
}

export const OccupiedList: React.FC<OccupiedListProps> = ({ chargers }) => {
  return (
    <div className="flex flex-col h-full bg-slate-900/50 rounded-xl border border-slate-800/50 backdrop-blur-sm">
      <div className="p-4 border-b border-slate-800 flex justify-between items-center">
        <h3 className="text-orange-500 font-semibold flex items-center gap-2">
          <span className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></span>
          Ocupados
        </h3>
        <span className="bg-orange-500/20 text-orange-400 text-xs px-2 py-0.5 rounded">
          {chargers.length}
        </span>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-3 custom-scrollbar">
        {chargers.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-600">
            <Clock size={48} className="mb-2 opacity-20" />
            <p className="text-sm">Nenhum carregador ocupado</p>
          </div>
        ) : (
          chargers.map((charger) => (
            <div key={charger.id} className="bg-slate-800/80 p-4 rounded-lg border border-orange-500/30 shadow-[0_0_15px_-5px_rgba(249,115,22,0.1)] relative overflow-hidden">
              {/* Accent Border Left */}
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-orange-500"></div>

              <div className="flex justify-between items-start mb-2 pl-3">
                <span className="font-semibold text-orange-100">{charger.name}</span>
                {charger.currentTicket?.date && (
                  <span className="text-orange-400 text-xs font-mono bg-orange-950/30 px-2 py-1 rounded flex items-center gap-1">
                    <Clock size={12} />
                    {formatTimeElapsed(charger.currentTicket.date)}
                  </span>
                )}
              </div>

              <div className="pl-3 mt-3">
                <div className="bg-slate-900/50 rounded p-2 border border-slate-700/50">
                  <p className="text-xs text-orange-200/70 uppercase tracking-wider font-bold mb-1">Em atendimento</p>
                  <p className="text-sm text-slate-300 line-clamp-2">
                    #{charger.currentTicket?.id} - {charger.currentTicket?.name}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// --- Column 3: Ranking List ---
interface RankingListProps {
  chargers: Charger[];
  totalAttributed: number;
}

export const RankingList: React.FC<RankingListProps> = ({ chargers, totalAttributed }) => {
  // Assume chargers are already sorted by parent
  const leader = chargers.length > 0 ? chargers[0] : null;
  const runnersUp = chargers.slice(1);

  return (
    <div className="flex flex-col h-full bg-slate-900/50 rounded-xl border border-slate-800/50 backdrop-blur-sm">
      <div className="p-4 border-b border-slate-800">
        <h3 className="text-yellow-500 font-semibold flex items-center gap-2 mb-1">
          <Trophy size={18} />
          Ranking de Carregadores
        </h3>
        <p className="text-xs text-slate-500">(período selecionado)</p>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto p-3 custom-scrollbar">
        {leader && (
          <div className="mb-4">
            <div className="bg-gradient-to-r from-yellow-600 to-yellow-500 p-5 rounded-xl shadow-lg relative overflow-hidden text-white">
              <div className="flex justify-between items-start relative z-10">
                <div className="flex items-center gap-3">
                  <div className="bg-white/20 p-2 rounded-full">
                    <Trophy className="w-8 h-8 text-white" fill="currentColor" />
                  </div>
                  <div>
                    <h4 className="text-lg font-bold leading-tight">{leader.name}</h4>
                    <span className="text-yellow-100 text-xs font-medium uppercase tracking-wide">Líder do ranking</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="block text-3xl font-bold">{leader.totalTicketsInPeriod || 0}</span>
                  <span className="text-xs text-yellow-100 opacity-80">tickets</span>
                </div>
              </div>
              <div className="absolute -right-4 -bottom-8 text-yellow-400 opacity-20 transform rotate-12">
                <Trophy size={120} />
              </div>
            </div>
          </div>
        )}

        <div className="space-y-2">
          {runnersUp.map((charger, index) => (
            <div key={charger.id} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg border border-slate-700">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-blue-400 font-bold text-sm border border-slate-600 shadow-inner">
                  {index + 2}
                </div>
                <span className="text-slate-300 font-medium text-sm">{charger.name}</span>
              </div>
              <div className="text-right">
                <span className="text-slate-200 font-bold block">{charger.totalTicketsInPeriod || 0}</span>
                <span className="text-[10px] text-slate-500 uppercase">tickets</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-900/30 rounded-b-xl">
        <div className="flex justify-between items-center">
          <span className="text-slate-400 text-sm">Total Atribuído</span>
          <span className="text-2xl font-bold text-slate-200">{totalAttributed}</span>
        </div>
      </div>
    </div>
  );
};