from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from gearbot.core import agent_node, tools_node
from gearbot.core import AgentState

def create_web_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    
    workflow.add_edge(START, "agent")
    
    # Routing inteligente: si hay tool calls → ejecuta tools, si no → termina
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END}
    )
    
    # Después de ejecutar tools, vuelve al agente
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()