import React, { useState } from 'react';
import Header from '@/components/Header';
import KPIGrid from '@/components/KPIGrid';
import TicketList from '@/components/TicketList';
import { useTickets } from '@/hooks/useTickets';
import { TicketStatus } from '@/types';

const App: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<TicketStatus | 'resolved' | null>(null);

  // Fetch real data from backend API
  const { tickets, stats, loading, error } = useTickets(searchTerm, selectedStatus);

  return (
    <div className="min-h-screen bg-[#0f172a] font-sans pb-10">
      {/* Search Header */}
      <Header searchTerm={searchTerm} onSearchChange={setSearchTerm} />

      <main className="max-w-7xl mx-auto px-4 md:px-8">
        {/* KPI / Status Filters */}
        <KPIGrid
          stats={stats}
          selectedStatus={selectedStatus}
          onFilterChange={setSelectedStatus}
        />

        {/* Loading State */}
        {loading && (
          <div className="text-center text-slate-400 py-10">
            Carregando tickets...
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Results List */}
        {!loading && !error && <TicketList tickets={tickets} />}
      </main>
    </div>
  );
};

export default App;