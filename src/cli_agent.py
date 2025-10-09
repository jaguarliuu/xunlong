"""DeepSearchCLI"""

import asyncio
import json
import sys
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print(": rich")

from .deep_search_agent import DeepSearchAgent

# CLI
app = typer.Typer(
    name="deepsearch-agent",
    help="DeepSearch - LangGraphagent",
    add_completion=False
)

if RICH_AVAILABLE:
    console = Console()
else:
    console = None


def print_info(message: str):
    """TODO: Add docstring."""
    if console:
        console.print(f"[blue][/blue] {message}")
    else:
        print(f"INFO: {message}")


def print_success(message: str):
    """TODO: Add docstring."""
    if console:
        console.print(f"[green][/green] {message}")
    else:
        print(f"SUCCESS: {message}")


def print_error(message: str):
    """TODO: Add docstring."""
    if console:
        console.print(f"[red][/red] {message}")
    else:
        print(f"ERROR: {message}")


def print_warning(message: str):
    """TODO: Add docstring."""
    if console:
        console.print(f"[yellow][/yellow] {message}")
    else:
        print(f"WARNING: {message}")


@app.command()
def search(
    query: str = typer.Argument(..., help=""),
    output: Optional[str] = typer.Option(None, "--output", "-o", help=""),
    config: Optional[str] = typer.Option(None, "--config", "-c", help=""),
    max_results: int = typer.Option(5, "--max-results", "-n", help=""),
    report_type: str = typer.Option("", "--report-type", "-t", help=" (/)"),
    format: str = typer.Option("markdown", "--format", "-f", help=" (json/markdown/text)"),
    timeout: int = typer.Option(300, "--timeout", help="()"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="")
):
    """TODO: Add docstring."""
    
    async def run_search():
        try:
            # 
            if config:
                agent = DeepSearchAgent(config)
            else:
                agent = DeepSearchAgent()
            
            print_info(f": {query}")
            
            # 
            search_config = {
                "max_search_results": max_results,
                "synthesis_config": {
                    "report_type": f"{report_type}",
                    "target_audience": "",
                    "detail_level": report_type
                },
                "timeout_seconds": timeout
            }
            
            # 
            if console and not verbose:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task("...", total=None)
                    result = await agent.search(query, config=search_config)
            else:
                result = await agent.search(query, config=search_config)
            
            # 
            if result["status"] in ["success", "partial_success"]:
                print_success(f": {result['status']}")
                
                if verbose:
                    print_info(f": {', '.join(result.get('execution_steps', []))}")
                    
                    if result.get('optimization_result'):
                        opt_queries = len(result['optimization_result'].get('optimized_queries', []))
                        print_info(f" {opt_queries} ")
                    
                    if result.get('search_results'):
                        success_count = result['search_results'].get('success_count', 0)
                        print_info(f" {success_count} ")
                
                # 
                await output_result(result, output, format)
                
            else:
                print_error(f": {result.get('error', '')}")
                if result.get('errors'):
                    for error in result['errors']:
                        print_error(f"  - {error}")
                sys.exit(1)
                
        except Exception as e:
            print_error(f": {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    asyncio.run(run_search())


@app.command()
def quick(
    query: str = typer.Argument(..., help=""),
    output: Optional[str] = typer.Option(None, "--output", "-o", help=""),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="")
):
    """TODO: Add docstring."""
    
    async def run_quick():
        try:
            # 
            if config:
                agent = DeepSearchAgent(config)
            else:
                agent = DeepSearchAgent()
            
            print_info(f": {query}")
            
            # 
            if console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task("...", total=None)
                    answer = await agent.quick_answer(query)
            else:
                answer = await agent.quick_answer(query)
            
            # 
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(answer)
                print_success(f": {output}")
            else:
                if console:
                    console.print(Panel(answer, title="", border_style="green"))
                else:
                    print(f"\n:\n{answer}\n")
                    
        except Exception as e:
            print_error(f": {e}")
            sys.exit(1)
    
    asyncio.run(run_quick())


@app.command()
def status(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="")
):
    """TODO: Add docstring."""
    try:
        # 
        if config:
            agent = DeepSearchAgent(config)
        else:
            agent = DeepSearchAgent()
        
        # 
        system_status = agent.get_system_status()
        
        if console:
            # Rich
            
            # LLM
            llm_table = Table(title="LLM")
            llm_table.add_column("", style="cyan")
            llm_table.add_column("", style="green")
            
            llm_status = system_status['llm_manager']
            llm_table.add_row("", llm_status['config_path'])
            llm_table.add_row("", str(llm_status['total_configs']))
            llm_table.add_row("", str(llm_status['active_clients']))
            llm_table.add_row("", ", ".join(llm_status['available_configs']))
            
            console.print(llm_table)
            console.print()
            
            # 
            agent_table = Table(title="")
            agent_table.add_column("", style="cyan")
            agent_table.add_column("", style="green")
            agent_table.add_column("", style="yellow")
            
            agents_status = system_status['agents_status']
            for agent_name, agent_info in agents_status.items():
                agent_table.add_row(
                    agent_name,
                    agent_info['status'],
                    agent_info['llm_model']['model_name']
                )
            
            console.print(agent_table)
            console.print()
            
            # 
            coord_table = Table(title="")
            coord_table.add_column("", style="cyan")
            coord_table.add_column("", style="green")
            
            coord_config = system_status['coordinator_config']
            coord_table.add_row("", str(coord_config['max_search_results']))
            coord_table.add_row("", str(coord_config['enable_parallel_analysis']))
            coord_table.add_row("", f"{coord_config['timeout_seconds']}")
            
            console.print(coord_table)
            
        else:
            # 
            print("===  ===")
            print(f"LLM: {system_status['llm_manager']['total_configs']}")
            print(f": {len(system_status['agents_status'])}")
            print(f": {system_status['coordinator_config']['max_search_results']}")
            
    except Exception as e:
        print_error(f": {e}")
        sys.exit(1)


@app.command()
def test(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="")
):
    """TODO: Add docstring."""
    try:
        # 
        if config:
            agent = DeepSearchAgent(config)
        else:
            agent = DeepSearchAgent()
        
        print_info("...")
        
        # 
        results = agent.test_connections()
        
        if console:
            table = Table(title="")
            table.add_column("", style="cyan")
            table.add_column("", style="green")
            
            for config_name, success in results.items():
                status = " " if success else " "
                style = "green" if success else "red"
                table.add_row(config_name, f"[{style}]{status}[/{style}]")
            
            console.print(table)
        else:
            print(":")
            for config_name, success in results.items():
                status = "" if success else ""
                print(f"  {config_name}: {status}")
        
        # 
        failed_count = sum(1 for success in results.values() if not success)
        if failed_count > 0:
            print_warning(f"{failed_count} ")
        else:
            print_success("")
            
    except Exception as e:
        print_error(f": {e}")
        sys.exit(1)


async def output_result(result: Dict[str, Any], output_path: Optional[str], format: str):
    """TODO: Add docstring."""
    
    if format == "json":
        # JSON
        output_data = result
        content = json.dumps(output_data, ensure_ascii=False, indent=2)
        
    elif format == "text":
        # 
        if result.get('final_report'):
            content = result['final_report']['report_content']
        else:
            content = f": {result['user_query']}\n: {result['status']}\n"
            if result.get('errors'):
                content += f": {', '.join(result['errors'])}\n"
    
    else:  # markdown ()
        # Markdown
        if result.get('final_report'):
            content = result['final_report']['report_content']
        else:
            content = f"# \n\n****: {result['user_query']}\n\n****: {result['status']}\n"
            if result.get('errors'):
                content += f"\n****:\n" + "\n".join(f"- {error}" for error in result['errors'])
    
    # 
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print_success(f": {output_path}")
    else:
        if console and format == "markdown":
            console.print(Markdown(content))
        else:
            print(content)


if __name__ == "__main__":
    app()