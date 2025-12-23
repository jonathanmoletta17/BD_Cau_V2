import React from 'react';
import { Ticket } from '../types';
import { Building2, Tag, User, Briefcase, Users } from 'lucide-react';

interface TicketCardProps {
  ticket: Ticket;
}

const TicketCard: React.FC<TicketCardProps> = ({ ticket }) => {
  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(dateString));
  };

  return (
    <div className="bg-[#151e32] border border-slate-800 rounded-lg p-6 mb-4 hover:border-blue-500/30 transition-colors shadow-sm">
      {/* Header Row */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-6">
        <div className="flex items-start gap-4 flex-1">
          <span className="bg-blue-900/50 text-blue-300 px-3 py-1 rounded text-sm font-bold border border-blue-800/50 whitespace-nowrap">
            #{ticket.id}
          </span>
          <h3 className="text-lg font-semibold text-slate-100 leading-snug">
            {ticket.name}
          </h3>
        </div>
        <div className="text-right shrink-0">
            <div className="text-[10px] text-blue-400 uppercase font-bold mb-1">Data Abertura</div>
            <div className="text-slate-300 font-medium text-sm">
              {formatDate(ticket.date_creation)}
            </div>
        </div>
      </div>

      {/* Metadata Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-6 text-sm">
        <div className="bg-slate-900/50 p-3 rounded border border-slate-800/50">
          <div className="flex items-center gap-2 text-slate-500 mb-1 text-xs uppercase font-bold">
            <Building2 size={12} /> Entidade
          </div>
          <div className="text-slate-300 truncate" title={ticket.entity.name}>
            {ticket.entity.name}
          </div>
        </div>

        <div className="bg-slate-900/50 p-3 rounded border border-slate-800/50">
          <div className="flex items-center gap-2 text-slate-500 mb-1 text-xs uppercase font-bold">
            <Tag size={12} /> Categoria
          </div>
          <div className="text-slate-300 truncate">
            {ticket.category ? ticket.category.name : 'N/A'}
          </div>
        </div>

        <div className="bg-slate-900/50 p-3 rounded border border-slate-800/50">
          <div className="flex items-center gap-2 text-slate-500 mb-1 text-xs uppercase font-bold">
            <User size={12} /> Requerente
          </div>
          <div className="text-slate-300 truncate">
            {ticket.requester ? ticket.requester.username : 'N/A'}
          </div>
        </div>

        <div className="bg-slate-900/50 p-3 rounded border border-slate-800/50">
          <div className="flex items-center gap-2 text-slate-500 mb-1 text-xs uppercase font-bold">
            <Briefcase size={12} /> Técnico
          </div>
          <div className="text-slate-300 truncate">
            {ticket.technician ? ticket.technician.username : 'N/A'}
          </div>
        </div>

        <div className="bg-slate-900/50 p-3 rounded border border-slate-800/50">
          <div className="flex items-center gap-2 text-slate-500 mb-1 text-xs uppercase font-bold">
            <Users size={12} /> Grupo
          </div>
          <div className="text-slate-300 truncate">
            {ticket.group ? ticket.group.name : 'N/A'}
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="relative mb-4">
         <p className="text-slate-400 text-sm leading-relaxed line-clamp-3">
           {ticket.content}
         </p>
      </div>

      {/* Footer / Action */}
      <div className="flex justify-start">
        <a href="#" className="text-blue-400 text-sm hover:text-blue-300 font-medium hover:underline flex items-center gap-1">
          ver mais
        </a>
      </div>
    </div>
  );
};

export default TicketCard;