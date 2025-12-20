from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from enum import Enum

class IntentType(str, Enum):
    ACCESS = "access"
    USER_CREATION = "user_creation"
    HARDWARE = "hardware"
    OTHER = "other"
    UNKNOWN = "unknown"

class TriageStep(str, Enum):
    IDENTIFICATION = "identification"
    COLLECTION = "collection"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"

class SlotDefinition(BaseModel):
    name: str
    description: str
    required: bool = True
    value: Optional[str] = None
    question: str  # The deterministic question to ask if missing

class SessionState(BaseModel):
    """
    Represents the deterministic state of a user triage session.
    """
    intent: IntentType = IntentType.UNKNOWN
    step: TriageStep = TriageStep.IDENTIFICATION
    
    # Dynamic slots based on intent (e.g., {'system': SlotDef(...), 'action': SlotDef(...)})
    slots: Dict[str, SlotDefinition] = Field(default_factory=dict)
    
    # Raw history could be kept for context, but state depends on 'slots'
    missing_fields: List[str] = Field(default_factory=list)

    def update_slot(self, name: str, value: str):
        if name in self.slots:
            self.slots[name].value = value
            if name in self.missing_fields:
                self.missing_fields.remove(name)

    def get_next_missing_slot(self) -> Optional[SlotDefinition]:
        """Returns the first required slot that has no value."""
        for slot_name in self.missing_fields:
            if slot_name in self.slots:
                return self.slots[slot_name]
        return None

    def is_complete(self) -> bool:
        return len(self.missing_fields) == 0
