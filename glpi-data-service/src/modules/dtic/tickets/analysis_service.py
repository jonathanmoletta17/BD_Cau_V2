
from sqlalchemy.orm import Session
from sqlalchemy import func, case, text
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .models import Ticket
from .relationship_models import TicketChange

class TicketAnalysisService:
    
    @staticmethod
    def get_ticket_timeline(db: Session, ticket_id: int) -> List[Dict[str, Any]]:
        """
        Reconstrói a linha do tempo legível de um ticket baseado em seus logs.
        Retorna uma lista cronológica de eventos.
        """
        # Buscar ID interno se for passado GLPI ID (assumindo que a entrada pode ser GLPI ID)
        # Mas idealmente usamos ID interno. Vamos suportar ambos se necessário, mas focar no interno ou converter.
        # Por padrão, assumimos que ticket_id é o ID do GLPI para facilidade de uso do agente,
        # mas precisamos buscar o ID interno para o join.
        
        ticket = db.query(Ticket).filter(Ticket.glpi_id == ticket_id).first()
        if not ticket:
            return []
            
        internal_id = ticket.id
        
        changes = db.query(TicketChange).filter(
            TicketChange.ticket_id == internal_id
        ).order_by(TicketChange.data_mudanca.asc()).all()
        
        timeline = []
        
        # Evento de Criação (Do Ticket, não Change)
        timeline.append({
            "timestamp": ticket.criado_em.isoformat() if ticket.criado_em else None,
            "actor": "Solicitante", # Poderia buscar o nome do criador se tivéssemos o ID
            "action": "Ticket Criado",
            "details": f"Título: {ticket.titulo}",
            "type": "CREATE"
        })
        
        for change in changes:
            event = {
                "timestamp": change.data_mudanca.isoformat() if change.data_mudanca else None,
                "actor": change.usuario_nome or "Sistema/Desconhecido",
                "field": change.campo,
                "old": change.valor_antigo,
                "new": change.valor_novo,
                "type": "UPDATE"
            }
            
            # Formatação Human-Readable
            if change.campo == 'status':
                event['description'] = f"Alterou status de '{change.valor_antigo}' para '{change.valor_novo}'"
            elif change.campo == 'technician':
                event['description'] = f"Atribuiu técnico: {change.valor_novo}"
            elif change.campo == 'content':
                event['description'] = "Adicionou um acompanhamento/tarefa"
                event['type'] = "CONTENT"
            elif change.campo == 'priority':
                 event['description'] = f"Mudou prioridade para {change.valor_novo}"
            else:
                event['description'] = f"Atualizou {change.campo}: {change.valor_novo}"
                
            timeline.append(event)
            
        return timeline

    @staticmethod
    def analyze_ticket_health(db: Session, ticket_id: int) -> Dict[str, Any]:
        """
        Calcula métricas de saúde de um ticket específico.
        """
        ticket = db.query(Ticket).filter(Ticket.glpi_id == ticket_id).first()
        if not ticket:
            return {"error": "Ticket not found"}
            
        internal_id = ticket.id
        changes = db.query(TicketChange).filter(TicketChange.ticket_id == internal_id).all()
        
        # Métricas
        ping_pong_count = 0
        reopen_count = 0
        last_status = None
        
        technician_changes = [c for c in changes if c.campo in ['technician', 'group']]
        status_changes = [c for c in changes if c.campo == 'status']
        
        # Contar reatribuições
        ping_pong_count = len(technician_changes)
        
        # Contar reaberturas (De Fechado/Solucionado para Processando/Novo)
        # Simplificação: Se valor_antigo contem "Solucionado" ou "Fechado"
        for sc in status_changes:
            old_v = str(sc.valor_antigo).lower()
            new_v = str(sc.valor_novo).lower()
            if ('solucionado' in old_v or 'fechado' in old_v) and \
               ('processando' in new_v or 'novo' in new_v or 'atribuído' in new_v):
                reopen_count += 1
        
        # Tempo desde última interação
        last_interaction = ticket.criado_em
        if changes:
            last_change_date = max(c.data_mudanca for c in changes if c.data_mudanca)
            if last_change_date:
                last_interaction = last_change_date
        
        hours_idle = 0
        if last_interaction:
            # Converter para offset-naive se necessário ou garantir timezone aware
            now = datetime.now(last_interaction.tzinfo)
            delta = now - last_interaction
            hours_idle = delta.total_seconds() / 3600
            
        return {
            "ticket_id": ticket_id,
            "reatribuicoes": ping_pong_count,
            "reaberturas": reopen_count,
            "horas_sem_interacao": round(hours_idle, 2),
            "saude": "Ruim" if ping_pong_count > 3 or reopen_count > 0 else "Boa"
        }

    @staticmethod
    def get_process_bottlenecks(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """
        Identifica gargalos no processo analisando tickets dos últimos X dias.
        Retorna tempo médio em cada status.
        Esta é uma query complexa que exige Window Functions, difícil em ORM puro simples.
        Usaremos SQL Raw via SQLAlchemy para performance e clareza.
        """
        
        # SQL para calcular tempo em cada status (Dwell Time)
        # Simplificação: Diferença entre uma mudança de status e a próxima do mesmo ticket
        sql = text("""
            WITH StatusChanges AS (
                SELECT 
                    ticket_id,
                    valor_novo as status_nome,
                    data_mudanca as start_time,
                    LEAD(data_mudanca) OVER (PARTITION BY ticket_id ORDER BY data_mudanca) as end_time
                FROM dtic.ticket_changes
                WHERE campo = 'status'
                  AND data_mudanca >= NOW() - INTERVAL ':days days'
            )
            SELECT 
                status_nome,
                COUNT(*) as ocorrencias,
                AVG(EXTRACT(EPOCH FROM (COALESCE(end_time, NOW()) - start_time))/3600)::NUMERIC(10,2) as media_horas
            FROM StatusChanges
            WHERE end_time IS NOT NULL
            GROUP BY status_nome
            ORDER BY media_horas DESC
        """)
        
        result = db.execute(sql, {"days": days}).fetchall()
        
        bottlenecks = []
        for row in result:
            bottlenecks.append({
                "status": row.status_nome,
                "ocorrencias": row.ocorrencias,
                "tempo_medio_horas": float(row.media_horas)
            })
            
        return bottlenecks
