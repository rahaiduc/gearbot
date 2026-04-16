"""
    Web interaction tools for the agent, allowing navigation, content extraction, 
    and interaction with web pages.
"""
from langchain_core.tools import tool
from gearbot.core.browser import browser_manager

@tool
async def navigate_to(url: str) -> str:
    """Navigate to a specified URL and return the page title.
    
    Args:
        url: The URL to navigate to.
    Returns:
        A string confirming the navigation and showing the page title.
    """
    result = await browser_manager.navigate(url)
    return f"Navegado a: {result['url']}\nTítulo: {result['title']}"


@tool
async def extract_page_content(selector: str = "body") -> str:
    """Extract text content from the page using a HTML selector.
    
    Args:
        selector: The HTML selector to extract text from.
    Returns:
        A string containing the extracted text.
    """
    text = await browser_manager.extract_text(selector)
    return text[:1500]  # Limitamos para no saturar el contexto


@tool
async def click_element(selector: str, description: str = "") -> str:
    """Click on an element specified by a selector.
    
    Args:
        selector: The HTML selector for the element to click.
        description: A description of the element being clicked.
    Returns:
        A string confirming the click action or reporting an error.
    """
    try:
        await browser_manager.click(selector)
        return f"Click realizado en: {selector} ({description})"
    except Exception as e:
        return f"Error al hacer click en {selector}: {str(e)}"


@tool
async def fill_field(selector: str, value: str, description: str = "") -> str:
    """Fill a form field specified by a selector with a given value.
    
    Args:
        selector: The HTML selector for the field to fill.
        value: The value to fill the field with.
        description: A description of the field being filled.
    Returns:
        A string confirming the fill action or reporting an error.
    """
    try:
        await browser_manager.fill(selector, value)
        return f"Campo {selector} rellenado con: {value} ({description})"
    except Exception as e:
        return f"Error al rellenar {selector}: {str(e)}"


@tool
async def get_page_info() -> str:
    """Get the current page information, including URL and title.
    
    Returns:
        A string containing the current URL and page title.
    """
    info = await browser_manager.get_current_page_info()
    return f"URL actual: {info['url']}\nTítulo: {info['title']}"


tools = [navigate_to, extract_page_content, click_element, fill_field, get_page_info]
