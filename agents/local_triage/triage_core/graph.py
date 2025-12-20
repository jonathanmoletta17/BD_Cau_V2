from typing import Literal

from langgraph.graph import StateGraph, END
from agents.local_triage.triage_core.state import AgentState
from agents.local_triage.triage_core.nodes.router import router_node
from agents.local_triage.triage_core.nodes.extractor import extractor_node
from agents.local_triage.triage_core.nodes.validator import validator_node
from agents.local_triage.triage_core.nodes.inquiry import inquiry_node
from agents.local_triage.triage_core.nodes.result import result_node
from agents.local_triage.triage_core.classifier_wrapper_node import classify_node_engine

# --- Conditional Logic ---

def route_after_router(state: AgentState) -> Literal["extractor", "result"]:
    """Decides next step after Router."""
    if state.get("intent") in ["UNKNOWN", "GREETING"]:
        return "result"
    return "extractor"

def route_after_validator(state: AgentState) -> Literal["classifier", "inquiry"]:
    """Decides next step after Validator."""
    if state.get("is_complete"):
        return "classifier"
    return "inquiry"

def route_after_inquiry(state: AgentState) -> Literal["router", "result"]:
    """Decides next step after Inquiry."""
    # If we just asked a question, we actually end the turn and wait for user input.
    # In a real chat app, this would be END.
    # For simulation, we might loop back if we simulate user input, but here we pause.
    return "result"

# --- Graph Definition ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("router", router_node)
workflow.add_node("extractor", extractor_node)
workflow.add_node("validator", validator_node)
workflow.add_node("inquiry", inquiry_node)
workflow.add_node("classifier", classify_node_engine)
workflow.add_node("result", result_node) # Final State Node

# Set Entry Point
workflow.set_entry_point("router")

# Add Edges
workflow.add_conditional_edges(
    "router",
    route_after_router,
    {
        "extractor": "extractor",
        "result": "result"
    }
)

workflow.add_edge("extractor", "validator")

workflow.add_conditional_edges(
    "validator",
    route_after_validator,
    {
        "classifier": "classifier",
        "inquiry": "inquiry" # Inquiry is now a terminal step for this turn
    }
)

workflow.add_edge("classifier", "result")
workflow.add_edge("inquiry", "result") # Inquiry also leads to result (Wait for user)

workflow.add_edge("result", END)

# Compile
app = workflow.compile()
