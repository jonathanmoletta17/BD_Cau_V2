import React from 'react';
import { Search } from 'lucide-react';

interface HeaderProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
}

const Header: React.FC<HeaderProps> = ({ searchTerm, onSearchChange }) => {
  return (
    <header className="bg-blue-600 text-white pb-32 pt-8 px-4 md:px-8 shadow-md relative z-0">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-4 mb-10">
          <div className="p-3 bg-blue-500 rounded-xl shadow-inner border border-blue-400 hidden sm:block">
             <Search size={32} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">GLPI SIS SMART SEARCH</h1>
            <p className="text-blue-100 text-sm md:text-base opacity-90">Busca de Tickets - Manutenção e Conservação</p>
          </div>
        </div>

        <div className="relative w-full max-w-5xl mx-auto">
          <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-slate-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-14 pr-6 py-5 bg-[#1e293b] border-2 border-blue-400/30 rounded-2xl text-white placeholder-slate-400 focus:ring-4 focus:ring-blue-500/20 focus:border-white focus:outline-none transition-all shadow-2xl text-lg"
            placeholder="Pesquise por tickets, descrições, categorias, técnicos..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
      </div>
    </header>
  );
};

export default Header;