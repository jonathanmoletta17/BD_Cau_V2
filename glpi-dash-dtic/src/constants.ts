import { TechnicianDetails, TicketDetail } from './types';

// Usando padrão Reverse Proxy: URL relativa
// O Nginx (prod) ou Vite Proxy (dev) resolverá o destino
export const API_BASE_URL = '/api/dtic';

// Colors for Charts
export const CHART_COLORS = {
  blue: '#3B82F6',
  orange: '#F97316',
  yellow: '#EAB308',
  purple: '#8b5cf6',
  cyan: '#06b6d4',
  slate: '#64748b',
  green: '#22C55E',
  red: '#EF4444',
  grid: '#334155',
  text: '#94a3b8'
};

// Helper function to generate technician details
export const getMockTechnicianDetails = (name: string): TechnicianDetails => {
  return {
    id: Math.floor(Math.random() * 1000),
    name: name,
    role: "Analista de Suporte N2",
    status: Math.random() > 0.3 ? 'online' : 'busy',
    stats: {
      avgResolutionTime: `${Math.floor(Math.random() * 4) + 1}h ${Math.floor(Math.random() * 59)}m`,
      satisfactionScore: Number((4 + Math.random()).toFixed(1)),
      totalSolved: Math.floor(Math.random() * 200) + 50,
      currentBacklog: Math.floor(Math.random() * 10)
    },
    performanceHistory: Array.from({ length: 7 }, (_, i) => ({
      date: `D-${6 - i}`,
      count: Math.floor(Math.random() * 15) + 2
    })),
    lastTickets: [
      { id: 12000 + Math.floor(Math.random() * 100), title: "Falha na impressão em rede", date: "Hoje, 10:30", status: "Resolvido" },
      { id: 12000 + Math.floor(Math.random() * 100), title: "Configuração de VPN", date: "Ontem, 16:45", status: "Resolvido" },
      { id: 12000 + Math.floor(Math.random() * 100), title: "Atualização Office 365", date: "Ontem, 14:20", status: "Resolvido" }
    ]
  };
};
