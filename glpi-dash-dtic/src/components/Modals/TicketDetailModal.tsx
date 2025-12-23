import React, { useState, useEffect } from 'react';
import {
   X, ExternalLink, Calendar, User, Briefcase,
   AlertCircle, MessageSquare, RefreshCw
} from 'lucide-react';
import { useTicketDetail } from '../../hooks/useTicketDetail';

interface TicketDetailModalProps {
   ticketId: number | null;
   isOpen: boolean;
   onClose: () => void;
}

export const TicketDetailModal: React.FC<TicketDetailModalProps> = ({ ticketId, isOpen, onClose }) => {
   // Use Hook for data fetching
   // Only fetch if modal is open and we have an ID
   const { data, loading, error } = useTicketDetail(isOpen ? ticketId : null);

   if (!isOpen) return null;

   return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
         {/* Backdrop */}
         <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity duration-300"
            onClick={onClose}
         />

         {/* Modal Container */}
         <div className="bg-slate-900 w-full max-w-5xl h-[85vh] rounded-xl shadow-2xl border border-slate-700 flex flex-col relative overflow-hidden animate-[scaleUp_0.2s_ease-out]">

            {/* Header */}
            <header className="bg-slate-800 px-6 py-4 border-b border-slate-700 flex justify-between items-center shrink-0">
               {loading || !data ? (
                  <div className="h-6 w-1/3 bg-slate-700 rounded animate-pulse" />
               ) : (
                  <div className="flex items-center gap-3 overflow-hidden">
                     {error ? (
                        <span className="text-red-400 text-sm font-bold">Erro ao carregar</span>
                     ) : (
                        <>
                           <span className="bg-blue-600/20 text-blue-400 border border-blue-500/30 px-2 py-1 rounded text-sm font-mono font-bold whitespace-nowrap">
                              #{data?.glpi_id}
                           </span>
                           <h2 className="text-lg font-semibold text-slate-100 truncate" title={data?.title}>
                              {data?.title}
                           </h2>
                           {data && <StatusBadge status={data.status} />}
                        </>
                     )}
                  </div>
               )}

               <button onClick={onClose} className="p-2 hover:bg-slate-700 rounded-full text-slate-400 hover:text-white transition-colors">
                  <X size={20} />
               </button>
            </header>

            {/* Content Body */}
            <div className="flex-1 flex flex-col md:flex-row overflow-hidden bg-slate-900">

               {/* LEFT: Main Content (Description + Timeline) */}
               <main className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8 bg-slate-900">
                  {loading || !data ? (
                     <SkeletonLoader />
                  ) : (
                     <>
                        {/* Description Box */}
                        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-5">
                           <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                              <MessageSquare size={14} /> Descrição do Chamado
                           </h3>
                           <div className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
                              {data.description}
                           </div>
                        </div>

                        {/* Timeline */}
                        <div className="space-y-6">
                           <div className="relative">
                              <div className="absolute left-1/2 -ml-0.5 w-0.5 h-full bg-slate-800" aria-hidden="true"></div>
                              <div className="relative flex justify-center">
                                 <span className="bg-slate-800 text-slate-400 text-[10px] font-bold px-2 py-1 rounded-full border border-slate-700">
                                    INÍCIO DO ATENDIMENTO
                                 </span>
                              </div>
                           </div>

                           {data.timeline.map((item) => {
                              const isLog = item.type === 'change';
                              const isTechnician = item.author === data.technician; // Simple inference

                              if (isLog) {
                                 return (
                                    <div key={item.id} className="flex justify-center my-4">
                                       <div className="bg-slate-800/80 text-slate-400 text-xs px-3 py-1 rounded-full border border-slate-700/50 text-center max-w-[80%]">
                                          {item.author !== 'Sistema' && <span className="font-semibold text-slate-300">{item.author}: </span>}
                                          {item.content}
                                          <span className="ml-2 opacity-50 text-[10px]">{item.date.split(' ')[1]}</span>
                                       </div>
                                    </div>
                                 );
                              }

                              return (
                                 <div key={item.id} className={`flex w-full ${isTechnician ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`flex max-w-[85%] md:max-w-[70%] ${isTechnician ? 'flex-row-reverse' : 'flex-row'} gap-3`}>

                                       {/* Avatar */}
                                       <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${isTechnician ? 'bg-blue-600 text-white' : 'bg-slate-600 text-slate-200'}`}>
                                          {item.author.substring(0, 2).toUpperCase()}
                                       </div>

                                       {/* Bubble */}
                                       <div className={`flex flex-col ${isTechnician ? 'items-end' : 'items-start'}`}>
                                          <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${isTechnician
                                             ? 'bg-blue-600 text-white rounded-tr-none'
                                             : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none'
                                             }`}>
                                             {item.content}
                                          </div>
                                          <div className="flex items-center gap-2 mt-1 px-1">
                                             <span className="text-xs font-semibold text-slate-400">{item.author}</span>
                                             <span className="text-[10px] text-slate-500">{item.date}</span>
                                          </div>
                                       </div>

                                    </div>
                                 </div>
                              );
                           })}
                        </div>
                     </>
                  )}
               </main>

               {/* RIGHT: Sidebar (Metadata) */}
               <aside className="w-full md:w-80 bg-slate-800/30 border-t md:border-t-0 md:border-l border-slate-700 p-6 overflow-y-auto custom-scrollbar">
                  {loading || !data ? (
                     <div className="space-y-4">
                        <div className="h-4 bg-slate-700 rounded w-1/2 animate-pulse" />
                        <div className="h-8 bg-slate-700 rounded w-full animate-pulse" />
                        <div className="h-4 bg-slate-700 rounded w-1/3 animate-pulse mt-4" />
                        <div className="h-8 bg-slate-700 rounded w-full animate-pulse" />
                     </div>
                  ) : (
                     <div className="space-y-6">
                        <SidebarItem
                           icon={<Calendar size={16} className="text-slate-400" />}
                           label="Data de Abertura"
                           value={data.creation_date}
                        />

                        <SidebarItem
                           icon={<User size={16} className="text-slate-400" />}
                           label="Solicitante"
                           value={data.requester}
                        />

                        <SidebarItem
                           icon={<Briefcase size={16} className="text-slate-400" />}
                           label="Técnico Responsável"
                           value={data.technician || "Não atribuído"}
                        />

                        <div>
                           <h4 className="text-xs text-slate-500 uppercase font-bold mb-2">Prioridade</h4>
                           <span className={`inline-block px-3 py-1 rounded text-xs font-bold border ${data.priority === 'Alta' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                              data.priority === 'Média' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                              }`}>
                              {data.priority}
                           </span>
                        </div>

                        <hr className="border-slate-700/50" />
                        <a
                           href={data.url || '#'}
                           target="_blank"
                           rel="noopener noreferrer"
                           className={`flex items-center justify-center gap-2 w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600 rounded transition-colors text-sm font-medium ${!data.url ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                           <ExternalLink size={14} />
                           Ver no GLPI
                        </a>
                     </div>
                  )}
               </aside>

            </div>
         </div>
      </div>
   );
};

/* --- Sub Components --- */

const StatusBadge = ({ status }: { status: string }) => {
   let colors = "bg-slate-700 text-slate-300 border-slate-600";
   if (status.toLowerCase().includes('atendimento')) colors = "bg-blue-500/10 text-blue-400 border-blue-500/20";
   if (status.toLowerCase().includes('solucionado')) colors = "bg-green-500/10 text-green-400 border-green-500/20";
   if (status.toLowerCase().includes('pendente')) colors = "bg-yellow-500/10 text-yellow-400 border-yellow-500/20";

   return (
      <span className={`text-xs px-2 py-0.5 rounded-full border ${colors} font-medium`}>
         {status}
      </span>
   );
};

const SidebarItem = ({ icon, label, value }: any) => (
   <div>
      <h4 className="text-xs text-slate-500 uppercase font-bold mb-1 flex items-center gap-2">
         {icon} {label}
      </h4>
      <div className="text-sm text-slate-200 font-medium">
         {value}
      </div>
   </div>
);

const SkeletonLoader = () => (
   <div className="space-y-6 animate-pulse">
      <div className="h-32 bg-slate-800 rounded-lg w-full" />
      <div className="space-y-4">
         <div className="flex gap-4">
            <div className="w-10 h-10 bg-slate-800 rounded-full" />
            <div className="h-16 bg-slate-800 rounded-lg w-2/3" />
         </div>
         <div className="flex gap-4 flex-row-reverse">
            <div className="w-10 h-10 bg-slate-800 rounded-full" />
            <div className="h-20 bg-slate-800 rounded-lg w-3/4" />
         </div>
      </div>
   </div>
);