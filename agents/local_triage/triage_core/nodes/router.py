import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from agents.local_triage.triage_core.state import AgentState

ROUTER_PROMPT = """
You are the Triage Router. Classify the user demand into one of the following INTENTS:

- PRINTER_ISSUE: Paper jam, toner low, printing problems.
- EQUIPMENT_REQUEST: Mouse, keyboard, monitor, headset, laptop, dock. (Includes both broken incidents and new requisitions).
- VPN_ACCESS: VPN permission, remote access.
- CREATE_USER: New employee, account creation.
- GREETING: Hello, Hi, Bom dia.
- UNKNOWN: Pizza, weather, out of scope requests.

Output purely a valid JSON object: {"intent": "INTENT_NAME"}
"""

llm = ChatOllama(
    base_url="http://localhost:11434",
    model="llama3.1",
    temperature=0,
    format="json"
)

def router_node(state: AgentState):
    """Route the request."""
    # Always use the pinned request for routing to avoid context drift
    request_text = state["pinned_request"]
    
    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=request_text)
    ]
    
    response = llm.invoke(messages)
    
    try:
        content = json.loads(response.content)
        intent = content.get("intent", "UNKNOWN")
    except:
        intent = "UNKNOWN"
        
    return {"intent": intent}
