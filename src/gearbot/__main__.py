import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

from gearbot.graph import create_web_graph
from gearbot.core.browser import browser_manager

load_dotenv()

console = Console()

async def main():
    """Función principal del agente"""
    console.print("[bold green]🚀 GearBot - Agente Web con Grok listo![/bold green]")
    console.print(f"Modelo: [cyan]{os.getenv('GROK_MODEL', 'grok-4')}[/cyan]")
    console.print(f"Modo navegador: [yellow]{'Headless' if os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true' else 'Visible'}[/yellow]\n")

    try:
        await browser_manager.start()
        console.print("[green]✅ Navegador iniciado correctamente.[/green]\n")
    except Exception as e:
        console.print(f"[red]Error al iniciar navegador: {e}[/red]")
        return

    graph = create_web_graph()

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]Tú[/bold cyan]")

            if user_input.lower() in ["salir", "exit", "q", "quit"]:
                console.print("[yellow]Cerrando agente...[/yellow]")
                break

            console.print("[dim]Procesando...[/dim]\n")

            last_state = None
            previous_url = None

            async for state in graph.astream(
                {"messages": [("user", user_input)]},
                stream_mode="values"
            ):
                last_state = state
                current_url = state.get("current_url")

                # Solo mostramos el panel si la URL cambió o es la primera vez que tiene datos
                if current_url and current_url != previous_url:
                    console.print(Panel(
                        f"[cyan]URL:[/cyan] {current_url}\n"
                        f"[cyan]Título:[/cyan] {state.get('page_title') or '—'}\n"
                        f"[cyan]Última acción:[/cyan] {state.get('last_action') or 'Ninguna'}\n"
                        f"[cyan]Error:[/cyan] {state.get('error') or 'Ninguno'}",
                        title="[bold blue]Estado actualizado[/bold blue]",
                        border_style="green",
                        box=box.ROUNDED
                    ))
                    previous_url = current_url

                # También mostramos si hay error
                elif state.get("error"):
                    console.print(Panel(
                        f"[red]Error:[/red] {state.get('error')}",
                        title="Estado del agente",
                        border_style="red"
                    ))

            # Respuesta final de Grok
            if last_state and last_state.get("messages"):
                final_message = last_state["messages"][-1].content
                console.print(f"\n[bold magenta]Grok:[/bold magenta] {final_message}\n")

        except Exception as e:
            console.print(f"[red]Error durante la ejecución: {str(e)}[/red]")

    await browser_manager.stop()
    console.print("[green]Navegador cerrado. ¡Hasta luego![/green]")



def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()