import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

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

            console.print("[dim]Procesando...[/dim]")

            result = await graph.ainvoke({"messages": [("user", user_input)]})

            final_message = result["messages"][-1].content
            console.print(f"[bold magenta]Grok:[/bold magenta] {final_message}\n")

        except Exception as e:
            console.print(f"[red]Error durante la ejecución: {str(e)}[/red]")

    await browser_manager.stop()
    console.print("[green]Navegador cerrado. ¡Hasta luego![/green]")



def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()