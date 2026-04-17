"""GearBot - Web Agent"""
import sys
import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
from gearbot.graph import create_web_graph
from gearbot.core.browser import browser_manager
from gearbot.config import BROWSER_HEADLESS, GROK_MODEL
from gearbot.web import WebAgent
from .gearbot import GearBot

console = Console()

if sys.platform == "win32":
    from asyncio.proactor_events import _ProactorBasePipeTransport

    def silence_event_loop_closed(func):
        """Decorator to silence 'Event loop is closed' errors on Windows when the transport is 
        garbage collected."""
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except RuntimeError as e:
                if str(e) != 'Event loop is closed':
                    raise
        return wrapper

    _ProactorBasePipeTransport.__del__ = (
        silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
    )

async def main():
    """Main function to run the GearBot agent, handling user input and displaying agent
    responses and state updates.
    """
    console.print("[bold green]🚀 GearBot - Web Agent Ready![/bold green]")
    console.print(f"Model: [cyan]{GROK_MODEL}[/cyan]")
    console.print(f"Browser Mode: [yellow]{'Headless' if BROWSER_HEADLESS.lower() == 'true'
                                             else 'Visible'}[/yellow]\n")

    try:
        await browser_manager.start()
        console.print("[green]✅ Browser started correctly.[/green]\n")
    except Exception as e:
        console.print(f"[red]Error starting browser: {e}[/red]")
        return

    graph = create_web_graph()
    try:
        while True:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

            if user_input.lower() in ["salir", "exit", "q", "quit"]:
                console.print("[yellow]Closing agent...[/yellow]")
                break

            console.print("[dim]Processing...[/dim]\n")

            last_state = None
            previous_url = None

            async for state in graph.astream(
                {"messages": [("user", user_input)]},
                {"configurable": {"thread_id": "1"}},
                stream_mode="values"
            ):
                last_state = state
                current_url = state.get("current_url")

                console.print(Panel(
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
                console.print(f"\n[bold magenta]Grok:[/bold magenta] {final_message}\n")
    except (KeyboardInterrupt, asyncio.CancelledError):
        console.print("\n[yellow]Interrupt detected. Closing agent...[/yellow]")
    finally:
        console.print("[dim]Closing browser safely...[/dim]")
        try:
            await browser_manager.stop()
        except Exception:
            pass

async def run():
    """Run the GearBot agent."""
    try:
        async with GearBot() as agent:
            agent.web_agent.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]Ctrl+C detected. Closing cleanly...[/yellow]")
    except Exception as e:
        console.print(Panel(
            f"[red]Unexpected critical error: {e}[/red]",
            title="Fatal Error",
            border_style="red"
        ))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run())
