from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_, desc, literal
from datetime import datetime, timedelta, timezone

from src.modules.sis.carregadores.models import Carregador
from src.modules.sis.tickets.models import Ticket
from src.modules.sis.tickets.relationship_models import TicketItem
from src.modules.sis.metadata.models import Entity  # For location name if needed
from src.modules.sis.config.models import Setting
from src.modules.sis.carregadores.expediente import business_minutes_today, is_in_expediente

# Constants
STATUS_OCUPADO = [2, 3, 4] # Processing, Planned, Pending
STATUS_DISPONIVEL = [1, 5, 6] # New, Solved, Closed
CARREGADOR_ITEMTYPE = 'PluginGenericobjectCarregador'

class CarregadoresService:
    @staticmethod
    def get_kanban(db: Session):
        # 1. Config de expediente
        cfg = db.query(Setting).filter(Setting.key == 'expediente').first()
        start_hhmm = (cfg.value or {}).get('startHour', '08:00') if cfg else '08:00'
        end_hhmm = (cfg.value or {}).get('endHour', '18:00') if cfg else '18:00'

        # 2. Fetch all Carregadores
        carregadores = db.query(Carregador).filter(Carregador.is_deleted == False).all()
        
        ocupados = []
        disponiveis = []
        
        for charger in carregadores:
            # Check for Active Tickets linked to this charger
            # Join TicketItem -> Ticket
            # Condition: TicketItem.itemtype == CARREGADOR_ITEMTYPE
            # Condition: TicketItem.items_id == charger.id
            # Condition: Ticket.glpi_id == TicketItem.tickets_id (Mirroring logic)
            # Condition: Ticket.status in STATUS_OCUPADO
            
            active_ticket = (
                db.query(Ticket)
                .join(TicketItem, Ticket.glpi_id == TicketItem.tickets_id)
                .filter(
                    TicketItem.itemtype == CARREGADOR_ITEMTYPE,
                    TicketItem.items_id == charger.id,
                    Ticket.status_id.in_(STATUS_OCUPADO),
                    Ticket.is_deleted == False
                )
                .first() # Assume one active ticket per charger max? Or take first.
            )
            
            if active_ticket:
                # Ocupado
                start_time = active_ticket.atualizado_em or active_ticket.criado_em
                tempo_min = 0
                if start_time:
                    try:
                        tempo_min = int((datetime.now(start_time.tzinfo) - start_time).total_seconds() / 60)
                    except:
                         tempo_min = 0

                # Get Entity/Location Name?
                ent_name = f"Ent:{active_ticket.entidade_id}"
                ent = db.query(Entity).filter(Entity.id == active_ticket.entidade_id).first()
                if ent:
                    ent_name = ent.name

                # Métricas diárias (expediente)
                now_utc = datetime.now(timezone.utc)
                tempo_ocupado_hoje = business_minutes_today(start_time, now_utc, start_hhmm, end_hhmm)
                expediente = "em" if is_in_expediente(now_utc, start_hhmm, end_hhmm) else "fim"

                ocupados.append({
                    "id": charger.id,
                    "nome": charger.name,
                    "ticket": {
                        "id": active_ticket.glpi_id,
                        "titulo": active_ticket.titulo,
                        "localizacao": ent_name
                    },
                    "tempo_min": tempo_min,
                    "tempo_ocupado_min_hoje": tempo_ocupado_hoje,
                    "expediente_status": expediente
                })
            else:
                # Disponivel - Find last closed ticket
                last_ticket = (
                    db.query(Ticket)
                    .join(TicketItem, Ticket.glpi_id == TicketItem.tickets_id)
                    .filter(
                        TicketItem.itemtype == CARREGADOR_ITEMTYPE,
                        TicketItem.items_id == charger.id,
                        Ticket.status_id.in_([5, 6]), # Solved/Closed
                        Ticket.is_deleted == False
                    )
                    .order_by(desc(Ticket.solucionado_em))
                    .first()
                )
                
                last_ticket_data = None
                tempo_min = 0
                
                if last_ticket:
                    end_time = last_ticket.solucionado_em or last_ticket.fechado_em
                    if end_time:
                        try:
                            tempo_min = int((datetime.now(end_time.tzinfo) - end_time).total_seconds() / 60)
                        except:
                            tempo_min = 0
                    
                    last_ticket_data = {
                        "id": last_ticket.glpi_id,
                        "titulo": last_ticket.titulo,
                        "localizacao": ""
                    }

                # Métricas diárias (expediente)
                now_utc = datetime.now(timezone.utc)
                tempo_disponivel_hoje = business_minutes_today((last_ticket.solucionado_em or last_ticket.fechado_em) if last_ticket else None, now_utc, start_hhmm, end_hhmm)
                expediente = "em" if is_in_expediente(now_utc, start_hhmm, end_hhmm) else "fim"

                disponiveis.append({
                    "id": charger.id,
                    "nome": charger.name,
                    "ultimo_ticket": last_ticket_data,
                    "tempo_min": tempo_min,
                    "tempo_disponivel_min_hoje": tempo_disponivel_hoje,
                    "expediente_status": expediente
                })

        return {"ocupados": ocupados, "disponiveis": disponiveis}

    @staticmethod
    def get_ranking(db: Session, start_date: str = None, end_date: str = None):
        """
        Ranking of chargers based on number of resolved tickets.
        """
        # Parse dates
        start = None
        end = None
        if start_date:
            try:
                 start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except: pass
        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except: pass

        # Query: Count tickets per Carregador
        # Join TicketItem -> Ticket
        # Filter: Status solved/closed
        
        query = (
            db.query(
                Carregador.id,
                Carregador.name,
                func.count(Ticket.id).label('tickets_atribuidos')
            )
            .join(TicketItem, and_(
                TicketItem.itemtype == CARREGADOR_ITEMTYPE,
                TicketItem.items_id == Carregador.id
            ))
            .join(Ticket, Ticket.glpi_id == TicketItem.tickets_id)
            .filter(
                Ticket.status_id.in_([5, 6]), # Solved/Closed
                Ticket.is_deleted == False
            )
        )
        
        if start:
            query = query.filter(Ticket.solucionado_em >= start)
        if end:
            query = query.filter(Ticket.solucionado_em <= end)
            
        results = (
            query
            .group_by(Carregador.id, Carregador.name)
            .order_by(desc('tickets_atribuidos'))
            .limit(10)
            .all()
        )
        
        return [
            {
                "id": row.id,
                "nome": row.name,
                "tickets_atribuidos": row.tickets_atribuidos
            }
            for row in results
        ]

    @staticmethod
    def get_list(db: Session):
        # Returns flat list with status
        kanban = CarregadoresService.get_kanban(db)
        result = []
        
        # Ocupados
        for i in kanban['ocupados']:
            result.append({
                "id": i['id'],
                "nome": i['nome'],
                "status": "ocupado",
                "localizacao": i['ticket']['localizacao'],
                "tempo_atribuido": f"{i['tempo_min']} min",
                "tempo_disponivel": None,
                "ticket_id": i['ticket']['id'],
                "ref_date": None,
                "tempo_ocupado_min_hoje": i.get('tempo_ocupado_min_hoje', 0),
                "tempo_disponivel_min_hoje": 0,
                "expediente_status": i.get('expediente_status', 'aguardando')
            })
            
        # Disponiveis
        for i in kanban['disponiveis']:
             result.append({
                "id": i['id'],
                "nome": i['nome'],
                "status": "disponivel",
                "localizacao": None,
                "tempo_atribuido": None,
                "tempo_disponivel": f"{i['tempo_min']} min",
                "ticket_id": i['ultimo_ticket']['id'] if i['ultimo_ticket'] else None,
                "ref_date": None,
                "tempo_ocupado_min_hoje": 0,
                "tempo_disponivel_min_hoje": i.get('tempo_disponivel_min_hoje', 0),
                "expediente_status": i.get('expediente_status', 'aguardando')
            })
            
        return result
