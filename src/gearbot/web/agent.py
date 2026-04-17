"""Web agent for GearBot."""
import sys
import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
from gearbot.graph import create_web_graph
from gearbot.core.browser import browser_manager
from gearbot.config import BROWSER_HEADLESS, GROK_MODEL

class WebAgent:
    """WebAgent class responsible for managing web interactions and browser control."""
    def __init__(self, console: Console):
        """Initialize the WebAgent with a browser manager and console for output."""
        self.browser_manager = browser_manager
        self.console = console

    async def start(self):
        """Start the web agent by launching the browser."""
        try:
            await browser_manager.start()
            self.console.print("[green]✅ Browser started correctly.[/green]\n")
        except Exception as e:
            self.console.print(f"[red]Error starting browser: {e}[/red]")
            return

        graph = create_web_graph()
        try:
            while True:
                user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

                if user_input.lower() in ["salir", "exit", "q", "quit"]:
                    self.console.print("[yellow]Closing agent...[/yellow]")
                    break

                self.console.print("[dim]Processing...[/dim]\n")

                last_state = None
                previous_url = None

                async for state in graph.astream(
                    {"messages": [("user", user_input)]},
                    {"configurable": {"thread_id": "1"}},
                    stream_mode="values"
                ):
                    last_state = state
                    current_url = state.get("current_url")

                    self.console.print(Panel(
                            f"[cyan]URL:[/cyan] {current_url}\n"
                            f"[cyan]Title:[/cyan] {state.get('page_title') or '—'}\n"
                            f"[cyan]Last Action:[/cyan] {state.get('last_action') or 'None'}\n"
                            f"[cyan]Error:[/cyan] {state.get('error') or 'None'}",
                            title="[bold blue]State Updated[/bold blue]",
                            border_style="green",
                            box=box.ROUNDED
                        ))

                if last_state and last_state.get("messages"):
                    final_message = last_state["messages"][-1].content
                    self.console.print(f"\n[bold magenta]Grok:[/bold magenta] {final_message}\n")
        except (KeyboardInterrupt, asyncio.CancelledError):
            self.console.print("\n[yellow]Interrupt detected. Closing agent...[/yellow]")
        finally:
            self.console.print("[dim]Closing browser safely...[/dim]")
            try:
                await browser_manager.stop()
            except Exception:
                pass