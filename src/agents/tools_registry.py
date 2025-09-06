from src.tools.patient_lookup import PatientLookupTool
from src.tools.schedule_tool import ScheduleLookupTool
from src.tools.book_slot import BookSlotTool
from src.tools.insurance_tool import InsuranceCollectionTool
from src.tools.confirmation_tool import ConfirmationTool
from src.tools.reminder_tool import ReminderTool
from src.tools.form_distribution import FormDistributionTool
from src.tools.insurance_extractor import InsuranceExtractor

# Instantiate tools
patient_lookup = PatientLookupTool()
schedule_lookup = ScheduleLookupTool()
book_slot = BookSlotTool()
insurance_tool = InsuranceCollectionTool()
confirmation_tool = ConfirmationTool()
reminder_tool = ReminderTool()
form_tool = FormDistributionTool()
insurance_extractor = InsuranceExtractor()

# Export all tools
TOOLS = {
    "patient_lookup": patient_lookup,
    "schedule_lookup": schedule_lookup,
    "book_slot": book_slot,
    "insurance_tool": insurance_tool,
    "confirmation_tool": confirmation_tool,
    "reminder_tool": reminder_tool,
    "form_tool": form_tool,
    "insurance_extractor": insurance_extractor
}
