from langchain_xai import ChatXAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.types import Command
from .state import AgentState
from gearbot.tools import tools
from .browser import browser_manager
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

# ==================== NODO DEL AGENTE ====================
async def agent_node(state: AgentState):
    llm_with_tools = llm.bind_tools(tools)
    messages = [SYSTEM_PROMPT] + list(state.messages)
    
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


# ==================== NODO DE TOOLS PERSONALIZADO ====================
async def tools_node(state: AgentState):
    """ToolNode personalizado que actualiza el estado del navegador"""
    
    # 1. Ejecutar las tools normalmente
    base_tool_node = ToolNode(tools)
    result = await base_tool_node.ainvoke(state)

    # 2. Actualizar el estado según qué tool se ejecutó
    updates = {}
    tool_messages = [m for m in result.get("messages", []) if isinstance(m, ToolMessage)]

    if tool_messages:
        last_tool = tool_messages[-1]
        tool_name = last_tool.name

        try:
            if tool_name == "navigate_to":
                # Obtener información real y actualizada del navegador
                page_info = await browser_manager.get_current_page_info()
                updates = {
                    "current_url": page_info["url"],
                    "page_title": page_info["title"],
                    "last_action": "navigate",
                    "error": None
                }

            elif tool_name in ["click_element", "fill_field"]:
                updates = {
                    "last_action": tool_name,
                    "error": None
                }

            elif tool_name == "get_page_info":
                page_info = await browser_manager.get_current_page_info()
                updates = {
                    "current_url": page_info["url"],
                    "page_title": page_info["title"],
                    "last_action": "get_page_info",
                    "error": None
                }

            # Puedes añadir más tools aquí en el futuro (extract_page_content, etc.)

        except Exception as e:
            updates["error"] = f"Error al actualizar estado: {str(e)}"

    # 3. Devolver Command (forma recomendada en LangGraph)
    return Command(
        update={
            **updates,
            "messages": result.get("messages", [])
        }
    )