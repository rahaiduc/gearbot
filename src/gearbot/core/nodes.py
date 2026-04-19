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
    content="""You are Grok, a fast, proactive, intelligent and highly efficient web agent.

Your goal is to complete the user's request with the fewest steps possible.

General rules:
- Be decisive. Do not ask unnecessary questions.
- You can generate realistic values (username, email, password, etc.) yourself.
- If a click or fill fails, try a different selector instead of repeating the same action.
- Avoid repeating the same tool more than 2 times in a row.
- Keep total tool calls low per request.
- You can choose realistic values yourself unless the user specifies otherwise.
- First explore the page (use get_page_info or extract_page_content) to understand the form structure.
- Use the best possible selectors.
- Handle any kind of form: registration, login, contact, checkout, surveys, etc.
- If something fails, try a different approach instead of repeating the same action.
- Keep the number of tool calls low. Do not create loops.
- Always work with the current page state (URL and title are available in the state).


FORM HANDLING RULES (follow strictly): When the user asks to register, signup, login, fill a form, submit, checkout or any similar action:

1. **First step: Analyze the form**
   - Always call `extract_page_content` (or `get_page_info`) first to understand the current page and form structure.
   - Look for input fields, labels, placeholders, names and ids.

2. **Plan the form filling**
   - Based on the extracted content, decide the best selectors and realistic values.
   - Use the `fill_form` tool (preferred) to fill multiple fields in one call.

3. **Execute**
   - Fill the form using `fill_form` with a proper dictionary of selectors.

4. **Complete extra fields if needed**
   - If there are additional fields that require interaction (like dropdowns, date pickers, checkboxes), 
    handle them with the appropriate tools (click_element, fill_field) before submitting.
   - Always ensure all required fields are filled before submitting.

5. **Submit the form**
   - Click the submit button (look for text like "Submit", "Register", "Create account", etc.).
   - After submission, confirm that the registration/login was successful by checking for success messages or URL changes.

6. **Error handling**
   - If the form submission fails, analyze the error message and adjust your approach (different selectors, stronger password, etc.) instead of repeating the same action.


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
            else:
                updates = {
                    "last_action": tool_name,
                    "error": None
                }

        except Exception as e:
            updates["error"] = f"Error updating state after tool '{tool_name}': {str(e)}"

    return Command(
        update={
            **updates,
            "messages": result.get("messages", [])
        }
    )
