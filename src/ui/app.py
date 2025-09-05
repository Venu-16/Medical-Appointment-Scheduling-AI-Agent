# src/ui/app.py
"""
Streamlit UI for RagaAI - Medical Appointment Scheduling Agent
Requirements: streamlit, pandas, openpyxl
Run: streamlit run src/ui/app.py
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# --- Adjust this import to match your actual workflow location ---
# from src.agents.workflow import workflow  # <-- Uncomment if using package import
try:
    # support running from project root or src folder
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from src.agents.workflow import workflow
except Exception:
    try:
        # alternate fallback if running from root
        from src.agents.workflow import workflow
    except Exception:
        workflow = None  # Show friendly error if not found

# ------------------------
# Helpful constants / paths
# ------------------------
DATA_DIR = Path("data")
APPOINTMENTS_CSV = DATA_DIR / "appointments.csv"
REMINDERS_CSV = DATA_DIR / "reminders.csv"
PATIENTS_CSV = DATA_DIR / "patients.csv"
SCHEDULE_XLSX = DATA_DIR / "doctor_schedules.xlsx"

# ------------------------
# Page config and styles
# ------------------------
st.set_page_config(page_title="RagaAI Scheduler", page_icon="🩺", layout="wide")

# Minimal CSS for a nicer look
st.markdown(
    """
    <style>
    .chat-bubble {
        border-radius: 12px;
        padding: 12px 14px;
        margin: 6px 0;
        max-width: 78%;
        line-height: 1.4;
    }
    .user {
        background: linear-gradient(90deg,#60a5fa 0%, #3b82f6 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .agent {
        background: #f3f4f6;
        color: #111827;
        margin-right: auto;
    }
    .app-header {
        font-size: 24px;
        font-weight: 700;
    }
    .muted {
        color: #6b7280;
        font-size: 12px;
    }
    .pill {
        display:inline-block;
        padding:6px 10px;
        border-radius:999px;
        background:#eef2ff;
        color:#3730a3;
        font-weight:600;
        margin-right:6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------
# Helper utilities
# ------------------------
def load_table(path: Path):
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            # fallback for appointments xlsx in some setups
            try:
                return pd.read_excel(path)
            except Exception:
                return pd.DataFrame()
    return pd.DataFrame()

def append_message(role: str, text: str):
    """Store chat in session state"""
    if "chat" not in st.session_state:
        st.session_state.chat = []
    st.session_state.chat.append({"role": role, "text": text, "ts": datetime.now().isoformat()})

def render_chat():
    """Render chat messages in the main column"""
    for item in st.session_state.get("chat", []):
        cls = "user" if item["role"] == "user" else "agent"
        align = "right" if cls == "user" else "left"
        st.markdown(
            f'<div class="chat-bubble {cls}" style="text-align:{align}">{item["text"]}</div>',
            unsafe_allow_html=True,
        )

# ------------------------
# Layout: Sidebar
# ------------------------
with st.sidebar:
    st.markdown("<div class='app-header'>RagaAI Scheduler</div>", unsafe_allow_html=True)
    st.markdown("🩺 Demo interface for the internship case study")
    st.divider()

    st.markdown("**Quick actions**")
    if st.button("Load sample patients"):
        if PATIENTS_CSV.exists():
            df = pd.read_csv(PATIENTS_CSV)
            st.success(f"Loaded {len(df)} patients")
        else:
            st.warning("patients.csv not found in /data")

    if st.button("Show appointments (refresh)"):
        appt_df = load_table(APPOINTMENTS_CSV)
        st.write(appt_df.head(10))

    st.markdown("---")
    st.markdown("**Simulated comms (demo)**")
    email_preview = load_table(REMINDERS_CSV)
    st.markdown(f"- Scheduled reminders: {len(email_preview)}")
    if st.button("Clear simulated logs"):
        if REMINDERS_CSV.exists():
            os.remove(REMINDERS_CSV)
            st.success("Cleared reminders.csv")
        else:
            st.info("No reminders.csv found")

    st.markdown("---")
    st.markdown("**Export**")
    if st.button("Export admin report (xlsx)"):
        appt = load_table(APPOINTMENTS_CSV)
        if appt.empty:
            st.warning("No appointments to export")
        else:
            out = DATA_DIR / f"admin_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            appt.to_excel(out, index=False)
            st.success(f"Exported admin report: {out}")
            st.markdown(f"Saved to `{out}`")

    st.markdown("---")
    st.markdown("**Notes**")
    st.markdown(
        """
        - This is a demo. Email/SMS are simulated and written to `data/reminders.csv`.
        - To integrate real comms, wire SendGrid/Twilio in `src/tools`.
        """
    )

# ------------------------
# Main layout
# ------------------------
col1, col2 = st.columns((2.2, 1))

with col1:
    st.markdown("## Chat with Scheduling Agent")
    st.markdown('<div class="muted">Type like a patient: "My name is Rahul Mehta, DOB 1990-05-15, prefer Dr. Ananya Rao"</div>', unsafe_allow_html=True)
    st.write("")  # spacer

    # Render existing chat
    if "chat" not in st.session_state:
        st.session_state.chat = [
            {"role": "agent", "text": "Hello! I’m RagaAI — I can help you book medical appointments. Please share your name, DOB, and preferred doctor (or say 'help').", "ts": datetime.now().isoformat()}
        ]

    render_chat()

    # Input box
    with st.form("user_input_form", clear_on_submit=True):
        user_text = st.text_input("You:", placeholder="e.g. My name is Rahul Mehta. DOB 1990-05-15. I want Dr. Ananya Rao.")
        submitted = st.form_submit_button("Send")
        if submitted and user_text:
            append_message("user", user_text)
            # Call the LangGraph workflow if available
            if workflow is None:
                append_message("agent", "⚠️ Workflow not found. Make sure src/agents/workflow.py exists and exports `workflow`.")
            else:
                # Build starting state based on the user's message
                state = {"user_input": user_text, "messages": []}
                try:
                    result = workflow.invoke(state)
                except Exception as e:
                    # graceful fallback
                    append_message("agent", f"Error running workflow: {e}")
                else:
                    # Append all produced messages
                    for m in result.get("messages", []):
                        append_message("agent", m)
            st.rerun()

with col2:
    st.markdown("## Appointments Dashboard")
    appt_df = load_table(APPOINTMENTS_CSV)
    if appt_df.empty:
        st.info("No confirmed appointments yet. Book one through the chat.")
    else:
        st.dataframe(appt_df.sort_values(by="booked_at", ascending=False).reset_index(drop=True), height=420)

    st.write("---")
    st.markdown("## Quick booking (manual)")
    with st.form("manual_book"):
        patient_id = st.text_input("Patient ID (e.g. P001)")
        doctor_id = st.text_input("Doctor ID (e.g. D001)")
        date = st.date_input("Date")
        slot_time = st.text_input("Slot start (HH:MM)")
        reason = st.text_input("Reason", value="Consultation")
        booked = st.form_submit_button("Create manual appointment")
        if booked:
            # Very simple manual append to appointments
            if not patient_id:
                st.warning("Please provide patient_id")
            else:
                appt_id = f"A_{doctor_id}_{date.isoformat()}_{slot_time.replace(':','')}"
                row = {
                    "appointment_id": appt_id,
                    "slot_id": f"{doctor_id}_{date.isoformat()}_{slot_time.replace(':','')}",
                    "patient_id": patient_id,
                    "patient_name": patient_id,
                    "booked_at": datetime.now().isoformat(),
                    "reason": reason
                }
                df_row = pd.DataFrame([row])
                if APPOINTMENTS_CSV.exists():
                    df_row.to_csv(APPOINTMENTS_CSV, mode="a", header=False, index=False)
                else:
                    df_row.to_csv(APPOINTMENTS_CSV, index=False)
                st.success(f"Manually created appointment {appt_id}")
                st.experimental_rerun()

# ------------------------
# Footer / helpful debug info
# ------------------------
st.markdown("---")
st.markdown("#### Demo logs")
if st.checkbox("Show session debug"):
    st.json(st.session_state.get("chat", []))

st.markdown("##### Last updated")
st.markdown(f"<span class='muted'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>", unsafe_allow_html=True)
