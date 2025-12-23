import { useState, useEffect, useCallback } from 'react';
import { DashboardData, GeneralStats, TicketNovo, TecnicoRanking, NivelSuporte } from '../types';
import { API_BASE_URL } from '../constants';

interface UseDashboardDataResult {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export const useDashboardData = (
  startDate?: string,
  endDate?: string
): UseDashboardDataResult => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query params for filtered endpoints
      const dateParams = startDate && endDate
        ? `?inicio=${startDate}&fim=${endDate}`
        : '';

      // Fetch FILTERED data (with date range)
      const [statsRes, rankingRes] = await Promise.allSettled([
        fetch(`${API_BASE_URL}/dashboard/stats-gerais${dateParams}`),
        fetch(`${API_BASE_URL}/dashboard/ranking-tecnicos${dateParams}`)
      ]);

      // Fetch UNFILTERED data (always total - for Novos card and tickets list)
      const [unfilteredStatsRes, allNewTicketsRes] = await Promise.allSettled([
        fetch(`${API_BASE_URL}/dashboard/stats-gerais`),
        fetch(`${API_BASE_URL}/dashboard/tickets-novos`)  // NO limit, NO date filter
      ]);

      // Fetch carousel data (FILTERED by date)
      const [categoriesRes, historyRes, levelsRes] = await Promise.allSettled([
        fetch(`${API_BASE_URL}/dashboard/ranking-categorias${dateParams}`),
        fetch(`${API_BASE_URL}/dashboard/historico${dateParams}`),
        fetch(`${API_BASE_URL}/dashboard/support-levels${dateParams}`)
      ]);

      // Check for failures
      if (statsRes.status === 'rejected' || (statsRes.status === 'fulfilled' && !statsRes.value.ok)) {
        throw new Error(`Failed to fetch filtered stats: ${statsRes.status === 'rejected' ? statsRes.reason : statsRes.value.statusText}`);
      }
      if (rankingRes.status === 'rejected' || (rankingRes.status === 'fulfilled' && !rankingRes.value.ok)) {
        throw new Error(`Failed to fetch ranking: ${rankingRes.status === 'rejected' ? rankingRes.reason : rankingRes.value.statusText}`);
      }
      if (unfilteredStatsRes.status === 'rejected' || (unfilteredStatsRes.status === 'fulfilled' && !unfilteredStatsRes.value.ok)) {
        throw new Error(`Failed to fetch unfiltered stats`);
      }
      if (allNewTicketsRes.status === 'rejected' || (allNewTicketsRes.status === 'fulfilled' && !allNewTicketsRes.value.ok)) {
        throw new Error(`Failed to fetch new tickets`);
      }
      if (levelsRes.status === 'rejected' || (levelsRes.status === 'fulfilled' && !levelsRes.value.ok)) {
        throw new Error(`Failed to fetch support levels: ${levelsRes.status === 'rejected' ? levelsRes.reason : levelsRes.value.statusText}`);
      }

      // Get filtered stats (for Em Progresso, Pendentes, Resolvidos)
      const filteredStats: GeneralStats = await (statsRes as PromiseFulfilledResult<Response>).value.json();

      // Get unfiltered stats (for Novos card - always total)
      const unfilteredStats: GeneralStats = await (unfilteredStatsRes as PromiseFulfilledResult<Response>).value.json();

      // Get all new tickets (unfiltered, no limit)
      const newTickets: TicketNovo[] = await (allNewTicketsRes as PromiseFulfilledResult<Response>).value.json();

      // Get filtered ranking
      const ranking: TecnicoRanking[] = await (rankingRes as PromiseFulfilledResult<Response>).value.json();

      // Get carousel data (filtered)
      const categoriesData = categoriesRes.status === 'fulfilled' && categoriesRes.value.ok
        ? await categoriesRes.value.json()
        : [];

      const historyData = historyRes.status === 'fulfilled' && historyRes.value.ok
        ? await historyRes.value.json()
        : [];

      const levelsData = levelsRes.status === 'fulfilled' && levelsRes.value.ok
        ? await levelsRes.value.json()
        : [];

      // Transform categories to match carousel format
      const categories = categoriesData.slice(0, 5).map((cat: any) => ({
        name: cat.category_name || cat.categoria || cat.name || 'N/A',  // API usa category_name
        value: cat.ticket_count || cat.total || cat.value || 0           // API usa ticket_count
      }));

      // Levels come directly from API (real data from tickets_groups!)
      const levels: NivelSuporte[] = levelsData.length > 0 ? levelsData : [];

      // History comes directly from API (already in correct format)
      const history = historyData.length > 0 ? historyData : [];

      // Combine filtered + unfiltered metrics
      const metrics: GeneralStats = {
        novos: unfilteredStats.novos,         // ✅ UNFILTERED (always total)
        em_progresso: filteredStats.em_progresso,  // ✅ FILTERED
        pendentes: filteredStats.pendentes,        // ✅ FILTERED
        resolvidos: filteredStats.resolvidos       // ✅ FILTERED
      };

      setData({
        metrics,
        newTickets,
        ranking,
        carouselData: {
          levels,      // ✅ Derived from real filtered data
          history,     // ✅ Derived from real filtered data
          categories   // ✅ Real API data (filtered)
        },
        lastUpdated: new Date()
      });

    } catch (err) {
      console.error("Failed to fetch dashboard data", err);
      setError(`Erro ao carregar dados: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
      // Keep previous data if available, don't fallback to mock
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, API_BASE_URL]);

  // Initial fetch and interval
  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 30000); // Update every 30 seconds
    return () => clearInterval(intervalId);
  }, [fetchData, startDate, endDate]);

  return { data, loading, error, refresh: fetchData };
};