import { TechnicianDetails, TicketDetail } from './types';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8003/dtic';

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

// Async Mock for Ticket Detail V4 (Simulating network request)
export const fetchMockTicketDetail = async (id: number): Promise<TicketDetail> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: id,
        glpi_id: id,
        title: "Erro intermitente no acesso ao Sistema de Protocolo",
        description: `Prezados,

Desde hoje pela manhã, ao tentar acessar o módulo de cadastro de processos, o sistema apresenta lentidão extrema e, ocasionalmente, o erro "Connection Timed Out". 

Já limpei cache e tentei em outro navegador.
Anexo print do erro.`,
        status: "Em Atendimento",
        priority: "Alta",
        creation_date: "10/12/2025 09:15",
        requester: "Ana Paula Souza",
        technician: "Luciano Marcelino da Silva",
        timeline: [
          {
            id: 1,
            date: "10/12/2025 09:30",
            type: "change",
            author: "Sistema",
            content: "Status alterado de 'Novo' para 'Em Atendimento' por Luciano Marcelino da Silva"
          },
          {
            id: 2,
            date: "10/12/2025 09:35",
            type: "followup",
            author: "Luciano Marcelino da Silva",
            content: "Olá Ana Paula. Verifiquei os logs do servidor e identificamos uma sobrecarga no banco de dados. Estamos reiniciando o serviço responsável."
          },
          {
            id: 3,
            date: "10/12/2025 10:00",
            type: "followup",
            author: "Ana Paula Souza",
            content: "Obrigada, Luciano. Aguardo retorno. O setor está parado."
          },
          {
            id: 4,
            date: "10/12/2025 10:45",
            type: "change",
            author: "Luciano Marcelino da Silva",
            content: "Categoria alterada de 'Incidente > Software' para 'Incidente > Infraestrutura'"
          },
          {
            id: 5,
            date: "10/12/2025 11:15",
            type: "followup",
            author: "Luciano Marcelino da Silva",
            content: "O serviço foi restabelecido e aplicamos um patch de correção. Por favor, tente acessar novamente e confirme se a velocidade normalizou."
          }
        ]
      });
    }, 800); // 800ms simulated delay
  });
};