// Interfaces based on src/models/dashboard/models.py

export interface GeneralStats {
  novos: number;        // Card Azul
  em_progresso: number; // Card Laranja
  pendentes: number;    // Card Amarelo
  resolvidos: number;   // Card Verde
}

export interface TicketNovo {
  id: number;
  titulo: string;
  solicitante: string;
  data: string;       // Formato: dd/MM/yyyy HH:mm
  entidade: string;
  prioridade: string; // "Baixa", "Média", "Alta"
}

export interface TecnicoRanking {
  tecnico: string;
  tickets: number;
}

export interface NivelSuporte {
  nivel: string; // "N1", "N2", "N3"
  total: number;
}

export interface TechnicianDetails {
  id: number;
  name: string;
  avatarUrl?: string; // Optional, might use initials
  role: string;
  status: 'online' | 'offline' | 'busy';
  stats: {
    avgResolutionTime: string; // "2h 30m"
    satisfactionScore: number; // 4.8
    totalSolved: number;
    currentBacklog: number;
  };
  performanceHistory: { date: string; count: number }[]; // Para o gráfico sparkline
  lastTickets: { id: number; title: string; date: string; status: string }[];
}

export interface MetricsCarouselData {
  levels: NivelSuporte[]; // View 1
  history: { date: string; created: number; resolved: number }[]; // View 2
  categories: { name: string; value: number }[]; // View 3
}

// --- V4 Interfaces (Ticket Detail API) ---

export interface TicketTimelineItem {
  id: number;
  date: string; // ISO Format or Relative
  type: 'followup' | 'change'; // 'followup' = comentário, 'change' = log
  author: string;
  content: string;
}

export interface TicketDetail {
  id: number;
  glpi_id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  creation_date: string;
  solve_date?: string;
  requester: string;
  technician?: string; // Optional, can be unassigned
  timeline: TicketTimelineItem[];
}

export interface DashboardData {
  metrics: GeneralStats;
  newTickets: TicketNovo[];
  ranking: TecnicoRanking[];
  carouselData: MetricsCarouselData; 
  lastUpdated: Date;
}