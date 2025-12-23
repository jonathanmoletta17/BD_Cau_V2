
import { Ticket, TicketStatus, KPIStats } from '../types';

const API_BASE = '/api/dtic/search';

interface SearchResponse {
    items: any[];
    total: number;
    page: number;
    pages: number;
}

interface StatsResponse {
    by_status: { id?: number; label: string; value: number }[];
    by_priority: { id?: number; label: string; value: number }[];
    total: number;
}

export const searchTickets = async (
    q: string,
    status: TicketStatus | 'resolved' | null
): Promise<Ticket[]> => {
    const params = new URLSearchParams();
    if (q) params.append('q', q);

    if (status) {
        if (status === 'resolved') {
            params.append('status', '5,6');
        } else {
            params.append('status', status.toString());
        }
    }

    params.append('per_page', '50');

    // Add timestamp to prevent caching if needed, though search typically isn't cached aggressively
    const res = await fetch(`${API_BASE}?${params.toString()}`);
    if (!res.ok) throw new Error('Falha na busca');
    const data: SearchResponse = await res.json();

    return data.items.map((item: any) => ({
        id: item.id,
        name: item.titulo,
        content: item.descricao,
        date_creation: item.data_criacao,
        date_mod: item.data_atualizacao,
        status: item.status_id,
        entity: { id: 0, name: item.entidade },
        category: item.categoria ? { id: 0, name: item.categoria } : null,
        requester: item.requerente ? { id: 0, name: item.requerente, username: item.requerente } : null,
        technician: item.tecnico ? { id: 0, name: item.tecnico, username: item.tecnico } : null,
        group: item.grupo ? { id: 0, name: item.grupo } : null
    }));
};

export const getStats = async (q: string): Promise<KPIStats> => {
    const params = new URLSearchParams();
    if (q) params.append('q', q); // Stats respect query filters but usually NOT status filters (to show distribution)

    const res = await fetch(`${API_BASE}/stats?${params.toString()}`);
    if (!res.ok) throw new Error('Falha ao obter estatísticas');
    const data: StatsResponse = await res.json();

    const stats: KPIStats = {
        new: 0,
        processing: 0,
        planned: 0,
        pending: 0,
        resolved: 0
    };

    data.by_status.forEach((item) => {
        const id = item.id;
        const val = item.value;
        if (id === 1) stats.new += val;
        else if (id === 2) stats.processing += val;
        else if (id === 3) stats.planned += val;
        else if (id === 4) stats.pending += val;
        else if (id === 5 || id === 6) stats.resolved += val;
    });

    return stats;
};
