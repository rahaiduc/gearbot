from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .browser import browser_manager
from .state import AgentState

llm = ChatOpenAI(model="gpt-4o", temperature=0)

SYSTEM_PROMPT = SystemMessage(
    content="""Eres un agente web experto y cuidadoso.
Puedes navegar, scrapear, hacer clic y rellenar formularios.
Antes de realizar acciones destructivas o de registro/compra, pide confirmación al usuario.
Sé preciso con los selectores CSS o XPath cuando sea necesario.
Siempre describe qué vas a hacer antes de hacerlo."""
)

async def agent_node(state: AgentState) -> AgentState:
    """Nodo principal: el LLM decide qué hacer"""
    messages = [SYSTEM_PROMPT] + list(state.messages)
    
    response = await llm.ainvoke(messages)
    
    return {
        "messages": [response],
        "last_action": "thinking"
    }


async def browser_node(state: AgentState) -> AgentState:
    """Nodo que ejecuta acciones en el navegador"""
    last_message = state.messages[-1]
    
    # Aquí parseamos la intención del LLM (esto se puede mejorar mucho después)
    content = last_message.content.lower()
    
    try:
        if "ve a " in content or "navega a " in content or "goto " in content:
            url = content.split("a ")[-1].strip().split()[0]
            if not url.startswith("http"):
                url = "https://" + url
            result = await browser_manager.navigate(url)
            return {"current_url": result.get("url"), "page_title": result.get("title")}
        
        elif "scrapea" in content or "extrae" in content or "lee" in content:
            text = await browser_manager.page.inner_text("body")
            return {"messages": [HumanMessage(content=f"Contenido extraído: {text[:1000]}...")]}
        
        else:
            return {"error": "No entendí la acción solicitada"}
            
    except Exception as e:
        return {"error": str(e)}