import React, { useState, useEffect, useMemo } from 'react';
import { RefreshCw, Calendar, Box } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

import { Charger, DashboardStats, TicketStatus } from './types';
import { fetchDashboardData } from './services/apiService';
import StatCards from './components/StatCards';
import { AvailableList, OccupiedList, RankingList } from './components/DashboardColumns';

const App: React.FC = () => {
  const [chargers, setChargers] = useState<Charger[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<string>(format(new Date(), 'HH:mm:ss'));

  // Date Filters
  const [dateStart, setDateStart] = useState<string>(format(new Date(), 'yyyy-MM-01'));
  const [dateEnd, setDateEnd] = useState<string>(format(new Date(), 'yyyy-MM-dd'));

  // Clock
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(format(new Date(), 'HH:mm:ss'));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Initial Data Fetch
  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchDashboardData(dateStart, dateEnd);
      setChargers(data);
    } catch (error) {
      console.error("Failed to load data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Only load initial data if dates are set? Or default load.
    // For now, load once. If specific deps needed, user can add logic.
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run once on mount

  // Compute Derived State (Business Logic)
  const { stats, availableList, occupiedList, rankingList, totalAttributed } = useMemo(() => {
    let availableCount = 0;
    let occupiedCount = 0;
    let offlineCount = 0;

    const available: Charger[] = [];
    const occupied: Charger[] = [];

    // Sort logic for ranking (descending by totalTicketsInPeriod)
    const ranking = [...chargers]
      .filter(c => !c.is_deleted)
      .sort((a, b) => (b.totalTicketsInPeriod || 0) - (a.totalTicketsInPeriod || 0));

    const totalAttributedCount = ranking.reduce((acc, curr) => acc + (curr.totalTicketsInPeriod || 0), 0);

    chargers.forEach(charger => {
      if (charger.is_deleted) {
        offlineCount++;
      } else if (charger.currentTicket) {
        occupiedCount++;
        occupied.push(charger);
      } else {
        availableCount++;
        available.push(charger);
      }
    });

    const statistics: DashboardStats = {
      available: availableCount,
      occupied: occupiedCount,
      offline: offlineCount,
      total: chargers.length
    };

    return {
      stats: statistics,
      availableList: available,
      occupiedList: occupied,
      rankingList: ranking,
      totalAttributed: totalAttributedCount
    };
  }, [chargers]);

  return (
    <div className="flex flex-col h-screen bg-slate-950 p-4 md:p-6 overflow-hidden font-sans">
      {/* --- HEADER --- */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 shrink-0">
        <div className="flex items-center gap-4">
          <div className="bg-slate-800 p-3 rounded-xl border border-slate-700 shadow-lg">
            <Box className="w-8 h-8 text-blue-500" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">CARREGADORES</h1>
            <p className="text-slate-400 text-sm font-medium">Em tempo real</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 bg-slate-900/50 p-2 rounded-xl border border-slate-800 backdrop-blur">
          <div className="flex items-center gap-2 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700/50">
            <Calendar size={14} className="text-slate-400" />
            <span className="text-xs text-slate-500 font-medium mr-1">Início:</span>
            <input
              type="date"
              value={dateStart}
              onChange={(e) => setDateStart(e.target.value)}
              className="bg-transparent text-sm text-slate-200 outline-none w-28 appearance-none [&::-webkit-calendar-picker-indicator]:invert"
            />
          </div>

          <div className="flex items-center gap-2 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700/50">
            <span className="text-xs text-slate-500 font-medium mr-1">Fim:</span>
            <input
              type="date"
              value={dateEnd}
              onChange={(e) => setDateEnd(e.target.value)}
              className="bg-transparent text-sm text-slate-200 outline-none w-28 appearance-none [&::-webkit-calendar-picker-indicator]:invert"
            />
          </div>

          <button
            onClick={loadData}
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-1.5 rounded-lg text-sm font-semibold transition-colors shadow-lg shadow-blue-500/20"
          >
            Aplicar
          </button>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right hidden lg:block">
            <div className="font-mono text-3xl font-bold text-slate-200 tracking-wider">
              {currentTime}
            </div>
          </div>
          <button
            onClick={loadData}
            className={`p-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl border border-slate-700 transition-all ${loading ? 'animate-spin' : ''}`}
            title="Refresh Data"
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </header>

      {/* --- KPIs --- */}
      <div className="shrink-0">
        <StatCards stats={stats} />
      </div>

      {/* --- MAIN GRID --- */}
      <main className="flex-1 min-h-0 flex flex-col lg:flex-row gap-6 pb-2 overflow-hidden">
        {/* Col 1: Available */}
        <div className="flex-1 lg:w-1/3 flex flex-col min-h-0 h-full">
          <AvailableList chargers={availableList} />
        </div>

        {/* Col 2: Occupied */}
        <div className="flex-1 lg:w-1/3 flex flex-col min-h-0 h-full">
          <OccupiedList chargers={occupiedList} />
        </div>

        {/* Col 3: Ranking */}
        <div className="flex-1 lg:w-1/3 flex flex-col min-h-0 h-full">
          <RankingList chargers={rankingList} totalAttributed={totalAttributed} />
        </div>
      </main>
    </div>
  );
};
export default App;