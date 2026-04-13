from typing import Annotated, Sequence, Dict, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """Estado completo del agente web"""
    
    messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    
    # Información del navegador
    current_url: Optional[str] = None
    page_title: Optional[str] = None
    
    # Control de ejecución
    last_action: Optional[str] = None
    error: Optional[str] = None
    
    # Para acciones sensibles
    pending_confirmation: bool = False
    pending_action: Optional[Dict] = None