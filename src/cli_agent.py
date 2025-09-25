"""DeepSearch智能体系统CLI接口"""

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
    print("警告: rich库未安装，将使用基础输出格式")

from .deep_search_agent import DeepSearchAgent

# 创建CLI应用
app = typer.Typer(
    name="deepsearch-agent",
    help="DeepSearch智能体系统 - 基于LangGraph的多agent协作深度搜索工具",
    add_completion=False
)

if RICH_AVAILABLE:
    console = Console()
else:
    console = None


def print_info(message: str):
    """打印信息"""
    if console:
        console.print(f"[blue]ℹ[/blue] {message}")
    else:
        print(f"INFO: {message}")


def print_success(message: str):
    """打印成功信息"""
    if console:
        console.print(f"[green]✓[/green] {message}")
    else:
        print(f"SUCCESS: {message}")


def print_error(message: str):
    """打印错误信息"""
    if console:
        console.print(f"[red]✗[/red] {message}")
    else:
        print(f"ERROR: {message}")


def print_warning(message: str):
    """打印警告信息"""
    if console:
        console.print(f"[yellow]⚠[/yellow] {message}")
    else:
        print(f"WARNING: {message}")


@app.command()
def search(
    query: str = typer.Argument(..., help="搜索查询"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    max_results: int = typer.Option(5, "--max-results", "-n", help="最大搜索结果数"),
    report_type: str = typer.Option("详细", "--report-type", "-t", help="报告类型 (简要/详细)"),
    format: str = typer.Option("markdown", "--format", "-f", help="输出格式 (json/markdown/text)"),
    timeout: int = typer.Option(300, "--timeout", help="超时时间(秒)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出")
):
    """执行深度搜索"""
    
    async def run_search():
        try:
            # 初始化智能体
            if config:
                agent = DeepSearchAgent(config)
            else:
                agent = DeepSearchAgent()
            
            print_info(f"开始深度搜索: {query}")
            
            # 配置搜索参数
            search_config = {
                "max_search_results": max_results,
                "synthesis_config": {
                    "report_type": f"{report_type}分析报告",
                    "target_audience": "一般用户",
                    "detail_level": report_type
                },
                "timeout_seconds": timeout
            }
            
            # 执行搜索
            if console and not verbose:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task("正在执行深度搜索...", total=None)
                    result = await agent.search(query, config=search_config)
            else:
                result = await agent.search(query, config=search_config)
            
            # 处理结果
            if result["status"] in ["success", "partial_success"]:
                print_success(f"搜索完成，状态: {result['status']}")
                
                if verbose:
                    print_info(f"执行步骤: {', '.join(result.get('execution_steps', []))}")
                    
                    if result.get('optimization_result'):
                        opt_queries = len(result['optimization_result'].get('optimized_queries', []))
                        print_info(f"生成了 {opt_queries} 个优化查询")
                    
                    if result.get('search_results'):
                        success_count = result['search_results'].get('success_count', 0)
                        print_info(f"成功获取 {success_count} 个搜索结果")
                
                # 输出结果
                await output_result(result, output, format)
                
            else:
                print_error(f"搜索失败: {result.get('error', '未知错误')}")
                if result.get('errors'):
                    for error in result['errors']:
                        print_error(f"  - {error}")
                sys.exit(1)
                
        except Exception as e:
            print_error(f"执行失败: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    asyncio.run(run_search())


@app.command()
def quick(
    query: str = typer.Argument(..., help="快速查询"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径")
):
    """快速回答"""
    
    async def run_quick():
        try:
            # 初始化智能体
            if config:
                agent = DeepSearchAgent(config)
            else:
                agent = DeepSearchAgent()
            
            print_info(f"快速查询: {query}")
            
            # 执行快速回答
            if console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task("正在生成回答...", total=None)
                    answer = await agent.quick_answer(query)
            else:
                answer = await agent.quick_answer(query)
            
            # 输出回答
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(answer)
                print_success(f"回答已保存到: {output}")
            else:
                if console:
                    console.print(Panel(answer, title="回答", border_style="green"))
                else:
                    print(f"\n回答:\n{answer}\n")
                    
        except Exception as e:
            print_error(f"执行失败: {e}")
            sys.exit(1)
    
    asyncio.run(run_quick())


@app.command()
def status(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径")
):
    """显示系统状态"""
    try:
        # 初始化智能体
        if config:
            agent = DeepSearchAgent(config)
        else:
            agent = DeepSearchAgent()
        
        # 获取状态
        system_status = agent.get_system_status()
        
        if console:
            # 使用Rich表格显示状态
            
            # LLM管理器状态
            llm_table = Table(title="LLM管理器状态")
            llm_table.add_column("项目", style="cyan")
            llm_table.add_column("值", style="green")
            
            llm_status = system_status['llm_manager']
            llm_table.add_row("配置文件", llm_status['config_path'])
            llm_table.add_row("总配置数", str(llm_status['total_configs']))
            llm_table.add_row("活跃客户端", str(llm_status['active_clients']))
            llm_table.add_row("可用配置", ", ".join(llm_status['available_configs']))
            
            console.print(llm_table)
            console.print()
            
            # 智能体状态
            agent_table = Table(title="智能体状态")
            agent_table.add_column("智能体", style="cyan")
            agent_table.add_column("状态", style="green")
            agent_table.add_column("模型", style="yellow")
            
            agents_status = system_status['agents_status']
            for agent_name, agent_info in agents_status.items():
                agent_table.add_row(
                    agent_name,
                    agent_info['status'],
                    agent_info['llm_model']['model_name']
                )
            
            console.print(agent_table)
            console.print()
            
            # 协调器配置
            coord_table = Table(title="协调器配置")
            coord_table.add_column("配置项", style="cyan")
            coord_table.add_column("值", style="green")
            
            coord_config = system_status['coordinator_config']
            coord_table.add_row("最大搜索结果", str(coord_config['max_search_results']))
            coord_table.add_row("并行分析", str(coord_config['enable_parallel_analysis']))
            coord_table.add_row("超时时间", f"{coord_config['timeout_seconds']}秒")
            
            console.print(coord_table)
            
        else:
            # 基础文本输出
            print("=== 系统状态 ===")
            print(f"LLM配置数量: {system_status['llm_manager']['total_configs']}")
            print(f"智能体数量: {len(system_status['agents_status'])}")
            print(f"最大搜索结果: {system_status['coordinator_config']['max_search_results']}")
            
    except Exception as e:
        print_error(f"获取状态失败: {e}")
        sys.exit(1)


@app.command()
def test(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径")
):
    """测试系统连接"""
    try:
        # 初始化智能体
        if config:
            agent = DeepSearchAgent(config)
        else:
            agent = DeepSearchAgent()
        
        print_info("测试系统连接...")
        
        # 测试连接
        results = agent.test_connections()
        
        if console:
            table = Table(title="连接测试结果")
            table.add_column("配置", style="cyan")
            table.add_column("状态", style="green")
            
            for config_name, success in results.items():
                status = "✓ 成功" if success else "✗ 失败"
                style = "green" if success else "red"
                table.add_row(config_name, f"[{style}]{status}[/{style}]")
            
            console.print(table)
        else:
            print("连接测试结果:")
            for config_name, success in results.items():
                status = "成功" if success else "失败"
                print(f"  {config_name}: {status}")
        
        # 检查是否有失败的连接
        failed_count = sum(1 for success in results.values() if not success)
        if failed_count > 0:
            print_warning(f"{failed_count} 个配置连接失败")
        else:
            print_success("所有连接测试通过")
            
    except Exception as e:
        print_error(f"测试失败: {e}")
        sys.exit(1)


async def output_result(result: Dict[str, Any], output_path: Optional[str], format: str):
    """输出结果"""
    
    if format == "json":
        # JSON格式输出
        output_data = result
        content = json.dumps(output_data, ensure_ascii=False, indent=2)
        
    elif format == "text":
        # 纯文本格式输出
        if result.get('final_report'):
            content = result['final_report']['report_content']
        else:
            content = f"搜索查询: {result['user_query']}\n状态: {result['status']}\n"
            if result.get('errors'):
                content += f"错误: {', '.join(result['errors'])}\n"
    
    else:  # markdown (默认)
        # Markdown格式输出
        if result.get('final_report'):
            content = result['final_report']['report_content']
        else:
            content = f"# 搜索结果\n\n**查询**: {result['user_query']}\n\n**状态**: {result['status']}\n"
            if result.get('errors'):
                content += f"\n**错误**:\n" + "\n".join(f"- {error}" for error in result['errors'])
    
    # 输出到文件或控制台
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print_success(f"结果已保存到: {output_path}")
    else:
        if console and format == "markdown":
            console.print(Markdown(content))
        else:
            print(content)


if __name__ == "__main__":
    app()