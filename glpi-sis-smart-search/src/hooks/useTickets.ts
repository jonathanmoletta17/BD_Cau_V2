import { useState, useEffect, useCallback } from 'react';
import { Ticket, KPIStats, TicketStatus } from '@/types';

const API_BASE_URL = '/api/v1/sis/smart-search';

interface UseTicketsResult {
  tickets: Ticket[];
  stats: KPIStats;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export const useTickets = (
  searchTerm: string,
  selectedStatus: TicketStatus | 'resolved' | null
): UseTicketsResult => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<KPIStats>({
    new: 0,
    processing: 0,
    planned: 0,
    pending: 0,
    resolved: 0
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query params for tickets
      const params = new URLSearchParams();
      if (searchTerm) {
        params.append('search', searchTerm);
      }
      
      // Map 'resolved' to multiple statuses
      if (selectedStatus) {
        if (selectedStatus === 'resolved') {
          // Resolved = SOLVED (5) or CLOSED (6)
          // Backend doesn't support multiple status, so we filter client-side for "resolved"
          // OR we fetch all and filter frontend (simpler for now)
        } else {
          params.append('status', selectedStatus.toString());
        }
      }

      const queryStr = params.toString() ? `?${params.toString()}` : '';

      // Fetch tickets and metrics in parallel
      const [ticketsRes, metricsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/tickets${queryStr}`),
        fetch(`${API_BASE_URL}/metrics`)
      ]);

      if (!ticketsRes.ok || !metricsRes.ok) {
        throw new Error('Failed to fetch data from API');
      }

      const ticketsData = await ticketsRes.json();
      const metricsData = await metricsRes.json();

      // Handle resolved filter client-side (status 5 or 6)
      let filteredTickets = ticketsData.tickets || [];
      if (selectedStatus === 'resolved') {
        filteredTickets = filteredTickets.filter((t: Ticket) => 
          t.status === 5 || t.status === 6
        );
      }

      setTickets(filteredTickets);
      setStats(metricsData);

    } catch (err) {
      console.error('Failed to fetch tickets:', err);
      setError('Falha ao carregar dados. Verifique a conexão com o backend.');
      setTickets([]);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, selectedStatus]);

  // Initial fetch and auto-refresh every 30s
  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 30000);
    return () => clearInterval(intervalId);
  }, [fetchData]);

  return { tickets, stats, loading, error, refresh: fetchData };
};
