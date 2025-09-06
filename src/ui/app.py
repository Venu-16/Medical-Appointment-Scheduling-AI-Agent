import sys, os
sys.path.append(os.path.abspath("."))

import streamlit as st
from src.agents.workflow import workflow
from src.agents.state import AgentState
from src.agents.tools_registry import TOOLS
git
st.set_page_config(page_title="AI Medical Scheduler", page_icon="🩺", layout="centered")

st.title("🩺 AI Medical Appointment Scheduler")

# Session state for conversation memory
if "state" not in st.session_state:
    st.session_state.state = AgentState(
        user_input="",
        patient=None,
        appointment=None,
        insurance=None,
        reminders=None,
        messages=[]
    )

# Chat history
chat_container = st.container()
with chat_container:
    if st.session_state.state["messages"]:
        for msg in st.session_state.state["messages"]:
            st.chat_message("assistant").write(msg)

# Chat input
user_input = st.chat_input("Type your message here...")
if user_input:
    st.session_state.state["user_input"] = user_input
    result = workflow.invoke(st.session_state.state)
    st.session_state.state = result
    st.rerun()

# File uploader for intake form (new patients only)
if st.session_state.state.get("appointment") and not st.session_state.state["patient"].get("is_returning", True):
    st.subheader("📑 Upload Filled Intake Form")
    uploaded_file = st.file_uploader("Upload your filled intake form (PDF)", type=["pdf"])
    if uploaded_file is not None:
        # Save file to forms_returned
        appt_id = st.session_state.state["appointment"]["appointment_id"]
        file_path = f"data/forms_returned/{appt_id}_filled.pdf"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success("Form uploaded successfully! Extracting insurance details...")

        # Run insurance extraction
        result = TOOLS["insurance_extractor"].extract_from_pdf(file_path)
        if result["status"] == "ok":
            TOOLS["insurance_tool"].add_from_form(appt_id, result["insurance"])
            st.session_state.state["insurance"] = result["insurance"]
            st.session_state.state["messages"].append("✅ Insurance details extracted from intake form.")
        else:
            st.session_state.state["messages"].append("⚠️ Error extracting insurance info from form.")
        st.rerun()

# Show appointment summary if available
if st.session_state.state.get("appointment"):
    with st.expander("📅 Appointment Details"):
        st.json(st.session_state.state["appointment"])

if st.session_state.state.get("insurance"):
    with st.expander("💳 Insurance Details"):
        st.json(st.session_state.state["insurance"])

if st.session_state.state.get("reminders"):
    with st.expander("⏰ Reminders Scheduled"):
        st.json(st.session_state.state["reminders"])
