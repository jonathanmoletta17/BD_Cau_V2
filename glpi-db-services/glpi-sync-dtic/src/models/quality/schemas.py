"""
Pydantic models for Quality Monitoring API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AlertSummary(BaseModel):
    """Summary of a quality alert for list views."""
    id: int
    alert_uuid: UUID
    rule_id: str
    severity: str
    ticket_id: Optional[int]
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    
    # Enriched fields from view
    glpi_id: Optional[int] = None
    titulo: Optional[str] = None
    status_id: Optional[int] = None
    tecnico: Optional[str] = None
    grupo: Optional[str] = None
    notification_count: int = 0
    
    class Config:
        from_attributes = True


class AlertDetail(BaseModel):
    """Detailed alert information including metadata."""
    id: int
    alert_uuid: UUID
    rule_id: str
    severity: str
    ticket_id: Optional[int]
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    metadata: Dict[str, Any]
    
    # Include rule name and description from metadata
    @property
    def rule_name(self) -> str:
        return self.metadata.get('rule_name', self.rule_id)
    
    @property
    def description(self) -> str:
        return self.metadata.get('description', '')
    
    @property
    def total_violations(self) -> int:
        return self.metadata.get('total_violations', 0)
    
    class Config:
        from_attributes = True


class QualitySummaryItem(BaseModel):
    """Aggregated summary by rule."""
    rule_id: str
    severity: str
    total_alerts: int
    affected_tickets: int
    last_detected: datetime
    
    class Config:
        from_attributes = True


class RunChecksResponse(BaseModel):
    """Response from manual quality check execution."""
    executed_at: str
    rules_executed: int
    alerts_created: int
    violations_found: Dict[str, int]
    errors: List[str]


class ResolveAlertRequest(BaseModel):
    """Request to resolve an alert."""
    user_id: Optional[int] = Field(None, description="ID do usuário que resolveu")
    notes: Optional[str] = Field(None, description="Notas sobre a resolução")
