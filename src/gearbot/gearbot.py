"""GearBot - A web automation agent."""
from rich.console import Console
from gearbot.config import BROWSER_HEADLESS, GROK_MODEL
from gearbot.web import WebAgent

class GearBot:
    """Main class for the GearBot agent, responsible for initializing components and running the agent loop."""
    def __init__(self):
        """Initialize the GearBot agent with necessary components."""
        self.web_agent = None
        self.console = None

    @property
    def web_agent(self):
        """Access the browser manager instance."""
        return self.web_agent

    async def __aenter__(self):
        """Asynchronous context manager entry, starting the browser and displaying initial information."""
        self.console = Console()
        self.web_agent = WebAgent(self.console)
        self.console.print("[bold green]🚀 GearBot - Web Agent Ready![/bold green]")
        self.console.print(f"Model: [cyan]{GROK_MODEL}[/cyan]")
        self.console.print(f"Browser Mode: [yellow]{'Headless' if BROWSER_HEADLESS.lower() == 'true'
                                                 else 'Visible'}[/yellow]\n")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous context manager exit, ensuring the browser is closed cleanly."""
        self.console = None
        self.web_agent = None
