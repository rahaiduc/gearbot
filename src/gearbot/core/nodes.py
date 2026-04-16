"""
    Core nodes for the GearBot agent, including the main agent node and a custom tools node that
    updates browser state.
"""
from langchain_xai import ChatXAI
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from gearbot.tools import tools
from gearbot.config import XAI_API_KEY, GROK_MODEL
from .state import AgentState
from .browser import browser_manager

llm = ChatXAI(model=GROK_MODEL, api_key=XAI_API_KEY, temperature=0)

SYSTEM_PROMPT = SystemMessage(
    content="""
    Eres Grok, un agente web experto y cuidadoso.
    Puedes navegar por internet, extraer información, hacer clic y rellenar formularios.
    Sé preciso con los selectores.
    Antes de realizar acciones importantes (como registrarte, comprar o enviar datos), pide confirmación
    explícita al usuario.
    """
)

async def agent_node(state: AgentState):
    """Agent node that processes messages and interacts with tools, while maintaining conversation 
    context.

    Args:
        state: The current state of the agent, including conversation history and any relevant data.

    Returns:
        A Command object containing the updated state and any messages to be sent back to the user.
    """
    llm_with_tools = llm.bind_tools(tools)
    messages = [SYSTEM_PROMPT] + list(state.messages)

    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

async def tools_node(state: AgentState):
    """Tools node that processes tool invocations and updates the agent's state based on the 
    results.
    
    Args:
        state: The current state of the agent, including conversation history and any relevant data.

    Returns:
        A Command object containing the updated state and any messages to be sent back to the user.
    """

    base_tool_node = ToolNode(tools)
    result = await base_tool_node.ainvoke(state)

    updates = {}
    tool_messages = [m for m in result.get("messages", []) if isinstance(m, ToolMessage)]

    if tool_messages:
        last_tool = tool_messages[-1]
        tool_name = last_tool.name

        try:
            if tool_name in ["navigate_to", "get_page_info"]:
                page_info = await browser_manager.get_current_page_info()
                updates = {
                    "current_url": page_info["url"],
                    "page_title": page_info["title"],
                    "last_action": tool_name,
                    "error": None
                }

            elif tool_name in ["click_element", "fill_field"]:
                updates = {
                    "last_action": tool_name,
                    "error": None
                }

        except Exception as e:
            updates["error"] = f"Error al actualizar estado: {str(e)}"

    return Command(
        update={
            **updates,
            "messages": result.get("messages", [])
        }
    )
