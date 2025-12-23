import { Charger, Ticket, TicketStatus } from '../types';
import { subDays, subHours, subMinutes, formatISO } from 'date-fns';

// Helper to generate dates
const now = new Date();

// Mock Tickets
const tickets: Record<number, Ticket> = {
  // Active/Occupied Tickets
  4109: { id: 4109, name: "Instalação de ponto de tomada 220v - copa subsolo", date: formatISO(subHours(now, 2)), status: TicketStatus.PROCESSING },
  4049: { id: 4049, name: "Movimentar sofá localizado no subsolo", date: formatISO(subDays(now, 1)), status: TicketStatus.PENDING },
  4052: { id: 4052, name: "Vazamento na caldeira", date: formatISO(subHours(now, 48)), status: TicketStatus.NEW },
  
  // Closed History Tickets (for Available chargers)
  3001: { id: 3001, name: "Troca de periféricos TI", date: formatISO(subDays(now, 10)), status: TicketStatus.CLOSED, solvedate: formatISO(subDays(now, 5)) },
  3002: { id: 3002, name: "Manutenção preventiva ar condicionado", date: formatISO(subDays(now, 15)), status: TicketStatus.CLOSED, solvedate: formatISO(subDays(now, 2)) },
  3003: { id: 3003, name: "Configuração de rede Wi-Fi", date: formatISO(subDays(now, 20)), status: TicketStatus.CLOSED, solvedate: formatISO(subHours(now, 1390)) }, // Matches screenshot approx
  3004: { id: 3004, name: "Reparo no sistema de segurança", date: formatISO(subDays(now, 30)), status: TicketStatus.CLOSED, solvedate: formatISO(subHours(now, 1557)) },
  3005: { id: 3005, name: "Backup de servidores", date: formatISO(subDays(now, 12)), status: TicketStatus.CLOSED, solvedate: formatISO(subHours(now, 1575)) },
};

// Mock Chargers
// We simulate the Join logic here
const rawChargers = [
  { id: 1, name: "Carregador 1", entities_id: 1, is_deleted: false, currentTicketId: null, lastTicketId: 3003, historyCount: 3 },
  { id: 2, name: "Carregador 2", entities_id: 1, is_deleted: false, currentTicketId: null, lastTicketId: 3004, historyCount: 2 },
  { id: 3, name: "Carregador 3", entities_id: 1, is_deleted: false, currentTicketId: 4109, lastTicketId: 3001, historyCount: 4 }, // Occupied
  { id: 4, name: "Carregador 4", entities_id: 1, is_deleted: false, currentTicketId: null, lastTicketId: 3005, historyCount: 1 },
  { id: 5, name: "Carregador 5", entities_id: 1, is_deleted: false, currentTicketId: null, lastTicketId: 3002, historyCount: 2 },
  { id: 6, name: "Carregador 6", entities_id: 1, is_deleted: false, currentTicketId: 4052, lastTicketId: null, historyCount: 0 }, // Occupied
  { id: 7, name: "Carregador 7", entities_id: 1, is_deleted: true, currentTicketId: null, lastTicketId: null, historyCount: 0 }, // Offline
  { id: 8, name: "Pedro Silva Souza Carvalho Pinto", entities_id: 1, is_deleted: false, currentTicketId: null, lastTicketId: null, historyCount: 0 }, // No history
  { id: 9, name: "Carregador 9 (Lab)", entities_id: 1, is_deleted: false, currentTicketId: null, lastTicketId: 3001, historyCount: 1 },
  { id: 10, name: "Carregador 10 (Recepção)", entities_id: 1, is_deleted: false, currentTicketId: null, lastTicketId: 3001, historyCount: 5 },
];

export const fetchDashboardData = async (): Promise<Charger[]> => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 600));

  return rawChargers.map(rc => {
    const charger: Charger = {
      id: rc.id,
      name: rc.name,
      entities_id: rc.entities_id,
      is_deleted: rc.is_deleted,
      totalTicketsInPeriod: rc.historyCount // Simulating the count within date range
    };

    if (rc.currentTicketId && tickets[rc.currentTicketId]) {
      charger.currentTicket = tickets[rc.currentTicketId];
    }

    if (rc.lastTicketId && tickets[rc.lastTicketId]) {
      charger.lastTicket = tickets[rc.lastTicketId];
    }

    return charger;
  });
};