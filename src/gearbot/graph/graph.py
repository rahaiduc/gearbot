from langgraph.graph import StateGraph, START, END
from core import agent_node, browser_node, AgentState

def create_web_graph():
    workflow = StateGraph(AgentState)
    
    # Añadir nodos
    workflow.add_node("agent", agent_node)
    workflow.add_node("browser", browser_node)
    
    # Edges
    workflow.add_edge(START, "agent")
    
    # Después del agente, decidimos si ir al navegador o terminar
    workflow.add_conditional_edges(
        "agent",
        lambda state: "browser" if "navega" in state.messages[-1].content.lower() 
                                 or "scrapea" in state.messages[-1].content.lower() 
                                 or "ve a" in state.messages[-1].content.lower() 
                                 else END
    )
    
    workflow.add_edge("browser", "agent")  # Volver al agente después de la acción
    
    return workflow.compile()