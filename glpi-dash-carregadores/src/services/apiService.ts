import { Charger } from '../types';

/**
 * Serviço de API Real para integração com backend PostgreSQL/GLPI
 * 
 * Este serviço substitui o mockService.ts para buscar dados reais do backend.
 * Configure a variável de ambiente VITE_API_URL em .env.local
 */

const API_BASE_URL = '/api/sis';

/**
 * Busca dados do dashboard de carregadores
 * 
 * @param dateStart - Data inicial do período (formato: YYYY-MM-DD)
 * @param dateEnd - Data final do período (formato: YYYY-MM-DD)
 * @returns Promise com array de Chargers
 * 
 * Endpoint esperado: GET /api/dashboard/chargers?dateStart=xxx&dateEnd=xxx
 * 
 * Formato de resposta esperado:
 * ```json
 * [
 *   {
 *     "id": 1,
 *     "name": "João Silva",
 *     "entities_id": 1,
 *     "is_deleted": false,
 *     "currentTicket": {
 *       "id": 4109,
 *       "name": "Instalação de ponto de tomada",
 *       "date": "2025-12-22T10:30:00.000Z",
 *       "status": 2
 *     },
 *     "lastTicket": {
 *       "id": 3001,
 *       "name": "Troca de periféricos TI",
 *       "date": "2025-12-12T08:00:00.000Z",
 *       "status": 6,
 *       "solvedate": "2025-12-17T14:30:00.000Z"
 *     },
 *     "totalTicketsInPeriod": 4
 *   }
 * ]
 * ```
 */
export const fetchDashboardData = async (
    dateStart: string,
    dateEnd: string
): Promise<Charger[]> => {
    try {
        const params = new URLSearchParams({
            dateStart,
            dateEnd
        });

        const url = `${API_BASE_URL}/dashboard/chargers?${params}`;
        console.log('[API] Fetching dashboard data:', url);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            // Adicione autenticação se necessário
            // headers: {
            //   'Authorization': `Bearer ${token}`,
            //   'Content-Type': 'application/json',
            // },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(
                `Failed to fetch dashboard data: ${response.status} ${response.statusText}\n${errorText}`
            );
        }

        const data: Charger[] = await response.json();
        console.log('[API] Dashboard data received:', data.length, 'chargers');

        return data;
    } catch (error) {
        console.error('[API] Error fetching dashboard data:', error);
        throw error;
    }
};

/**
 * Healthcheck do backend
 * Endpoint esperado: GET /api/health
 */
export const checkAPIHealth = async (): Promise<boolean> => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch (error) {
        console.error('[API] Health check failed:', error);
        return false;
    }
};
