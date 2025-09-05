# src/agents/workflow.py
from langgraph.graph import StateGraph, START, END
from src.agents.state import AgentState
from src.agents.tools_registry import TOOLS
from langchain.chat_models import init_chat_model
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

def extract_name_dob(user_input: str):
    """
    Very simple regex-based extractor for name and DOB.
    Expected DOB format: YYYY-MM-DD or DD/MM/YYYY
    """
    name = None
    dob = None

    # Try to find DOB
    dob_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", user_input)
    if not dob_match:
        dob_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", user_input)

    if dob_match:
        dob_str = dob_match.group(1)
        try:
            if "-" in dob_str:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            else:
                dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
        except Exception:
            dob = None

    # Naive way: assume the first capitalized words before "DOB" or standalone
    name_match = re.search(r"(?:My name is|I am)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)", user_input)
    if name_match:
        name = name_match.group(1)

    return name, dob


# Node: Greeting
def greeting_node(state: AgentState):
    msg = "Hello! Please provide your name, date of birth, and preferred doctor."
    state["messages"].append(msg)
    return state


# Node: Patient Lookup
def patient_lookup_node(state: AgentState):
    name, dob = extract_name_dob(state["user_input"])
    result = TOOLS[0].run({"name": name, "dob": dob})
    if result["status"] == "found":
        state["patient"] = result["patient"]
        msg = f"Welcome back {result['patient']['full_name']}! Let's continue."
    else:
        # Create a new patient entry with placeholders
        state["patient"] = {
            "full_name": name or "Unknown",
            "dob": str(dob) if dob else None,
            "preferred_doctor_id": None,
            "patient_id": None,
            "email": None,
            "phone": None,
        }
        msg = "You seem to be a new patient. We'll register you."
    state["messages"].append(msg)
    return state


# Node: Scheduling
def scheduling_node(state: AgentState):
    patient = state.get("patient", {})
    doctor_id = patient.get("preferred_doctor_id")

    if not doctor_id:
        state["messages"].append(
            "Please provide your preferred doctor ID before scheduling."
        )
        return state

    slots = TOOLS[1].run({"doctor_id": doctor_id})
    if slots:
        slot = slots[0]  # Pick first available
        appt = TOOLS[2].run({
            "slot_id": slot["slot_id"],
            "patient_id": patient.get("patient_id"),
            "patient_name": patient.get("full_name")
        })
        state["appointment"] = appt["appointment"]
        msg = f"Booked appointment for {patient.get('full_name')} at {slot['slot_start']}."
    else:
        msg = "No slots available. Please try another day."
    state["messages"].append(msg)
    return state


# Node: Insurance
def insurance_node(state: AgentState):
    if not state.get("appointment"):
        return state
    appt_id = state["appointment"]["appointment_id"]
    insurance = {"carrier": "HealthPrime", "member_id": "AB12345", "group_number": "7890"}
    result = TOOLS[3].run({"appointment_id": appt_id, **insurance})
    state["insurance"] = insurance
    state["messages"].append("Insurance details recorded.")
    return state


# Node: Confirmation
def confirmation_node(state: AgentState):
    if not state.get("appointment"):
        state["messages"].append("No appointment to confirm.")
        return state
    appt_id = state["appointment"]["appointment_id"]
    result = TOOLS[4].run({"appointment_id": appt_id})
    state["messages"].append(result["message"])
    return state


# Node: Reminders
def reminder_node(state: AgentState):
    if not state.get("appointment"):
        state["messages"].append("No appointment found. Skipping reminders.")
        return state
    appt_id = state["appointment"]["appointment_id"]
    reminders = TOOLS[5].run({
        "appointment_id": appt_id,
        "patient_email": state["patient"].get("email"),
        "patient_phone": state["patient"].get("phone")
    })
    state["reminders"] = reminders
    state["messages"].append("Reminders scheduled.")
    return state


# Build Graph
graph = StateGraph(AgentState)
graph.add_node("greeting", greeting_node)
graph.add_node("lookup", patient_lookup_node)
graph.add_node("scheduling", scheduling_node)
graph.add_node("insurance", insurance_node)
graph.add_node("confirmation", confirmation_node)
graph.add_node("reminder", reminder_node)

graph.add_edge(START, "greeting")
graph.add_edge("greeting", "lookup")
graph.add_edge("lookup", "scheduling")
graph.add_edge("scheduling", "insurance")
graph.add_edge("insurance", "confirmation")
graph.add_edge("confirmation", "reminder")
graph.add_edge("reminder", END)

workflow = graph.compile()
