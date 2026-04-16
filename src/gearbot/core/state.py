"""State management for the agent, including messages and browser information."""
from typing import Annotated, Sequence, Dict, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """State of the agent, including messages and browser information.
    
    Attributes:
        messages: List of messages exchanged with the agent.
        current_url: Current URL in the browser.
        page_title: Title of the current page.
        last_action: Last action taken by the agent.
        error: Any error encountered during execution.
        pending_confirmation: Whether there is a pending confirmation for a sensitive action.
        pending_action: Details of the pending action, if any.
    """

    messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    current_url: Optional[str] = None
    page_title: Optional[str] = None
    last_action: Optional[str] = None
    error: Optional[str] = None
    pending_confirmation: bool = False
    pending_action: Optional[Dict] = None
