import pandas as pd
from pathlib import Path
import re

DATA_FILE = Path("data/appointments.xlsx")

def load_calendar() -> pd.DataFrame:
    """Load calendar data from Excel, or create an empty one if none exists."""
    if DATA_FILE.exists():
        return pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["id", "patient", "date", "time", "reason"])
        df.to_excel(DATA_FILE, index=False)
        return df

def save_calendar(df: pd.DataFrame):
    """Save calendar back to Excel."""
    df.to_excel(DATA_FILE, index=False)

# --- NEW: nice formatting ---
def format_appointments(df: pd.DataFrame) -> str:
    """Format appointments into a pretty text table."""
    if df.empty:
        return "📭 No appointments scheduled."

    lines = ["📅 Current Appointments:"]
    lines.append("-" * 60)
    lines.append(f"{'ID':<4} {'Patient':<15} {'Date':<12} {'Time':<8} {'Reason'}")
    lines.append("-" * 60)

    for _, row in df.iterrows():
        lines.append(f"{row['id']:<4} {row['patient']:<15} {row['date']:<12} {row['time']:<8} {row['reason']}")

    lines.append("-" * 60)
    return "\n".join(lines)

def list_appointments() -> str:
    """Return formatted list of all appointments."""
    df = load_calendar()
    return format_appointments(df)

def add_appointment(patient: str, date: str, time: str, reason: str) -> str:
    """Add a new appointment to the calendar."""
    df = load_calendar()
    new_id = len(df) + 1
    new_entry = {"id": new_id, "patient": patient, "date": date, "time": time, "reason": reason}
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    save_calendar(df)
    return f"✅ Appointment added for {patient} on {date} at {time} ({reason})."

def cancel_appointment(appointment_id: int = None, patient: str = None) -> str:
    """Cancel an appointment by ID or patient name, then show updated schedule."""
    df = load_calendar()

    if appointment_id is not None:
        if appointment_id not in df["id"].values:
            return f"❌ Appointment {appointment_id} not found."
        df = df[df["id"] != appointment_id]
        save_calendar(df)
        return f"🗑️ Appointment {appointment_id} cancelled.\n\n{format_appointments(df)}"

    if patient is not None:
        matches = df[df["patient"].str.contains(patient, case=False, na=False)]
        if matches.empty:
            return f"❌ No appointments found for {patient}."
        cancel_id = matches.iloc[0]["id"]
        df = df[df["id"] != cancel_id]
        save_calendar(df)
        return f"🗑️ Appointment for {patient} (ID {cancel_id}) cancelled.\n\n{format_appointments(df)}"

    return "❌ Please specify an appointment ID or patient name to cancel."



# --- Parsing helpers ---
def parse_add_command(user_text: str):
    """Parse user text for appointment details."""
    name_match = re.search(r"for\s+([A-Z][a-z]+)", user_text)
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", user_text)
    time_match = re.search(r"\d{1,2}:\d{2}", user_text)
    reason_match = re.search(r"for (.*)$", user_text)

    patient = name_match.group(1) if name_match else "Unknown"
    date = date_match.group(0) if date_match else "TBD"
    time = time_match.group(0) if time_match else "TBD"
    reason = reason_match.group(1) if reason_match else "General Checkup"

    return patient, date, time, reason

def parse_cancel_command(user_text: str):
    """Parse user text for cancel request (ID or patient name)."""
    id_match = re.search(r"(\d+)", user_text)
    name_match = re.search(r"cancel\s+([A-Z][a-z]+)", user_text, re.IGNORECASE)

    if id_match:
        return int(id_match.group(1)), None
    if name_match:
        return None, name_match.group(1)
    return None, None
