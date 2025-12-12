"""
API Helper Functions - V3
Python helpers para trabalhar com IDs corretos
"""
from typing import List, Dict, Optional
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from src.core import Database
from src.modules.dtic.tickets import Ticket, TicketUser, TicketGroup
from src.modules.dtic.metadata import User, Group


class TicketAPIHelper:
    """Helper class para queries de tickets prontas para uso com GLPI API."""
    
    @staticmethod
    def get_ticket_by_glpi_id(glpi_id: int, session: Session = None) -> Optional[Dict]:
        """
        Busca ticket pelo GLPI ID (não pelo ID interno).
        Retorna dicionário com IDs corretos para uso com API.
        
        Args:
            glpi_id: ID do ticket no GLPI
            session: SQLAlchemy session (opcional)
            
        Returns:
            Dict com ticket e atores, ou None se não encontrado
        """
        close_session = False
        if not session:
            session = Database.get_session(context="dtic")
            close_session = True
        
        try:
            # Buscar ticket
            ticket = session.query(Ticket).filter(Ticket.glpi_id == glpi_id).first()
            
            if not ticket:
                return None
            
            # Buscar usuários
            users_query = (
                session.query(User.id, User.name, User.realname, TicketUser.type)
                .join(TicketUser, TicketUser.user_id == User.id)
                .filter(TicketUser.ticket_id == ticket.id)
            )
            
            users = [
                {
                    'user_id': u.id,  # Já é GLPI ID
                    'name': u.name,
                    'realname': u.realname,
                    'type': u.type,
                    'type_label': {1: 'Requester', 2: 'Assigned', 3: 'Observer'}.get(u.type, 'Unknown')
                }
                for u in users_query.all()
            ]
            
            # Buscar grupos
            groups_query = (
                session.query(Group.id, Group.name, TicketGroup.type)
                .join(TicketGroup, TicketGroup.group_id == Group.id)
                .filter(TicketGroup.ticket_id == ticket.id)
            )
            
            groups = [
                {
                    'group_id': g.id,  # Já é GLPI ID
                    'name': g.name,
                    'type': g.type,
                    'type_label': {1: 'Requester', 2: 'Assigned'}.get(g.type, 'Unknown')
                }
                for g in groups_query.all()
            ]
            
            return {
                'ticket_id': ticket.glpi_id,  # ID para usar na API
                'titulo': ticket.titulo,
                'descricao': ticket.descricao,
                'status_id': ticket.status_id,
                'prioridade_id': ticket.prioridade_id,
                'criado_em': ticket.criado_em,
                'solucionado_em': ticket.solucionado_em,
                'fechado_em': ticket.fechado_em,
                'url': ticket.url,
                'users': users,
                'groups': groups
            }
        finally:
            if close_session:
                session.close()

    @staticmethod
    def list_tickets_api_ready(limit: int = 100, offset: int = 0, session: Session = None) -> List[Dict]:
        """
        Lista tickets com IDs prontos para API.
        
        Args:
            limit: Número de registros
            offset: Paginação
            session: SQLAlchemy session (opcional)
            
        Returns:
            Lista de dicts com IDs corretos
        """
        close_session = False
        if not session:
            session = Database.get_session(context="dtic")
            close_session = True
        
        try:
            tickets = (
                session.query(Ticket)
                .order_by(Ticket.glpi_id.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            
            return [
                {
                    'ticket_id': t.glpi_id,  # ID para API
                    'titulo': t.titulo,
                    'status_id': t.status_id,
                    'criado_em': t.criado_em,
                    'url': t.url
                }
                for t in tickets
            ]
        finally:
            if close_session:
                session.close()


# Exemplo de uso
if __name__ == "__main__":
    # Buscar ticket específico
    ticket = TicketAPIHelper.get_ticket_by_glpi_id(10615)
    
    if ticket:
        print(f"Ticket ID (para API): {ticket['ticket_id']}")
        print(f"Título: {ticket['titulo']}")
        print(f"Usuários: {len(ticket['users'])}")
        print(f"\nPara fazer request na API:")
        print(f"  GET /apirest.php/Ticket/{ticket['ticket_id']}")
    
    # Listar tickets
    tickets = TicketAPIHelper.list_tickets_api_ready(limit=5)
    print(f"\nÚltimos 5 tickets (IDs para API):")
    for t in tickets:
        print(f"  {t['ticket_id']}: {t['titulo'][:50]}")
