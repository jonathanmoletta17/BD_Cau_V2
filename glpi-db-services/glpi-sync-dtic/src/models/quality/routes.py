"""
Quality Monitoring API Routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime

from src.core.database import get_db_session
from .schemas import (
    AlertSummary, 
    AlertDetail, 
    QualitySummaryItem,
    RunChecksResponse,
    ResolveAlertRequest
)
from ...services.quality.monitor import QualityMonitor
from ...services.quality.rules import QUALITY_RULES, RULE_METADATA

router = APIRouter(prefix="/quality", tags=["quality"])


@router.get("/alerts", response_model=List[AlertSummary])
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity (HIGH, MEDIUM, LOW)"),
    rule_id: Optional[str] = Query(None, description="Filter by rule ID"),
    limit: int = Query(50, le=200, description="Max results"),
    db: Session = Depends(get_db_session)
):
    """
    Lista alertas ativos de qualidade GLPI.
    Utiliza view 'active_alerts' que já traz dados enriquecidos.
    """
    try:
        # Build query dynamically
        where_clauses = []
        params = {}
        
        if severity:
            where_clauses.append("severity = :severity")
            params['severity'] = severity
        if rule_id:
            where_clauses.append("rule_id = :rule_id")
            params['rule_id'] = rule_id
        
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = text(f"""
            SELECT * FROM dtic.active_alerts
            WHERE 1=1 {where_sql}
            ORDER BY detected_at DESC
            LIMIT :limit
        """)
        params['limit'] = limit
        
        result = db.execute(query, params)
        alerts = [AlertSummary(**dict(row._mapping)) for row in result]
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar alertas: {str(e)}")


@router.get("/alerts/{alert_id}", response_model=AlertDetail)
async def get_alert_detail(
    alert_id: int,
    db: Session = Depends(get_db_session)
):
    """Obtém detalhes completos de um alerta específico."""
    try:
        query = text("""
            SELECT * FROM dtic.quality_alerts
            WHERE id = :alert_id
        """)
        result = db.execute(query, {'alert_id': alert_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        return AlertDetail(**dict(result._mapping))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar alerta: {str(e)}")


@router.get("/summary", response_model=List[QualitySummaryItem])
async def get_quality_summary(
    db: Session = Depends(get_db_session)
):
    """
    Retorna resumo agregado de alertas ativos por regra.
    Utiliza view 'quality_summary'.
    """
    try:
        query = text("SELECT * FROM dtic.quality_summary")
        result = db.execute(query)
        summary = [QualitySummaryItem(**dict(row._mapping)) for row in result]
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo: {str(e)}")


@router.post("/run-checks", response_model=RunChecksResponse)
async def run_quality_checks(
    db: Session = Depends(get_db_session)
):
    """
    Executa manualmente todas as verificações de qualidade.
    Normalmente executado pelo scheduler, mas pode ser chamado manualmente.
    """
    try:
        monitor = QualityMonitor(db)
        results = monitor.run_all_checks()
        return RunChecksResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao executar verificações: {str(e)}"
        )


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    request: ResolveAlertRequest,
    db: Session = Depends(get_db_session)
):
    """Marca um alerta como resolvido."""
    try:
        monitor = QualityMonitor(db)
        monitor.resolve_alert(alert_id, request.user_id)
        
        return {
            "status": "resolved",
            "alert_id": alert_id,
            "resolved_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao resolver alerta: {str(e)}"
        )


@router.get("/rules")
async def get_available_rules():
    """
    Lista todas as regras de qualidade disponíveis com metadados.
    """
    rules_info = []
    for rule_id, config in QUALITY_RULES.items():
        rules_info.append({
            'rule_id': rule_id,
            'name': config['name'],
            'description': config['description'],
            'severity': config['severity'],
            'action': config['action'],
            'threshold': config['threshold'],
            'metadata': RULE_METADATA.get(rule_id, {})
        })
    return rules_info


@router.get("/stats")
async def get_quality_stats(
    db: Session = Depends(get_db_session)
):
    """Estatísticas gerais do sistema de qualidade."""
    try:
        query = text("""
            SELECT 
                COUNT(*) FILTER (WHERE severity = 'HIGH') as high_severity,
                COUNT(*) FILTER (WHERE severity = 'MEDIUM') as medium_severity,
                COUNT(*) FILTER (WHERE severity = 'LOW') as low_severity,
                COUNT(DISTINCT rule_id) as active_rules,
                COUNT(DISTINCT ticket_id) as affected_tickets
            FROM dtic.quality_alerts
            WHERE resolved_at IS NULL
        """)
        result = db.execute(query).fetchone()
        
        return {
            'high': result[0] or 0,
            'medium': result[1] or 0,
            'low': result[2] or 0,
            'active_rules': result[3] or 0,
            'affected_tickets': result[4] or 0,
            'total_alerts': (result[0] or 0) + (result[1] or 0) + (result[2] or 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")
