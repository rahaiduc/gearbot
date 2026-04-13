from langchain_xai import ChatXAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from state import AgentState
from tools.web import tools
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración del modelo desde .env
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4")

llm = ChatXAI(model=GROK_MODEL, temperature=0)

SYSTEM_PROMPT = SystemMessage(
    content="""Eres Grok, un agente web experto y cuidadoso.
Puedes navegar por internet, extraer información, hacer clic y rellenar formularios.
Sé preciso con los selectores.
Antes de realizar acciones importantes (como registrarte, comprar o enviar datos), pide confirmación explícita al usuario."""
)

# Nodo del agente (LLM con tools)
async def agent_node(state: AgentState):
    llm_with_tools = llm.bind_tools(tools)
    messages = [SYSTEM_PROMPT] + list(state.messages)
    
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


# Nodo de herramientas (usamos el ToolNode prebuilt de LangGraph)
tools_node = ToolNode(tools)