import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType

# Import all clinical toolsy
from src.tools.clinical_tools import (
    PatientLookupTool,
    PatientRegistrationTool,
    ScheduleLookupTool,
    BookSlotTool,
    CancelAppointmentTool,
    InsuranceCollectionTool,
    FormDistributionTool,
    ConfirmationTool,
    ExportReportTool,
    ReminderTool,
    EmailTool,
    SMSTool,
)

def build_gemini_agent():
    """Build a Gemini-powered scheduling agent with clinical tools."""

    # Load environment vars
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("❌ GOOGLE_API_KEY not set in .env")

    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # faster + cheaper than pro
        temperature=0
    )

    # Register tools
    tools = [
        PatientLookupTool,
        PatientRegistrationTool,
        ScheduleLookupTool,
        BookSlotTool,
        CancelAppointmentTool,
        InsuranceCollectionTool,
        FormDistributionTool,
        ConfirmationTool,
        ExportReportTool,
        ReminderTool,
        EmailTool,
        SMSTool,
    ]

    # Create ReAct-style agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    return agent
