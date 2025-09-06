from langgraph.graph import StateGraph, START, END
from src.agents.state import AgentState
from src.agents.tools_registry import TOOLS

# 1. Greeting
def greeting_node(state: AgentState):
    msg = "Hello! Please provide your name, date of birth, and preferred doctor."
    state["messages"].append(msg)
    return state

# 2. Patient Lookup
def patient_lookup_node(state: AgentState):
    # ⚡ Demo: naive extraction (hardcoded example)
    if "Rahul" in state["user_input"]:
        name, dob = "Rahul Mehta", "1990-05-15"
    else:
        name, dob = "New Patient", None

    result = TOOLS["patient_lookup"].lookup(name, dob)
    if result["status"] == "found":
        state["patient"] = result["patient"]
        state["patient"]["is_returning"] = True
        msg = f"Welcome back {result['patient']['full_name']}!"
    else:
        state["patient"] = {
            "full_name": name,
            "dob": dob,
            "email": "demo@example.com",
            "phone": "9999999999",
            "is_returning": False
        }
        msg = "You are a new patient. Let's continue with booking."
    state["messages"].append(msg)
    return state

# 3. Scheduling
def scheduling_node(state: AgentState):
    doctor_id = state["patient"].get("preferred_doctor_id", "D001")
    slots = TOOLS["schedule_lookup"].get_slots(doctor_id)
    if slots:
        slot = slots[0]  # pick first available
        appt = TOOLS["book_slot"].book(
            slot["slot_id"],
            state["patient"].get("patient_id", "NEW001"),
            state["patient"]["full_name"]
        )
        state["appointment"] = appt["appointment"]

        if not state["patient"].get("is_returning", True):
            TOOLS["form_tool"].send_form(
                state["patient"]["email"],
                appt["appointment"]["appointment_id"]
            )
            msg = f"Appointment booked. Intake form sent to {state['patient']['email']}."
        else:
            msg = f"Appointment booked for {state['patient']['full_name']} at {slot['slot_start']}."
    else:
        msg = "No slots available."
    state["messages"].append(msg)
    return state

# 4. Insurance (only for new patients)
def insurance_node(state: AgentState):
    if state["patient"].get("is_returning", True):
        return state

    appt_id = state["appointment"]["appointment_id"]
    form_path = f"data/forms_returned/{appt_id}_filled.pdf"
    result = TOOLS["insurance_extractor"].extract_from_pdf(form_path)

    if result["status"] == "ok":
        TOOLS["insurance_tool"].add_from_form(appt_id, result["insurance"])
        state["insurance"] = result["insurance"]
        state["messages"].append("Insurance details extracted from intake form.")
    else:
        state["messages"].append("Error extracting insurance info from form.")
    return state

# 5. Confirmation
def confirmation_node(state: AgentState):
    appt_id = state["appointment"]["appointment_id"]
    result = TOOLS["confirmation_tool"].confirm(appt_id)
    state["messages"].append(result["message"])
    return state

# 6. Reminders
def reminder_node(state: AgentState):
    appt_id = state["appointment"]["appointment_id"]
    reminders = TOOLS["reminder_tool"].create_reminders(
        appt_id,
        state["patient"]["email"],
        state["patient"]["phone"]
    )
    state["reminders"] = reminders
    state["messages"].append("Reminders scheduled.")
    return state

# Build workflow graph
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
