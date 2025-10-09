""""""

import json
import asyncio
from pathlib import Path
from typing import Optional

import typer
from loguru import logger

from .config import DeepSearchConfig
from .pipeline import DeepSearchPipeline


app = typer.Typer(
    name="deepsearch",
    help="DeepSearch - ",
    add_completion=False
)


@app.command()
def search(
    query: str = typer.Argument(..., help=""),
    topk: int = typer.Option(5, "--topk", "-k", help=""),
    headless: bool = typer.Option(False, "--headless/--no-headless", help=""),
    engine: str = typer.Option("duckduckgo", "--engine", "-e", help=""),
    output: Optional[str] = typer.Option(None, "--output", "-o", help=""),
    shots_dir: str = typer.Option("./shots", "--shots-dir", help=""),
    verbose: bool = typer.Option(False, "--verbose", "-v", help=""),
):
    """"""
    
    # 
    if verbose:
        logger.remove()
        logger.add(
            lambda msg: typer.echo(msg, err=True),
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
            level="DEBUG"
        )
    else:
        logger.remove()
        logger.add(
            lambda msg: typer.echo(msg, err=True),
            format="<level>{level}</level>: {message}",
            level="INFO"
        )
    
    # 
    config = DeepSearchConfig(
        headless=headless,
        search_engine=engine,
        topk=topk,
        shots_dir=shots_dir,
        output_json_path=output
    )
    
    # 
    try:
        result = asyncio.run(_run_search(config, query))
        
        # 
        result_json = result.model_dump_json(indent=2)
        
        if output:
            # 
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.model_dump_json(indent=2))
            
            typer.echo(f": {output_path}")
            
            # 
            typer.echo(f"\n:")
            typer.echo(f": {result.query}")
            typer.echo(f": {result.engine}")
            typer.echo(f": {result.total_found}")
            typer.echo(f": {result.success_count}")
            typer.echo(f": {result.error_count}")
            typer.echo(f": {result.execution_time:.2f}s")
            
            for i, item in enumerate(result.items, 1):
                status = "" if not item.error else ""
                typer.echo(f"{status} {i}. {item.title[:60]}...")
        else:
            # JSON
            typer.echo(result_json)
            
    except KeyboardInterrupt:
        typer.echo("\n", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f": {e}", err=True)
        raise typer.Exit(1)


async def _run_search(config: DeepSearchConfig, query: str):
    """"""
    pipeline = DeepSearchPipeline(config)
    
    # 
    results = await pipeline.search_and_extract(query, topk=config.topk)
    
    # 
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class SearchResult:
        query: str
        engine: str
        total_found: int
        success_count: int
        error_count: int
        execution_time: float
        items: List[dict]
        
        def model_dump_json(self, indent=2):
            import json
            return json.dumps({
                'query': self.query,
                'engine': self.engine,
                'total_found': self.total_found,
                'success_count': self.success_count,
                'error_count': self.error_count,
                'execution_time': self.execution_time,
                'items': self.items
            }, indent=indent, ensure_ascii=False)
    
    # 
    success_count = sum(1 for item in results if item.get('extraction_status') == 'success')
    error_count = len(results) - success_count
    
    return SearchResult(
        query=query,
        engine=config.search_engine,
        total_found=len(results),
        success_count=success_count,
        error_count=error_count,
        execution_time=0.0,  # TODO: 
        items=[{
            'title': item.get('title', ''),
            'url': item.get('url', ''),
            'content': item.get('content', ''),
            'summary': item.get('summary', ''),
            'error': item.get('extraction_error')
        } for item in results]
    )


@app.command()
def install_browser():
    """Playwright"""
    import subprocess
    import sys
    
    try:
        typer.echo("Playwright...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        typer.echo("!")
    except subprocess.CalledProcessError as e:
        typer.echo(f": {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()