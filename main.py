import asyncio
from rich.console import Console
from rich.prompt import Prompt
from src.gearbot import create_web_graph, browser_manager

console = Console()

async def main():
    console.print("[bold green]🚀 Agente Web con StateGraph Manual listo![/bold green]")
    
    # Iniciar navegador
    await browser_manager.start(headless=False)
    
    graph = create_web_graph()
    
    while True:
        user_input = Prompt.ask("[bold cyan]Tú[/bold cyan]")
        
        if user_input.lower() in ["salir", "exit", "q"]:
            break
        
        result = await graph.ainvoke({
            "messages": [("user", user_input)]
        })
        
        final_msg = result["messages"][-1].content
        console.print(f"[bold magenta]Agente:[/bold magenta] {final_msg}\n")

    await browser_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())