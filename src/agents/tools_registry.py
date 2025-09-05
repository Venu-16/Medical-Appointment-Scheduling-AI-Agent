# src/agents/tools_registry.py
from langchain.tools import StructuredTool
from src.tools.patient_lookup import PatientLookupTool
from src.tools.schedule_tool import ScheduleLookupTool
from src.tools.book_slot import BookSlotTool
from src.tools.insurance_tool import InsuranceCollectionTool
from src.tools.confirmation_tool import ConfirmationTool
from src.tools.reminder_tool import ReminderTool

# Initialize raw tool classes
patient_lookup = PatientLookupTool()
schedule_lookup = ScheduleLookupTool()
book_slot = BookSlotTool()
insurance_tool = InsuranceCollectionTool()
confirmation_tool = ConfirmationTool()
reminder_tool = ReminderTool()

# Wrap them into LangChain Tools
TOOLS = [
    StructuredTool.from_function(
        func=patient_lookup.lookup,
        name="patient_lookup",
        description="Look up patient by name and DOB"
    ),
    StructuredTool.from_function(
        func=schedule_lookup.get_slots,
        name="schedule_lookup",
        description="Get available slots for a doctor on a date"
    ),
    StructuredTool.from_function(
        func=book_slot.book,
        name="book_slot",
        description="Book a slot for a patient"
    ),
    StructuredTool.from_function(
        func=insurance_tool.add_insurance,
        name="insurance_tool",
        description="Add insurance details to an appointment"
    ),
    StructuredTool.from_function(
        func=confirmation_tool.confirm,
        name="confirmation_tool",
        description="Confirm an appointment and return message"
    ),
    StructuredTool.from_function(
        func=reminder_tool.create_reminders,
        name="reminder_tool",
        description="Schedule reminders for appointment via email/SMS"
    ),
]
