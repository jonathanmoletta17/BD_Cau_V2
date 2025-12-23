
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import KPIGrid from './components/KPIGrid';
import TicketList from './components/TicketList';
import { TicketStatus, KPIStats, Ticket } from './types';
import { searchTickets, getStats } from './services/service';

const App: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<TicketStatus | 'resolved' | null>(null);

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<KPIStats>({ new: 0, processing: 0, planned: 0, pending: 0, resolved: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch Stats (Re-fetch when searchTerm changes)
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats(searchTerm);
        setStats(data);
      } catch (e) {
        console.error("Failed to fetch stats", e);
      }
    };
    fetchStats();
  }, [searchTerm]);

  // Fetch Tickets (Re-fetch when searchTerm or status changes)
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await searchTickets(searchTerm, selectedStatus);
        setTickets(data);
      } catch (err: any) {
        setError(err.message);
        setTickets([]);
      } finally {
        setLoading(false);
      }
    };

    // Debounce search slightly
    const timeoutId = setTimeout(() => {
      fetchData();
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedStatus]);

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

        {/* Results List */}
        {loading && <div className="text-white text-center mt-10">Carregando...</div>}
        {error && <div className="text-red-500 text-center mt-10">Erro: {error}</div>}
        {!loading && !error && <TicketList tickets={tickets} />}
      </main>
    </div>
  );
};

export default App;