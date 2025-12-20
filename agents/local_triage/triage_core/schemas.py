from typing import Literal, Optional, List
from pydantic import BaseModel, Field

class RequestType(BaseModel):
    request_type: Literal["incident", "requisition"]

class PrinterIssue(BaseModel):
    issue_type: Literal["paper_jam", "toner_low", "connection", "other"]
    serial_number: Optional[str] = Field(description="Serial number if available")

class EquipmentRequest(BaseModel):
    equipment_type: Literal["mouse", "keyboard", "monitor", "headset", "laptop", "docking_station"]
    request_type: Literal["incident", "requisition"] = Field(description="'incident' for broken items, 'requisition' for new/additional items")
    justification: Optional[str] = Field(description="Required for 'requisition'")

class VPNAccessRequest(BaseModel):
    justification: str = Field(description="Mandatory business justification for VPN access")
    manager_approval: Optional[bool] = Field(description="Whether manager has approved (if mentioned)")

class CreateUserRequest(BaseModel):
    full_name: str
    department: str
    user_type: Literal["efetivo", "terceiro", "estagiario"]
    cpf: Optional[str] = Field(description="Required for 'efetivo' or 'estagiario'")
    matricula: Optional[str] = Field(description="Required for 'efetivo'")
    empresa: Optional[str] = Field(description="Required for 'terceiro'")
