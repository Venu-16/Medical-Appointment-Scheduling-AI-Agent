from langchain.tools import tool
from tools import calendar_tools as ct

@tool
def list_appointments_tool() -> str:
    """List all scheduled appointments."""
    return ct.list_appointments()

@tool
def add_appointment_tool(patient: str, date: str, time: str, reason: str) -> str:
    """Add a new appointment."""
    return ct.add_appointment(patient, date, time, reason)

@tool
def cancel_appointment_tool(appointment_id: int = None, patient: str = None) -> str:
    """Cancel an appointment by ID or patient name."""
    return ct.cancel_appointment(appointment_id, patient)
