import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from agents.local_triage.triage_core.state import AgentState
from agents.local_triage.triage_core.schemas import PrinterIssue, EquipmentRequest, VPNAccessRequest, CreateUserRequest

llm = ChatOllama(
    base_url="http://localhost:11434",
    model="llama3.1",
    temperature=0,
    format="json"
)

def get_schema_for_intent(intent: str):
    if intent == "PRINTER_ISSUE": return PrinterIssue.model_json_schema()
    if intent == "EQUIPMENT_REQUEST": return EquipmentRequest.model_json_schema()
    if intent == "VPN_ACCESS": return VPNAccessRequest.model_json_schema()
    if intent == "CREATE_USER": return CreateUserRequest.model_json_schema()
    return None

def extractor_node(state: AgentState):
    intent = state.get("intent")
    request_text = state["pinned_request"]
    schema = get_schema_for_intent(intent)
    
    if not schema:
        return {"data": {}}
        
    prompt = f"""
    Extract the following fields from the user request based on this JSON schema:
    {json.dumps(schema)}
    
    Request: "{request_text}"
    
    Return purely a JSON object with the extracted fields. If a field is missing, omit it or use null.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        data = json.loads(response.content)
    except:
        data = {}
        
    return {"data": data}
