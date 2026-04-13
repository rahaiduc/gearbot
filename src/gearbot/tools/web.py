from langchain_xai import ChatXAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from core import browser_manager

# ==================== HERRAMIENTAS DEL NAVEGADOR ====================

@tool
async def navigate_to(url: str) -> str:
    """Navega a una URL específica"""
    result = await browser_manager.navigate(url)
    return f"Navegado a: {result['url']}\nTítulo: {result['title']}"


@tool
async def extract_page_content(selector: str = "body") -> str:
    """Extrae el texto visible de la página o de un selector específico"""
    text = await browser_manager.extract_text(selector)
    return text[:1500]  # Limitamos para no saturar el contexto


@tool
async def click_element(selector: str, description: str = "") -> str:
    """Hace clic en un elemento de la página"""
    try:
        await browser_manager.click(selector)
        return f"Click realizado en: {selector} ({description})"
    except Exception as e:
        return f"Error al hacer click en {selector}: {str(e)}"


@tool
async def fill_field(selector: str, value: str, description: str = "") -> str:
    """Rellena un campo de formulario"""
    try:
        await browser_manager.fill(selector, value)
        return f"Campo {selector} rellenado con: {value} ({description})"
    except Exception as e:
        return f"Error al rellenar {selector}: {str(e)}"


@tool
async def get_page_info() -> str:
    """Devuelve información actual de la página (URL y título)"""
    info = await browser_manager.get_current_page_info()
    return f"URL actual: {info['url']}\nTítulo: {info['title']}"


tools = [navigate_to, extract_page_content, click_element, fill_field, get_page_info]