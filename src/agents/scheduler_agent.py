from langgraph.graph import StateGraph, END
from typing import TypedDict
from tools import calendar_tools as ct

class SchedulerState(TypedDict):
    user_input: str
    response: str

def scheduling_node(state: SchedulerState) -> SchedulerState:
    """Smarter rule-based scheduling logic."""
    user_text = state["user_input"].lower()

    if "list" in user_text:
        # list_appointments() now returns a pretty string, not a DataFrame
        return {"user_input": user_text, "response": ct.list_appointments()}

    elif "add" in user_text or "book" in user_text:
        patient, date, time, reason = ct.parse_add_command(state["user_input"])
        return {
            "user_input": user_text,
            "response": ct.add_appointment(patient, date, time, reason)
        }

    elif "cancel" in user_text:
        appointment_id, patient = ct.parse_cancel_command(state["user_input"])
        return {
            "user_input": user_text,
            "response": ct.cancel_appointment(appointment_id, patient)
        }

    else:
        return {
            "user_input": user_text,
            "response": "I can help with: list, add/book, or cancel appointments."
        }

def build_scheduler_graph():
    graph = StateGraph(SchedulerState)
    graph.add_node("scheduling", scheduling_node)
    graph.set_entry_point("scheduling")
    graph.add_edge("scheduling", END)
    return graph
