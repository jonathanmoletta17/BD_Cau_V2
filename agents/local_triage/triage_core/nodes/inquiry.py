from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from agents.local_triage.triage_core.state import AgentState

llm = ChatOllama(
    base_url="http://localhost:11434",
    model="llama3.1",
    temperature=0.2
)

def inquiry_node(state: AgentState):
    """Ask the user for missing information."""
    missing = state["missing_fields"]
    current_data = state["data"]
    
    prompt = f"""
    The user wants: {state['pinned_request']}
    We extracted: {current_data}
    We are missing these required fields: {missing}
    
    Politely ask the user for the missing information in Portuguese.
    Be concise.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "messages": [AIMessage(content=response.content)],
        "step": "inquiry"
    }
