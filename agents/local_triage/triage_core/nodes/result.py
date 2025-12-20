from agents.local_triage.triage_core.state import AgentState

def result_node(state: AgentState):
    """
    Final node in the core layer. 
    Prepares the output payload or finalize state.
    """
    return {
        "output_payload": {
            "intent": state.get("intent"),
            "data": state.get("data"),
            "complete": state.get("is_complete"),
            "messages": [m.content for m in state.get("messages", []) if hasattr(m, "content")]
        }
    }
