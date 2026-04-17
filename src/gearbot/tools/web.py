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
    For forms, it's useful to first extract content to understand the structure before interacting.
    Useful to understand the structure of forms before interacting with them.
    Args:
        selector: The HTML selector to extract text from.
    Returns:
        A string containing the extracted text.
    """
    text = await browser_manager.extract_text(selector)
    return text[:1500]  # Limitamos para no saturar el contexto


@tool
async def click_element(selector: str, description: str = "") -> str:
    """Click any element on the page (buttons, links, checkboxes, etc.).
    Some form fields maybe are required to be clicked.
    
    Preferred selectors:
    - text=Sign up, text=Login, text=Submit, text=Create account
    - id=, name=, placeholder=, aria-label
    
    Use this to open modals, click buttons, links, or checkboxes. 

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
    """Fill any input field, textarea, or dropdown in a form.
    Some fields may require clicking, use click_element for those cases.
    
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
async def fill_form(fields: dict, description: str = "") -> str:
    """Fill an entire form using a dictionary of field selectors and values.
    
    This is the recommended tool for filling forms (registration, login, 
    checkout, contact forms, etc.).
    
    Args:
        fields: A dictionary where keys are selectors and values are the data to fill.
                Example: {
                    "text=Username": "grokuser456",
                    "#email": "grok@example.com",
                    "input[name='password']": "SecurePass123!",
                    "[placeholder='Full name']": "Grok Agent"
                }
        description: Optional description of the form being filled.
    
    Returns:
        A summary of which fields were filled successfully.
    """
    results = []
    for selector, value in fields.items():
        try:
            await browser_manager.fill(selector, str(value))
            results.append(f"✅ '{selector}' → {value}")
        except Exception as e:
            results.append(f"❌ Failed '{selector}': {str(e)}")
    
    success_count = len([r for r in results if r.startswith("✅")])
    return f"Filled {success_count}/{len(fields)} fields in form.\n" + "\n".join(results)

@tool
async def get_page_info() -> str:
    """Get current page information (URL and title).
    
    Use this when you need to confirm where you are before taking action.
    
    Returns:
        A string containing the current URL and page title.
    """
    info = await browser_manager.get_current_page_info()
    return f"URL actual: {info['url']}\nTítulo: {info['title']}"


tools = [navigate_to, extract_page_content, click_element, fill_field, fill_form, get_page_info]
