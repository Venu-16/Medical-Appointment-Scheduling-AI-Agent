# src/agents/state.py
from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    user_input: str
    patient: Optional[dict]
    appointment: Optional[dict]
    insurance: Optional[dict]
    reminders: Optional[List[dict]]
    messages: List[str]
