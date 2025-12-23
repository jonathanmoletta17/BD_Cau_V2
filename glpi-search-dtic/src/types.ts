export enum TicketStatus {
  NEW = 1,
  PROCESSING = 2, // Em andamento (Atribuído)
  PLANNED = 3,
  PENDING = 4,
  SOLVED = 5,
  CLOSED = 6
}

export interface TicketEntity {
  id: number;
  name: string; // e.g., "Palácio Piratini"
}

export interface TicketCategory {
  id: number;
  name: string; // e.g., "Ar Condicionado"
}

export interface TicketUser {
  id: number;
  name: string;
  username: string; // e.g., "lauro-junior"
}

export interface TicketGroup {
  id: number;
  name: string;
}

export interface Ticket {
  id: number;
  name: string; // Title
  content: string; // Description
  date_creation: string; // ISO Date
  date_mod: string | null;
  status: TicketStatus;
  entity: TicketEntity;
  category: TicketCategory | null;
  requester: TicketUser | null;
  technician: TicketUser | null;
  group: TicketGroup | null;
}

export interface KPIStats {
  new: number;
  processing: number;
  planned: number;
  pending: number;
  resolved: number;
}