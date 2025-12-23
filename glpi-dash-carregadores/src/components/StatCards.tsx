import React from 'react';
import { DashboardStats } from '../types';
import { CheckCircle, Clock, XCircle, Users } from 'lucide-react';

interface StatCardsProps {
  stats: DashboardStats;
}

const StatCards: React.FC<StatCardsProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Available */}
      <div className="bg-green-600 rounded-xl p-4 shadow-lg relative overflow-hidden group hover:scale-[1.02] transition-transform duration-200">
        <div className="flex justify-between items-start z-10 relative">
          <div>
            <div className="bg-white/20 p-2 rounded-lg w-min mb-3">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-1">{stats.available}</h2>
            <p className="text-green-100 text-sm font-medium">Disponíveis</p>
          </div>
          <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-semibold text-white">Agora</span>
        </div>
        <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-xl group-hover:bg-white/20 transition-all"></div>
      </div>

      {/* Occupied */}
      <div className="bg-orange-600 rounded-xl p-4 shadow-lg relative overflow-hidden group hover:scale-[1.02] transition-transform duration-200">
        <div className="flex justify-between items-start z-10 relative">
          <div>
            <div className="bg-white/20 p-2 rounded-lg w-min mb-3">
              <Clock className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-1">{stats.occupied}</h2>
            <p className="text-orange-100 text-sm font-medium">Ocupados</p>
          </div>
          <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-semibold text-white">Agora</span>
        </div>
        <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-xl group-hover:bg-white/20 transition-all"></div>
      </div>

      {/* Offline */}
      <div className="bg-slate-700 rounded-xl p-4 shadow-lg relative overflow-hidden group hover:scale-[1.02] transition-transform duration-200">
        <div className="flex justify-between items-start z-10 relative">
          <div>
            <div className="bg-white/10 p-2 rounded-lg w-min mb-3">
              <XCircle className="w-6 h-6 text-gray-300" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-1">{stats.offline}</h2>
            <p className="text-gray-400 text-sm font-medium">Offline</p>
          </div>
          <span className="bg-white/10 px-3 py-1 rounded-full text-xs font-semibold text-gray-300">Agora</span>
        </div>
      </div>

      {/* Total */}
      <div className="bg-blue-600 rounded-xl p-4 shadow-lg relative overflow-hidden group hover:scale-[1.02] transition-transform duration-200">
        <div className="flex justify-between items-start z-10 relative">
          <div>
            <div className="bg-white/20 p-2 rounded-lg w-min mb-3">
              <Users className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-1">{stats.total}</h2>
            <p className="text-blue-100 text-sm font-medium">Total de Carregadores</p>
          </div>
          <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-semibold text-white">Agora</span>
        </div>
        <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-xl group-hover:bg-white/20 transition-all"></div>
      </div>
    </div>
  );
};

export default StatCards;