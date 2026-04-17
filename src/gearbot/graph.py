"""Graph definition for GearBot, outlining the workflow of the agent and its interactions 
with tools."""
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from gearbot.core import agent_node, tools_node, AgentState

def create_web_graph():
    """Create the state graph for the GearBot agent, defining the workflow and interactions
    between the agent and its tools."""
    workflow = StateGraph(AgentState)
    # Short term memory checkpointer to maintain conversation context and state across interactions
    checkpointer = InMemorySaver()
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    workflow.add_edge(START, "agent")
    # Condición para decidir si se necesitan ejecutar herramientas
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END}
    )

    # Después de ejecutar tools, vuelve al agente
    workflow.add_edge("tools", "agent")

    return workflow.compile(checkpointer=checkpointer)
