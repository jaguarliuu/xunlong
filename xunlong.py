#!/usr/bin/env python
"""
XunLong - 深度搜索与智能创作系统
专业的CLI入口，支持多种输出模式
"""

import asyncio
import sys
from pathlib import Path

import click

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from src.deep_search_agent import DeepSearchAgent


# CLI主命令组
@click.group()
@click.version_option(version="1.0.0", prog_name="XunLong")
def cli():
    """
    XunLong - 深度搜索与智能创作系统

    支持多种输出模式：报告生成、小说创作、PPT制作等
    """
    pass


# ============================================================
# 报告生成命令
# ============================================================

@cli.command()
@click.argument('query')
@click.option('--type', '-t', 'report_type',
              type=click.Choice(['comprehensive', 'daily', 'analysis', 'research'], case_sensitive=False),
              default='comprehensive',
              help='报告类型：comprehensive(综合), daily(日报), analysis(分析), research(研究)')
@click.option('--depth', '-d',
              type=click.Choice(['surface', 'medium', 'deep'], case_sensitive=False),
              default='deep',
              help='搜索深度：surface(浅层), medium(中等), deep(深度)')
@click.option('--max-results', '-m',
              type=int,
              default=20,
              help='最大搜索结果数量 (默认: 20)')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细执行过程')
def report(query, report_type, depth, max_results, verbose):
    """
    生成研究报告

    示例:

    \b
        xunlong report "人工智能在医疗领域的应用"
        xunlong report "区块链技术" --type analysis --depth deep
        xunlong report "量子计算发展" -t research -m 30 -v
    """
    asyncio.run(_execute_report(query, report_type, depth, max_results, verbose))


async def _execute_report(query: str, report_type: str, depth: str, max_results: int, verbose: bool):
    """执行报告生成"""

    click.echo(click.style("\n=== XunLong 报告生成 ===\n", fg="cyan", bold=True))

    if verbose:
        click.echo(f"查询: {query}")
        click.echo(f"报告类型: {report_type}")
        click.echo(f"搜索深度: {depth}")
        click.echo(f"最大结果数: {max_results}\n")

    try:
        agent = DeepSearchAgent()

        if verbose:
            click.echo(click.style("✓ ", fg="green") + "智能体系统初始化完成\n")

        # 执行搜索，显式指定输出类型为report
        with click.progressbar(length=100, label='执行深度搜索') as bar:
            result = await agent.search(
                query,
                context={
                    'output_type': 'report',  # 显式指定输出类型
                    'report_type': report_type,
                    'search_depth': depth,
                    'max_results': max_results
                }
            )
            bar.update(100)

        click.echo()

        # 显示结果
        _display_result(result, verbose)

    except KeyboardInterrupt:
        click.echo(click.style("\n⚠️  用户中断执行", fg="yellow"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"\n❌ 执行失败: {e}", fg="red"))
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


# ============================================================
# 小说创作命令
# ============================================================

@cli.command()
@click.argument('query')
@click.option('--genre', '-g',
              type=click.Choice(['mystery', 'scifi', 'fantasy', 'horror', 'romance', 'wuxia'], case_sensitive=False),
              default='mystery',
              help='小说类型：mystery(推理), scifi(科幻), fantasy(奇幻), horror(恐怖), romance(爱情), wuxia(武侠)')
@click.option('--length', '-l',
              type=click.Choice(['short', 'medium', 'long'], case_sensitive=False),
              default='short',
              help='篇幅长度：short(短篇5章), medium(中篇12章), long(长篇30章)')
@click.option('--viewpoint', '-vp',
              type=click.Choice(['first', 'third', 'omniscient'], case_sensitive=False),
              default='first',
              help='叙事视角：first(第一人称), third(第三人称), omniscient(全知视角)')
@click.option('--constraint', '-c',
              multiple=True,
              help='特殊约束，可多次指定 (如: -c "暴风雪山庄" -c "密室")')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细执行过程')
def fiction(query, genre, length, viewpoint, constraint, verbose):
    """
    创作小说

    示例:

    \b
        xunlong fiction "写一篇推理小说" --genre mystery --length short
        xunlong fiction "科幻故事" -g scifi -l medium -vp third
        xunlong fiction "密室杀人案" -g mystery -c "暴风雪山庄" -c "本格推理" -v
    """
    asyncio.run(_execute_fiction(query, genre, length, viewpoint, list(constraint), verbose))


async def _execute_fiction(query: str, genre: str, length: str, viewpoint: str,
                           constraints: list, verbose: bool):
    """执行小说创作"""

    click.echo(click.style("\n=== XunLong 小说创作 ===\n", fg="magenta", bold=True))

    if verbose:
        click.echo(f"查询: {query}")
        click.echo(f"类型: {genre}")
        click.echo(f"篇幅: {length}")
        click.echo(f"视角: {viewpoint}")
        if constraints:
            click.echo(f"约束: {', '.join(constraints)}")
        click.echo()

    try:
        agent = DeepSearchAgent()

        if verbose:
            click.echo(click.style("✓ ", fg="green") + "智能体系统初始化完成\n")

        # 映射英文参数到中文
        genre_map = {
            'mystery': '推理',
            'scifi': '科幻',
            'fantasy': '奇幻',
            'horror': '恐怖',
            'romance': '爱情',
            'wuxia': '武侠'
        }

        viewpoint_map = {
            'first': '第一人称',
            'third': '第三人称',
            'omniscient': '全知视角'
        }

        # 执行搜索，显式指定输出类型为fiction
        with click.progressbar(length=100, label='执行小说创作') as bar:
            result = await agent.search(
                query,
                context={
                    'output_type': 'fiction',  # 显式指定输出类型
                    'fiction_requirements': {
                        'genre': genre_map.get(genre, genre),
                        'length': length,
                        'viewpoint': viewpoint_map.get(viewpoint, viewpoint),
                        'constraints': constraints
                    }
                }
            )
            bar.update(100)

        click.echo()

        # 显示结果
        _display_result(result, verbose, output_type='fiction')

    except KeyboardInterrupt:
        click.echo(click.style("\n⚠️  用户中断执行", fg="yellow"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"\n❌ 执行失败: {e}", fg="red"))
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


# ============================================================
# PPT生成命令（预留）
# ============================================================

@cli.command()
@click.argument('query')
@click.option('--theme', '-t',
              type=click.Choice(['business', 'academic', 'creative'], case_sensitive=False),
              default='business',
              help='PPT主题：business(商务), academic(学术), creative(创意)')
@click.option('--slides', '-s',
              type=int,
              default=10,
              help='幻灯片数量 (默认: 10)')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细执行过程')
def ppt(query, theme, slides, verbose):
    """
    生成PPT演示文稿（功能开发中）

    示例:

    \b
        xunlong ppt "产品介绍" --theme business --slides 15
        xunlong ppt "研究报告" -t academic -s 20 -v
    """
    click.echo(click.style("\n⚠️  PPT生成功能正在开发中...\n", fg="yellow", bold=True))
    click.echo("敬请期待！\n")

    # TODO: 实现PPT生成功能
    # asyncio.run(_execute_ppt(query, theme, slides, verbose))


# ============================================================
# 快速问答命令
# ============================================================

@cli.command()
@click.argument('question')
@click.option('--model', '-m',
              type=click.Choice(['fast', 'balanced', 'quality'], case_sensitive=False),
              default='balanced',
              help='模型选择：fast(快速), balanced(平衡), quality(高质量)')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细信息')
def ask(question, model, verbose):
    """
    快速问答（不进行深度搜索）

    示例:

    \b
        xunlong ask "什么是量子计算？"
        xunlong ask "如何学习Python？" --model quality -v
    """
    click.echo(click.style("\n=== XunLong 快速问答 ===\n", fg="blue", bold=True))
    click.echo(f"问题: {question}\n")

    # TODO: 实现快速问答功能
    click.echo(click.style("⚠️  快速问答功能正在开发中...\n", fg="yellow"))


# ============================================================
# 系统状态命令
# ============================================================

@cli.command()
def status():
    """
    查看系统状态

    显示LLM配置、可用提供商等信息
    """
    click.echo(click.style("\n=== XunLong 系统状态 ===\n", fg="cyan", bold=True))

    try:
        agent = DeepSearchAgent()
        status_info = agent.get_status()

        click.echo(f"系统: {status_info.get('system', 'Unknown')}")
        click.echo(f"状态: {click.style('✓ 运行中', fg='green')}")

        if status_info.get('llm_manager'):
            llm_info = status_info['llm_manager']
            click.echo(f"\nLLM配置: {llm_info.get('total_configs', 0)} 个")

            providers = llm_info.get('available_providers', {})
            click.echo("\n可用提供商:")
            for name, info in providers.items():
                status = info.get('status', '未知')
                color = 'green' if status == '可用' else 'yellow'
                click.echo(f"  • {name}: {click.style(status, fg=color)}")

        click.echo()

    except Exception as e:
        click.echo(click.style(f"❌ 获取状态失败: {e}", fg="red"))
        sys.exit(1)


# ============================================================
# 辅助函数
# ============================================================

def _display_result(result: dict, verbose: bool, output_type: str = 'report'):
    """显示执行结果"""

    status = result.get('status', 'unknown')

    if status == 'success':
        click.echo(click.style("✓ ", fg="green", bold=True) +
                   click.style("执行成功", fg="green"))
    else:
        click.echo(click.style("⚠️  ", fg="yellow") +
                   click.style(f"执行状态: {status}", fg="yellow"))

    # 显示项目信息
    if result.get('project_id'):
        click.echo(f"\n项目ID: {result['project_id']}")

    if result.get('project_dir'):
        project_dir = result['project_dir']
        click.echo(f"项目目录: {click.style(project_dir, fg='cyan')}")

    # 显示执行步骤
    if verbose and result.get('messages'):
        click.echo(f"\n{click.style('执行步骤:', bold=True)}")
        for msg in result['messages']:
            if msg.get('agent'):
                agent = msg.get('agent', 'Unknown')
                content = msg.get('content', '')[:60]
                click.echo(f"  {click.style('✓', fg='green')} {agent}: {content}...")

    # 显示最终输出
    if result.get('final_report') and result['final_report'].get('result'):
        final_result = result['final_report']['result']

        if final_result.get('report'):
            report_data = final_result['report']

            if output_type == 'fiction':
                click.echo(f"\n{click.style('=== 小说预览 ===', fg='magenta', bold=True)}")

                # 显示小说信息
                metadata = report_data.get('metadata', {})
                click.echo(f"\n标题: {report_data.get('title', '未知')}")
                click.echo(f"类型: {metadata.get('genre', '未知')}")
                click.echo(f"总章节: {metadata.get('total_chapters', 0)}")
                click.echo(f"成功写作: {metadata.get('successful_chapters', 0)} 章")
                click.echo(f"总字数: {report_data.get('word_count', 0)}")

            else:
                click.echo(f"\n{click.style('=== 报告预览 ===', fg='cyan', bold=True)}")
                click.echo(f"\n标题: {report_data.get('title', '未知')}")
                click.echo(f"字数: {report_data.get('word_count', 0)}")

            # 显示内容预览
            content = report_data.get('content', '')
            if content:
                preview = content[:500].strip()
                click.echo(f"\n{preview}...")

            # 显示保存位置
            if result.get('project_dir'):
                report_path = f"{result['project_dir']}/reports/FINAL_REPORT.md"
                click.echo(f"\n{click.style('✓', fg='green')} 完整内容已保存到: {click.style(report_path, fg='cyan')}")

    # 显示搜索结果统计
    if result.get('search_results'):
        count = len(result['search_results'])
        click.echo(f"\n{click.style('✓', fg='green')} 找到 {count} 个搜索结果")

    # 显示错误信息
    if result.get('errors'):
        click.echo(f"\n{click.style('警告:', fg='yellow', bold=True)}")
        for error in result['errors']:
            click.echo(f"  • {error}")

    click.echo()


# ============================================================
# 主入口
# ============================================================

if __name__ == '__main__':
    cli()
