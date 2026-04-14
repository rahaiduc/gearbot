# src/agente/__main__.py
import asyncio
import os
from rich.console import Console
from rich.prompt import Prompt
from dotenv import load_dotenv

from gearbot.graph import create_web_graph
from gearbot.core import browser_manager

load_dotenv()
console = Console()

async def main():
    console.print("[bold green]🚀 Agente Web con Grok + LangGraph listo![/bold green]")
    console.print(f"Modelo: [cyan]{os.getenv('GROK_MODEL', 'grok-4')}[/cyan]")
    console.print(f"Navegador en modo: [yellow]{'Headless' if os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true' else 'Visible'}[/yellow]\n")

    # Iniciar navegador
    await browser_manager.start()
    console.print("[green]Navegador iniciado correctamente.[/green]\n")

    graph = create_web_graph()

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]Tú[/bold cyan]")
            
            if user_input.lower() in ["salir", "exit", "q", "quit"]:
                console.print("[yellow]Cerrando agente...[/yellow]")
                break

            console.print("[dim]Procesando...[/dim]")

            result = await graph.ainvoke({
                "messages": [("user", user_input)]
            })

            # Mostrar solo la última respuesta del asistente
            final_message = result["messages"][-1].content
            console.print(f"[bold magenta]Grok:[/bold magenta] {final_message}\n")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

    # Cerrar navegador al salir
    await browser_manager.stop()
    console.print("[green]Navegador cerrado. ¡Hasta luego![/green]")

if __name__ == "__main__":
    asyncio.run(main())