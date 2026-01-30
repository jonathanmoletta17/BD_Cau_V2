import React from 'react';
import { Ticket } from '../types';
import TicketCard from './TicketCard';
import { BarChart2, Clock } from 'lucide-react';

interface TicketListProps {
  tickets: Ticket[];
}

const TicketList: React.FC<TicketListProps> = ({ tickets }) => {
  return (
    <div className="bg-[#1e293b] rounded-xl border border-slate-700/50 p-6 shadow-xl">
      <div className="flex flex-col md:flex-row items-center justify-between mb-8 border-b border-slate-700 pb-6">
        <h2 className="text-2xl font-semibold text-white mb-4 md:mb-0">
          Resultados <span className="text-blue-400">({tickets.length})</span>
        </h2>

        <div className="flex bg-slate-900/80 rounded-lg p-1 border border-slate-700">
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium shadow-sm transition-all hover:bg-blue-500">
            <BarChart2 size={16} />
            Relevância
          </button>
          <button className="flex items-center gap-2 px-4 py-2 text-slate-400 hover:text-white rounded-md text-sm font-medium transition-colors">
            <Clock size={16} />
            Recentes
          </button>
        </div>
      </div>

      {tickets.length > 0 ? (
        <div className="space-y-4">
          {tickets.map((ticket) => (
            <TicketCard key={ticket.id} ticket={ticket} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800 mb-4">
             <BarChart2 className="h-8 w-8 text-slate-500" />
          </div>
          <h3 className="text-lg font-medium text-white">Nenhum ticket encontrado</h3>
          <p className="text-slate-400 mt-2">Tente ajustar seus filtros ou termo de busca.</p>
        </div>
      )}
    </div>
  );
};

export default TicketList;