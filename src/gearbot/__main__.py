"""GearBot - Web Agent"""
import sys
import asyncio
from rich.console import Console
from rich.panel import Panel
from .gearbot import GearBot

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

def main():
    """Synchronous entry point (obligatorio para uv console scripts)."""
    asyncio.run(run())


async def run():
    """Async main logic."""
    try:
        async with GearBot() as bot:
            await bot.start_web_agent()
    except KeyboardInterrupt:
        Console().print("\n[yellow]Ctrl+C detected. Closing cleanly...[/yellow]")
    except Exception as e:
        Console().print(Panel(
            f"[red]Unexpected critical error: {e}[/red]",
            title="Fatal Error",
            border_style="red"
        ))
        sys.exit(1)


if __name__ == "__main__":
    main()
