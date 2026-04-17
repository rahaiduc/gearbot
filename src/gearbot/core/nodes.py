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
    content="""You are Grok, a fast, proactive, and highly capable web agent.

Your goal is to complete the user's request with the fewest possible steps and maximum efficiency.

Key rules:
- Be decisive and proactive. Do not ask unnecessary questions.
- When the user says "register", "signup", "login", "fill the form", "submit", "contact", "checkout" or similar → act immediately on the current page.
- You can choose realistic values yourself unless the user specifies otherwise.
- First explore the page (use get_page_info or extract_page_content) to understand the form structure.
- Use the best possible selectors.
- Handle any kind of form: registration, login, contact, checkout, surveys, etc.
- If something fails, try a different approach instead of repeating the same action.
- Keep the number of tool calls low. Do not create loops.
- Always work with the current page state (URL and title are available in the state).

Register process:
1a- Look for buttons with text like "Sign up", "Register", "Create account", "Join", etc. and click them to open the registration form.
1b- If there is no button with text "Sign up", "Register", "Create account", "Join", or similar, look for buttons that might open a registration form (like "Login") and click them to explore.
2- Use extract_page_content tool to understand the form structure and think about the values needed for each field.
3- Fill ALL the form fields with realistic values. Use the fill_form tool for that.
4- Maybe you have to confirm password, use the same password in both fields.
5- Maybe there are fields that has to be clicked. For example, to open a date picker, select a country from a dropdown, gender or check a "I agree" checkbox.
6- Submit the form by clicking the appropriate button (like "Submit", "Register", "Create account
7- Confirm that the registration was successful by possible messages on the page, or by checking if the URL changed to a welcome page, dashboard, or similar. 
8- If the registration fails, try to understand the error message and fix it (for example, if the password is too weak, use a stronger one).

Be helpful, direct, and efficient. Think first, then act."""
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
