export enum TicketStatus {
  NEW = 1,
  PROCESSING = 2,
  PLANNED = 3,
  PENDING = 4,
  SOLVED = 5,
  CLOSED = 6
}

export interface Ticket {
  id: number;
  name: string;
  date: string; // ISO string creation date
  status: TicketStatus;
  solvedate?: string | null; // ISO string
}

export interface Charger {
  id: number;
  name: string;
  entities_id: number;
  is_deleted: boolean;
  // Computed/Joined fields for frontend convenience
  currentTicket?: Ticket;
  lastTicket?: Ticket;
  totalTicketsInPeriod?: number; // For ranking
}

export interface DashboardStats {
  available: number;
  occupied: number;
  offline: number;
  total: number;
}

export interface DateRange {
  start: string;
  end: string;
}