
import { useState, useEffect } from 'react';
import { TicketDetail } from '../types';
import { API_BASE_URL } from '../constants';

interface UseTicketDetailResult {
    data: TicketDetail | null;
    loading: boolean;
    error: string | null;
}

export const useTicketDetail = (ticketId: number | null): UseTicketDetailResult => {
    const [data, setData] = useState<TicketDetail | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!ticketId) {
            setData(null);
            return;
        }

        const fetchDetail = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/dashboard/ticket/${ticketId}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch ticket detail: ${response.statusText}`);
                }
                const result: TicketDetail = await response.json();
                setData(result);
            } catch (err) {
                console.error("Failed to fetch ticket detail", err);
                setError(err instanceof Error ? err.message : 'Unknown error');
                setData(null);
            } finally {
                setLoading(false);
            }
        };

        fetchDetail();
    }, [ticketId]);

    return { data, loading, error };
};
