"""命令行接口模块"""

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
    help="DeepSearch - 智能搜索与内容抽取工具",
    add_completion=False
)


@app.command()
def search(
    query: str = typer.Argument(..., help="搜索查询词"),
    topk: int = typer.Option(5, "--topk", "-k", help="抓取结果数量"),
    headless: bool = typer.Option(False, "--headless/--no-headless", help="是否使用无头浏览器"),
    engine: str = typer.Option("duckduckgo", "--engine", "-e", help="搜索引擎"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    shots_dir: str = typer.Option("./shots", "--shots-dir", help="截图保存目录"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
):
    """执行搜索并抽取内容"""
    
    # 配置日志
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
    
    # 创建配置
    config = DeepSearchConfig(
        headless=headless,
        search_engine=engine,
        topk=topk,
        shots_dir=shots_dir,
        output_json_path=output
    )
    
    # 执行搜索
    try:
        result = asyncio.run(_run_search(config, query))
        
        # 输出结果
        result_json = result.model_dump_json(indent=2)
        
        if output:
            # 保存到文件
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.model_dump_json(indent=2))
            
            typer.echo(f"结果已保存到: {output_path}")
            
            # 简化输出到控制台
            typer.echo(f"\n搜索完成:")
            typer.echo(f"查询词: {result.query}")
            typer.echo(f"搜索引擎: {result.engine}")
            typer.echo(f"找到结果: {result.total_found}")
            typer.echo(f"成功处理: {result.success_count}")
            typer.echo(f"处理失败: {result.error_count}")
            typer.echo(f"执行时间: {result.execution_time:.2f}s")
            
            for i, item in enumerate(result.items, 1):
                status = "✓" if not item.error else "✗"
                typer.echo(f"{status} {i}. {item.title[:60]}...")
        else:
            # 直接输出JSON
            typer.echo(result_json)
            
    except KeyboardInterrupt:
        typer.echo("\n搜索已取消", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"搜索失败: {e}", err=True)
        raise typer.Exit(1)


async def _run_search(config: DeepSearchConfig, query: str):
    """运行搜索的异步函数"""
    pipeline = DeepSearchPipeline(config)
    return await pipeline.search(query)


@app.command()
def install_browser():
    """安装Playwright浏览器"""
    import subprocess
    import sys
    
    try:
        typer.echo("正在安装Playwright浏览器...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        typer.echo("浏览器安装完成!")
    except subprocess.CalledProcessError as e:
        typer.echo(f"浏览器安装失败: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()