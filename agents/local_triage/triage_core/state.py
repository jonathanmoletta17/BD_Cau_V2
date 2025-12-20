from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    pinned_request: str  # The original user request (Immutable)
    
    # Extraction State
    intent: Optional[str]
    data: Dict[str, Any]
    missing_fields: List[str]
    
    # Flow Control
    step: Optional[str]
    is_complete: bool
    
    # Output Contract
    output_payload: Optional[Dict[str, Any]]
