import { useState, useEffect, useCallback } from 'react';
import { QualityAlert, QualityStats } from '../types';

import { API_BASE_URL } from '../constants';

interface UseQualityAlertsReturn {
    alerts: QualityAlert[];
    stats: QualityStats | null;
    loading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
    runChecks: () => Promise<void>;
}

export const useQualityAlerts = (): UseQualityAlertsReturn => {
    const [alerts, setAlerts] = useState<QualityAlert[]>([]);
    const [stats, setStats] = useState<QualityStats | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const [alertsRes, statsRes] = await Promise.all([
                fetch(`${API_BASE_URL}/quality/alerts?limit=50`),
                fetch(`${API_BASE_URL}/quality/stats`)
            ]);

            if (!alertsRes.ok || !statsRes.ok) {
                throw new Error('Falha ao carregar dados de qualidade');
            }

            const alertsData = await alertsRes.json();
            const statsData = await statsRes.json();

            setAlerts(alertsData);
            setStats(statsData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro desconhecido');
            console.error('Error fetching quality data:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const runChecks = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/quality/run-checks`, {
                method: 'POST'
            });
            if (!res.ok) throw new Error('Falha ao executar verificações');
            await fetchData(); // Refresh data after run
        } catch (err) {
            console.error('Error running quality checks:', err);
            // Optional: set error state or show toast
        }
    };

    useEffect(() => {
        fetchData();
        // Refresh every 5 minutes
        const interval = setInterval(fetchData, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, [fetchData]);

    return { alerts, stats, loading, error, refresh: fetchData, runChecks };
};
