from langchain_xai import ChatXAI
from langchain_core.messages import SystemMessage
from state import AgentState
from tools.web import tools
llm = ChatXAI(model="grok-4", temperature=0)

SYSTEM_PROMPT = SystemMessage(
    content="""Eres un agente web experto llamado Grok.
Tu objetivo es ayudar al usuario a navegar, scrapear información y realizar acciones en páginas web.
Usa las herramientas disponibles de forma precisa.
Antes de realizar acciones importantes (click en botones de compra, registro, envío de formularios), pide confirmación al usuario.
Sé claro y describe qué vas a hacer."""
)

async def agent_node(state: AgentState):
    """Nodo que llama al LLM con tool calling"""
    messages = [SYSTEM_PROMPT] + list(state.messages)
    
    # Bind tools al LLM
    llm_with_tools = llm.bind_tools(tools)
    
    response = await llm_with_tools.ainvoke(messages)
    
    return {"messages": [response]}


async def tools_node(state: AgentState):
    """Nodo que ejecuta las herramientas del navegador"""
    # LangGraph tiene ToolNode, pero como usamos async, lo hacemos manual por ahora
    last_message = state.messages[-1]
    
    if not last_message.tool_calls:
        return {}
    
    tool_results = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        args = tool_call["args"]
        
        # Ejecutar la herramienta correspondiente
        for tool in tools:
            if tool.name == tool_name:
                result = await tool.ainvoke(args)
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_name,
                    "content": result
                })
                break
    
    return {"messages": tool_results}