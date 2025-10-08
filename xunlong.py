#!/usr/bin/env python
"""
XunLong - 深度搜索与智能创作系统
专业的CLI入口，支持多种输出模式
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Optional

import click

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from src.deep_search_agent import DeepSearchAgent
from src.utils.document_loader import load_document, LoadedDocument, DocumentLoadError


# CLI主命令组
@click.group()
@click.version_option(version="1.0.0", prog_name="XunLong")
def cli():
    """
    XunLong - 深度搜索与智能创作系统

    支持多种输出模式：报告生成、小说创作、PPT制作等
    """
    pass


def _load_user_document(input_file: Optional[Path], verbose: bool) -> Dict[str, Dict[str, object] | str]:
    """Load optional user document and return context payload."""

    if not input_file:
        return {}

    try:
        loaded: LoadedDocument = load_document(input_file)
    except DocumentLoadError as exc:
        click.echo(click.style(f"❌ 无法读取文档: {exc}", fg="red"))
        sys.exit(1)

    if verbose:
        meta_msg = f"引用文档: {loaded.filename} ({loaded.char_length} 字符"
        if loaded.truncated:
            meta_msg += "，已截断"
        meta_msg += ")"
        click.echo(meta_msg)

    return {
        'user_document': loaded.content,
        'user_document_meta': {
            'filename': loaded.filename,
            'suffix': loaded.suffix,
            'char_length': loaded.char_length,
            'truncated': loaded.truncated,
            'source_path': loaded.source_path
        }
    }


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
@click.option('--output-format', '-o',
              type=click.Choice(['html', 'md', 'markdown'], case_sensitive=False),
              default='html',
              help='输出格式：html(HTML网页), md/markdown(Markdown文档)')
@click.option('--html-template',
              type=str,
              default='academic',
              help='HTML模板：academic(学术), technical(技术)')
@click.option('--html-theme',
              type=str,
              default='light',
              help='HTML主题：light(浅色), dark(深色)')
@click.option('--input-file',
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help='预加载用户文档（.txt/.pdf/.docx）作为上下文')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细执行过程')
def report(query, report_type, depth, max_results, output_format, html_template, html_theme, input_file, verbose):
    """
    生成研究报告

    示例:

    \b
        xunlong report "人工智能在医疗领域的应用"
        xunlong report "区块链技术" --type analysis --depth deep -o html
        xunlong report "量子计算发展" -t research -m 30 -o md -v
    """
    asyncio.run(_execute_report(query, report_type, depth, max_results, output_format, html_template, html_theme, input_file, verbose))


async def _execute_report(query: str, report_type: str, depth: str, max_results: int,
                          output_format: str, html_template: str, html_theme: str,
                          input_file: Optional[Path], verbose: bool):
    """执行报告生成"""

    click.echo(click.style("\n=== XunLong 报告生成 ===\n", fg="cyan", bold=True))

    # 标准化输出格式
    output_format = 'md' if output_format in ['markdown', 'md'] else output_format

    if verbose:
        click.echo(f"查询: {query}")
        click.echo(f"报告类型: {report_type}")
        click.echo(f"搜索深度: {depth}")
        click.echo(f"最大结果数: {max_results}")
        click.echo(f"输出格式: {output_format}")
        if output_format == 'html':
            click.echo(f"HTML模板: {html_template}")
            click.echo(f"HTML主题: {html_theme}")
        click.echo()

    user_document = _load_user_document(input_file, verbose)

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
                    'max_results': max_results,
                    'output_format': output_format,  # 输出格式
                    'html_template': html_template,  # HTML模板
                    'html_theme': html_theme,  # HTML主题
                    **user_document
                }
            )
            bar.update(100)

        click.echo()

        # 显示结果
        _display_result(result, verbose, output_format=output_format)

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
@click.option('--output-format', '-o',
              type=click.Choice(['html', 'md', 'markdown'], case_sensitive=False),
              default='html',
              help='输出格式：html(HTML网页), md/markdown(Markdown文档)')
@click.option('--html-template',
              type=str,
              default='novel',
              help='HTML模板：novel(小说), ebook(电子书)')
@click.option('--html-theme',
              type=str,
              default='sepia',
              help='HTML主题：light(浅色), dark(深色), sepia(复古)')
@click.option('--input-file',
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help='预加载用户文档（.txt/.pdf/.docx）作为创作上下文')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细执行过程')
def fiction(query, genre, length, viewpoint, constraint, output_format, html_template, html_theme, input_file, verbose):
    """
    创作小说

    示例:

    \b
        xunlong fiction "写一篇推理小说" --genre mystery --length short
        xunlong fiction "科幻故事" -g scifi -l medium -vp third -o html
        xunlong fiction "密室杀人案" -g mystery -c "暴风雪山庄" -o md -v
    """
    asyncio.run(_execute_fiction(query, genre, length, viewpoint, list(constraint), output_format, html_template, html_theme, input_file, verbose))


async def _execute_fiction(query: str, genre: str, length: str, viewpoint: str,
                           constraints: list, output_format: str, html_template: str, html_theme: str,
                           input_file: Optional[Path], verbose: bool):
    """执行小说创作"""

    click.echo(click.style("\n=== XunLong 小说创作 ===\n", fg="magenta", bold=True))

    # 标准化输出格式
    output_format = 'md' if output_format in ['markdown', 'md'] else output_format

    if verbose:
        click.echo(f"查询: {query}")
        click.echo(f"类型: {genre}")
        click.echo(f"篇幅: {length}")
        click.echo(f"视角: {viewpoint}")
        if constraints:
            click.echo(f"约束: {', '.join(constraints)}")
        click.echo(f"输出格式: {output_format}")
        if output_format == 'html':
            click.echo(f"HTML模板: {html_template}")
            click.echo(f"HTML主题: {html_theme}")
        click.echo()

    user_document = _load_user_document(input_file, verbose)

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
                    },
                    'output_format': output_format,  # 输出格式
                    'html_template': html_template,  # HTML模板
                    'html_theme': html_theme,  # HTML主题
                    **user_document
                }
            )
            bar.update(100)

        click.echo()

        # 显示结果
        _display_result(result, verbose, output_type='fiction', output_format=output_format)

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
# PPT生成命令
# ============================================================

@cli.command()
@click.argument('topic')
@click.option('--style', '-s',
              type=click.Choice(['red', 'business', 'academic', 'creative', 'simple'], case_sensitive=False),
              default='business',
              help='PPT风格：red(RED简约风), business(商务详细), academic(学术风), creative(创意风), simple(极简风)')
@click.option('--slides', '-n',
              type=int,
              default=10,
              help='PPT页数 (默认: 10)')
@click.option('--depth', '-d',
              type=click.Choice(['surface', 'medium', 'deep'], case_sensitive=False),
              default='medium',
              help='内容深度：surface(浅层), medium(中等), deep(深度)')
@click.option('--theme',
              type=str,
              default='default',
              help='主题色：default(默认), blue(蓝色), red(红色), green(绿色), purple(紫色)')
@click.option('--speech-notes',
              type=str,
              default=None,
              help='生成演说稿。传入场景描述（如："投资人路演"），将为每页生成对应的演说稿并保存到文件')
@click.option('--input-file',
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help='预加载用户文档（.txt/.pdf/.docx）作为PPT素材')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细执行过程')
def ppt(topic, style, slides, depth, theme, speech_notes, input_file, verbose):
    """
    生成PPT演示文稿

    示例:

    \b
        xunlong ppt "人工智能技术趋势"
        xunlong ppt "产品发布会" --style business --slides 15
        xunlong ppt "2025年度总结" -s red -n 8 -v
        xunlong ppt "学术报告" -s academic -d deep --theme blue
        xunlong ppt "投资路演" --speech-notes "面向风险投资人的项目路演" -v
    """
    asyncio.run(_execute_ppt(topic, style, slides, depth, theme, speech_notes, input_file, verbose))


async def _execute_ppt(topic: str, style: str, slides: int, depth: str, theme: str,
                       speech_notes: str, input_file: Optional[Path], verbose: bool):
    """执行PPT生成"""

    click.echo(click.style("\n=== XunLong PPT生成 ===\n", fg="green", bold=True))

    if verbose:
        click.echo(f"主题: {topic}")
        click.echo(f"风格: {style}")
        click.echo(f"页数: {slides}")
        click.echo(f"深度: {depth}")
        click.echo(f"主题色: {theme}")
        if speech_notes:
            click.echo(f"演说稿场景: {speech_notes}")
        click.echo()

    user_document = _load_user_document(input_file, verbose)

    try:
        agent = DeepSearchAgent()

        ppt_context = {
            'output_type': 'ppt',  # 指定输出类型为PPT
            'ppt_config': {
                'style': style,
                'slides': slides,
                'depth': depth,
                'theme': theme,
                'speech_notes': speech_notes  # 演说稿场景描述
            },
            **user_document
        }

        # 进度条
        with click.progressbar(length=100, label='生成PPT中') as bar:
            result = await agent.search(
                query=topic,
                context=ppt_context
            )
            bar.update(100)

        click.echo()

        # 显示结果
        _display_result(result, verbose, output_type='ppt', output_format='html')

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
# 导出命令
# ============================================================

@cli.command()
@click.argument('project_id')
@click.option('--type', '-t', 'export_type',
              type=click.Choice(['pptx', 'pdf', 'docx', 'md'], case_sensitive=False),
              required=True,
              help='导出格式：pptx(PPT项目), pdf(PDF文档), docx(Word文档), md(Markdown)')
@click.option('--output', '-o',
              type=str,
              default=None,
              help='输出文件路径（可选，默认保存到项目目录）')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细执行过程')
def export(project_id, export_type, output, verbose):
    """
    导出项目到指定格式

    示例:

    \b
        xunlong export 20251004_215421_2025大模型领域产业报告 --type pptx
        xunlong export 20251004_180344_预制菜产业报告 --type pdf -o report.pdf
        xunlong export 20251004_123456_小说项目 --type docx -v
    """
    asyncio.run(_execute_export(project_id, export_type, output, verbose))


async def _execute_export(project_id: str, export_type: str, output_path: str, verbose: bool):
    """执行导出"""

    click.echo(click.style("\n=== XunLong 项目导出 ===\n", fg="cyan", bold=True))

    if verbose:
        click.echo(f"项目ID: {project_id}")
        click.echo(f"导出格式: {export_type.upper()}")
        if output_path:
            click.echo(f"输出路径: {output_path}")
        click.echo()

    try:
        from src.export.export_manager import ExportManager

        export_manager = ExportManager()

        # 执行导出
        with click.progressbar(length=100, label=f'导出为{export_type.upper()}') as bar:
            result = await export_manager.export_project(
                project_id=project_id,
                export_type=export_type,
                output_path=output_path
            )
            bar.update(100)

        click.echo()

        if result["status"] == "success":
            click.echo(click.style("✓ ", fg="green", bold=True) +
                      click.style("导出成功", fg="green"))
            click.echo(f"\n导出文件: {click.style(result['output_file'], fg='cyan')}")

            if result.get("file_size"):
                click.echo(f"文件大小: {result['file_size']}")
        else:
            click.echo(click.style("✗ ", fg="red", bold=True) +
                      click.style(f"导出失败: {result.get('error', '未知错误')}", fg="red"))
            sys.exit(1)

    except ImportError:
        click.echo(click.style("❌ 导出功能需要安装额外依赖", fg="red"))
        click.echo("\n请运行以下命令安装:")
        click.echo("  pip install python-pptx python-docx markdown2 weasyprint")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo(click.style("\n⚠️  用户中断执行", fg="yellow"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"\n❌ 导出失败: {e}", fg="red"))
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


# ============================================================
# 迭代优化命令
# ============================================================

@cli.command()
@click.argument('project_id')
@click.argument('requirement')
@click.option('--verbose', '-v',
              is_flag=True,
              help='显示详细执行过程')
def iterate(project_id, requirement, verbose):
    """
    对已生成的项目进行迭代优化

    示例:

    \b
        xunlong iterate 20251004_215421 "将第3页的图表改成饼图"
        xunlong iterate 20251004_180344 "增加数据对比章节"
        xunlong iterate 20251004_123456 "重写第5章，增加悬念" -v
    """
    asyncio.run(_execute_iterate(project_id, requirement, verbose))


async def _execute_iterate(project_id: str, requirement: str, verbose: bool):
    """执行迭代优化"""

    click.echo(click.style("\n=== XunLong 项目迭代 ===\n", fg="magenta", bold=True))

    if verbose:
        click.echo(f"项目ID: {project_id}")
        click.echo(f"优化需求: {requirement}")
        click.echo()

    try:
        from src.agents.iteration_agent import IterationAgent

        iteration_agent = IterationAgent()

        # 执行迭代
        with click.progressbar(length=100, label='分析并优化项目') as bar:
            result = await iteration_agent.iterate_project(
                project_id=project_id,
                requirement=requirement
            )
            bar.update(100)

        click.echo()

        if result["status"] == "success":
            click.echo(click.style("✓ ", fg="green", bold=True) +
                      click.style("迭代成功", fg="green"))

            click.echo(f"\n项目类型: {result.get('project_type', '未知')}")
            click.echo(f"修改范围: {result.get('modification_scope', '未知')}")
            click.echo(f"新版本: {click.style(result.get('new_version', '未知'), fg='cyan')}")

            if result.get('output_file'):
                click.echo(f"\n更新文件: {click.style(result['output_file'], fg='cyan')}")

            if result.get('changes'):
                click.echo(f"\n修改内容:")
                for change in result['changes']:
                    click.echo(f"  • {change}")
        else:
            click.echo(click.style("✗ ", fg="red", bold=True) +
                      click.style(f"迭代失败: {result.get('error', '未知错误')}", fg="red"))
            sys.exit(1)

    except ImportError:
        click.echo(click.style("❌ 迭代功能模块未找到", fg="red"))
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo(click.style("\n⚠️  用户中断执行", fg="yellow"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"\n❌ 迭代失败: {e}", fg="red"))
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


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

def _display_result(result: dict, verbose: bool, output_type: str = 'report', output_format: str = 'md'):
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

        # PPT类型的处理
        if output_type == 'ppt' and final_result.get('ppt'):
            ppt_data = final_result['ppt']
            click.echo(f"\n{click.style('=== PPT预览 ===', fg='green', bold=True)}")

            metadata = ppt_data.get('metadata', {})
            click.echo(f"\n标题: {ppt_data.get('title', '未知')}")
            click.echo(f"风格: {metadata.get('style', '未知')}")
            click.echo(f"总页数: {metadata.get('slide_count', 0)}")

            # 显示保存位置
            if result.get('project_dir'):
                from pathlib import Path
                project_dir = Path(result['project_dir'])

                html_path = project_dir / 'reports' / 'FINAL_REPORT.html'
                if html_path.exists():
                    click.echo(f"\n{click.style('✓', fg='green')} PPT已保存到: {click.style(str(html_path), fg='cyan')}")
                    click.echo(f"   {click.style('提示: 在浏览器中打开查看全屏PPT演示', fg='bright_black')}")
                    click.echo(f"   {click.style('提示: 使用方向键或滚动翻页', fg='bright_black')}")

        # 报告/小说类型的处理
        elif final_result.get('report'):
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
                from pathlib import Path
                project_dir = Path(result['project_dir'])

                # 显示Markdown文件路径
                md_path = project_dir / 'reports' / 'FINAL_REPORT.md'
                click.echo(f"\n{click.style('✓', fg='green')} 完整内容已保存到: {click.style(str(md_path), fg='cyan')}")

                # 如果是HTML格式，显示HTML文件路径
                if output_format == 'html':
                    html_path = project_dir / 'reports' / 'FINAL_REPORT.html'
                    if html_path.exists():
                        click.echo(f"{click.style('✓', fg='green')} HTML报告: {click.style(str(html_path), fg='cyan')}")
                        click.echo(f"   {click.style('提示: 在浏览器中打开HTML文件以查看精美排版', fg='bright_black')}")

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
