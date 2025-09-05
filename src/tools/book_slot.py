import os
import pandas as pd
from openpyxl import Workbook
from langchain.tools import tool

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
os.makedirs(DATA_DIR, exist_ok=True)

PATIENTS_FILE = os.path.join(DATA_DIR, "patients.csv")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.csv")
SCHEDULES_FILE = os.path.join(DATA_DIR, "doctor_schedules.xlsx")
FORMS_FILE = os.path.join(DATA_DIR, "forms_sent.csv")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.csv")

# ----------------------------
# 🔹 Patient Management
# ----------------------------
@tool
def PatientLookupTool(name: str, dob: str) -> dict:
    """Look up a patient by name and DOB. Returns dict or 'new patient'."""
    if not os.path.exists(PATIENTS_FILE):
        return "new patient"

    df = pd.read_csv(PATIENTS_FILE)
    match = df[(df["name"].str.lower() == name.lower()) & (df["dob"] == dob)]
    if not match.empty:
        return match.iloc[0].to_dict()
    return "new patient"


@tool
def PatientRegistrationTool(name: str, dob: str, phone: str, email: str, insurance: str, doctor_pref: str) -> str:
    """Register a new patient."""
    cols = ["id", "name", "dob", "phone", "email", "insurance", "doctor_pref"]
    if not os.path.exists(PATIENTS_FILE):
        pd.DataFrame(columns=cols).to_csv(PATIENTS_FILE, index=False)

    df = pd.read_csv(PATIENTS_FILE)
    new_id = 1 if df.empty else df["id"].max() + 1
    new_row = {"id": new_id, "name": name, "dob": dob, "phone": phone, "email": email, "insurance": insurance, "doctor_pref": doctor_pref}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(PATIENTS_FILE, index=False)
    return f"✅ Patient {name} registered with ID {new_id}"

# ----------------------------
# 🔹 Scheduling
# ----------------------------
@tool
def ScheduleLookupTool(doctor_id: int, date: str = None) -> str:
    """Look up free slots for a doctor, optionally filter by date."""
    if not os.path.exists(SCHEDULES_FILE):
        return "❌ No schedules found."
    df = pd.read_excel(SCHEDULES_FILE)
    df = df[(df["doctor_id"] == doctor_id) & (df["is_booked"] == False)]
    if date:
        df = df[df["date"] == date]
    if df.empty:
        return "❌ No free slots available."
    return df.to_string(index=False)


@tool
def BookSlotTool(slot_id: int, patient_id: int, patient_name: str) -> str:
    """Book a free slot for a patient."""
    if not os.path.exists(SCHEDULES_FILE):
        return "❌ No schedules available."
    schedules = pd.read_excel(SCHEDULES_FILE)
    if slot_id not in schedules["slot_id"].values:
        return f"❌ Slot {slot_id} not found."

    if schedules.loc[schedules["slot_id"] == slot_id, "is_booked"].values[0]:
        return f"❌ Slot {slot_id} already booked."

    schedules.loc[schedules["slot_id"] == slot_id, "is_booked"] = True
    schedules.to_excel(SCHEDULES_FILE, index=False)

    # Append to appointments
    appt_cols = ["appointment_id", "slot_id", "patient_id", "patient_name", "doctor_id", "date", "time"]
    if not os.path.exists(APPOINTMENTS_FILE):
        pd.DataFrame(columns=appt_cols).to_csv(APPOINTMENTS_FILE, index=False)
    appts = pd.read_csv(APPOINTMENTS_FILE)
    new_id = 1 if appts.empty else appts["appointment_id"].max() + 1
    slot = schedules[schedules["slot_id"] == slot_id].iloc[0]
    new_appt = {
        "appointment_id": new_id,
        "slot_id": slot_id,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "doctor_id": slot["doctor_id"],
        "date": slot["date"],
        "time": slot["time"]
    }
    appts = pd.concat([appts, pd.DataFrame([new_appt])], ignore_index=True)
    appts.to_csv(APPOINTMENTS_FILE, index=False)
    return f"✅ Appointment booked for {patient_name} with doctor {slot['doctor_id']} on {slot['date']} at {slot['time']}."


@tool
def CancelAppointmentTool(appointment_id: int) -> str:
    """Cancel an appointment and free the slot."""
    if not os.path.exists(APPOINTMENTS_FILE):
        return "❌ No appointments found."
    appts = pd.read_csv(APPOINTMENTS_FILE)
    if appointment_id not in appts["appointment_id"].values:
        return f"❌ Appointment {appointment_id} not found."

    appt = appts[appts["appointment_id"] == appointment_id].iloc[0]
    slot_id = appt["slot_id"]

    # Mark slot as free again
    if os.path.exists(SCHEDULES_FILE):
        schedules = pd.read_excel(SCHEDULES_FILE)
        schedules.loc[schedules["slot_id"] == slot_id, "is_booked"] = False
        schedules.to_excel(SCHEDULES_FILE, index=False)

    # Remove appointment
    appts = appts[appts["appointment_id"] != appointment_id]
    appts.to_csv(APPOINTMENTS_FILE, index=False)

    return f"🗑️ Appointment {appointment_id} cancelled, slot {slot_id} freed."

# ----------------------------
# 🔹 Insurance & Forms
# ----------------------------
@tool
def InsuranceCollectionTool(appointment_id: int, carrier: str, member_id: str, group_number: str) -> str:
    """Attach insurance info to an appointment record."""
    if not os.path.exists(APPOINTMENTS_FILE):
        return "❌ No appointments found."
    appts = pd.read_csv(APPOINTMENTS_FILE)
    if appointment_id not in appts["appointment_id"].values:
        return f"❌ Appointment {appointment_id} not found."

    appts.loc[appts["appointment_id"] == appointment_id, ["insurance_carrier", "member_id", "group_number"]] = [carrier, member_id, group_number]
    appts.to_csv(APPOINTMENTS_FILE, index=False)
    return f"✅ Insurance info added for appointment {appointment_id}"

@tool
def FormDistributionTool(email: str, appointment_id: int) -> str:
    """Send intake form (simulated)."""
    cols = ["appointment_id", "email"]
    if not os.path.exists(FORMS_FILE):
        pd.DataFrame(columns=cols).to_csv(FORMS_FILE, index=False)
    df = pd.read_csv(FORMS_FILE)
    df = pd.concat([df, pd.DataFrame([{"appointment_id": appointment_id, "email": email}])], ignore_index=True)
    df.to_csv(FORMS_FILE, index=False)
    return f"📩 Intake form sent to {email} for appointment {appointment_id}"

# ----------------------------
# 🔹 Confirmation & Reporting
# ----------------------------
@tool
def ConfirmationTool(appointment_id: int) -> str:
    """Generate confirmation message."""
    if not os.path.exists(APPOINTMENTS_FILE):
        return "❌ No appointments found."
    appts = pd.read_csv(APPOINTMENTS_FILE)
    appt = appts[appts["appointment_id"] == appointment_id]
    if appt.empty:
        return f"❌ Appointment {appointment_id} not found."
    row = appt.iloc[0]
    return f"✅ Confirmation: {row['patient_name']} with doctor {row['doctor_id']} on {row['date']} at {row['time']}."

@tool
def ExportReportTool() -> str:
    """Export all appointments into admin_report.xlsx"""
    if not os.path.exists(APPOINTMENTS_FILE):
        return "❌ No appointments found."
    df = pd.read_csv(APPOINTMENTS_FILE)
    out_path = os.path.join(DATA_DIR, "admin_report.xlsx")
    df.to_excel(out_path, index=False)
    return f"📊 Report exported to {out_path}"

# ----------------------------
# 🔹 Reminders & Communication
# ----------------------------
@tool
def ReminderTool(appointment_id: int, patient_email: str, patient_phone: str) -> str:
    """Schedule reminders for a patient."""
    cols = ["appointment_id", "when", "recipient"]
    if not os.path.exists(REMINDERS_FILE):
        pd.DataFrame(columns=cols).to_csv(REMINDERS_FILE, index=False)
    df = pd.read_csv(REMINDERS_FILE)

    reminders = [
        {"appointment_id": appointment_id, "when": "T-1d", "recipient": patient_email},
        {"appointment_id": appointment_id, "when": "T-6h", "recipient": patient_email},
        {"appointment_id": appointment_id, "when": "T-1h", "recipient": patient_phone},
    ]
    df = pd.concat([df, pd.DataFrame(reminders)], ignore_index=True)
    df.to_csv(REMINDERS_FILE, index=False)
    return f"⏰ 3 reminders scheduled for appointment {appointment_id}"

@tool
def EmailTool(recipient_email: str, subject: str, body: str) -> str:
    """Simulated email sender."""
    return f"📧 Email to {recipient_email}: {subject}\n{body}"

@tool
def SMSTool(recipient_phone: str, message: str) -> str:
    """Simulated SMS sender."""
    return f"📱 SMS to {recipient_phone}: {message}"
