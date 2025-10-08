"""
报告协调器 - 协调多智能体生成高质量报告
"""
import asyncio
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

try:
    import markdown
except ImportError:  # pragma: no cover
    markdown = None

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager
from ...tools.image_searcher import ImageSearcher
from ...tools.image_downloader import ImageDownloader
from .outline_generator import OutlineGenerator
from .section_writer import SectionWriter
from .section_evaluator import SectionEvaluator
from .data_visualizer import DataVisualizer


class ReportCoordinator:
    """报告协调器 - 管理多智能体协作生成报告"""

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager,
        max_iterations: int = 3,
        confidence_threshold: float = 0.7,
        enable_visualization: bool = True,
        enable_images: bool = True
    ):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        self.enable_visualization = enable_visualization
        self.enable_images = enable_images
        self.name = "报告协调器"

        # 初始化智能体
        self.outline_generator = OutlineGenerator(llm_manager, prompt_manager)
        self.section_writer = SectionWriter(llm_manager, prompt_manager)
        self.section_evaluator = SectionEvaluator(
            llm_manager, prompt_manager, confidence_threshold
        )
        self.data_visualizer = DataVisualizer(llm_manager, prompt_manager)

        # 初始化图片相关工具
        if enable_images:
            self.image_searcher = ImageSearcher()
            self.image_downloader = ImageDownloader()
        else:
            self.image_searcher = None
            self.image_downloader = None

    async def generate_report(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        synthesis_results: Optional[Dict[str, Any]] = None,
        report_type: str = "comprehensive",
        output_format: str = "md",
        html_config: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        协调生成高质量报告

        Args:
            query: 查询内容
            search_results: 搜索结果
            synthesis_results: 综合结果
            report_type: 报告类型
            output_format: 输出格式 ('md' 或 'html')
            html_config: HTML配置 {'template': 'academic', 'theme': 'light'}
        """

        logger.info(f"[{self.name}] 开始协作生成报告 (类型: {report_type}, 格式: {output_format})")

        try:
            # Phase 1: 生成大纲
            logger.info(f"[{self.name}] Phase 1: 生成报告大纲")
            outline_result = await self.outline_generator.generate_outline(
                query, search_results, synthesis_results, report_type
            )

            if outline_result["status"] != "success":
                raise Exception("大纲生成失败")

            outline = outline_result["outline"]
            sections = outline["sections"]

            logger.info(f"[{self.name}] 大纲生成完成，共 {len(sections)} 个段落")

            # Phase 2: 并行写作所有段落
            logger.info(f"[{self.name}] Phase 2: 并行写作 {len(sections)} 个段落")
            section_results = await self._parallel_section_writing(
                sections, search_results, query, report_type
            )

            # Phase 3: 迭代评估和优化
            logger.info(f"[{self.name}] Phase 3: 评估与优化段落")
            optimized_sections = await self._iterative_optimization(
                section_results, sections, search_results
            )

            # Phase 3.5: 数据可视化（如果启用）
            if self.enable_visualization:
                logger.info(f"[{self.name}] Phase 3.5: 添加数据可视化")
                optimized_sections = await self._add_visualizations(optimized_sections)

            # Phase 3.6: 添加配图（如果启用）
            if (
                self.enable_images
                and self.image_searcher
                and self.image_searcher.is_available()
                and not all(section.get("images_inserted") for section in optimized_sections)
            ):
                logger.info(f"[{self.name}] Phase 3.6: 为章节添加配图")
                optimized_sections = await self._add_images_to_sections(
                    optimized_sections,
                    project_id=project_id
                )

            # Phase 4: 组装最终报告
            logger.info(f"[{self.name}] Phase 4: 组装最终报告")
            final_report = await self._assemble_report(
                outline, optimized_sections, query, report_type
            )

            logger.info(f"[{self.name}] 报告生成完成，总字数: {final_report['word_count']}")

            # Phase 5: 转换为HTML格式（如果需要）
            html_content = None
            if output_format == 'html':
                logger.info(f"[{self.name}] Phase 5: 转换为HTML格式")
                html_content = await self._convert_to_html(
                    final_report, query, html_config or {}
                )

            return {
                "report": final_report,
                "html_content": html_content,
                "outline": outline,
                "section_details": optimized_sections,
                "output_format": output_format,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"[{self.name}] 报告生成失败: {e}")
            return {
                "report": None,
                "status": "error",
                "error": str(e)
            }

    async def _parallel_section_writing(
        self,
        sections: List[Dict[str, Any]],
        available_content: List[Dict[str, Any]],
        query: str,
        report_type: str
    ) -> List[Dict[str, Any]]:
        """并行写作所有段落"""

        logger.info(f"[{self.name}] 开始并行写作 {len(sections)} 个段落")

        # 创建生成任务
        tasks = []
        for index, section in enumerate(sections):
            previous_requirements = sections[index - 1].get("requirements", "") if index > 0 else ""
            tasks.append(
                self._generate_single_section(
                    index=index,
                    section=section,
                    previous_requirements=previous_requirements,
                    available_content=available_content,
                    query=query,
                    report_type=report_type
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        section_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[{self.name}] 段落 {i+1} 生成失败: {result}")
                section_results.append({
                    "section_id": i + 1,
                    "title": sections[i].get("title", f"Section {i+1}"),
                    "content": "",
                    "confidence": 0.0,
                    "status": "error",
                    "error": str(result),
                    "visualizations": []
                })
            else:
                section_results.append(result)

        logger.info(f"[{self.name}] 段落生成完成")
        return section_results

    async def _generate_single_section(
        self,
        index: int,
        section: Dict[str, Any],
        previous_requirements: str,
        available_content: List[Dict[str, Any]],
        query: str,
        report_type: str
    ) -> Dict[str, Any]:
        """
        生成单个段落，包含文本撰写与可视化识别（若启用）
        """

        context = {
            "query": query,
            "report_type": report_type,
            "previous_section": previous_requirements
        }

        writer_result = await self.section_writer.write_section(
            section,
            available_content,
            context
        )

        writer_result.setdefault("section_id", section.get("id", index + 1))
        writer_result.setdefault("title", section.get("title", f"Section {index + 1}"))
        writer_result.setdefault("visualizations", [])

        if (
            self.enable_visualization
            and writer_result.get("content")
            and not writer_result.get("visualizations")
        ):
            viz_response = await self.data_visualizer.process({
                "content": writer_result.get("content", ""),
                "title": writer_result.get("title", "")
            })

            if viz_response.get("status") == "success" and viz_response.get("visualizations"):
                writer_result["visualizations"] = viz_response["visualizations"]

        return writer_result

    async def _iterative_optimization(
        self,
        section_results: List[Dict[str, Any]],
        section_requirements: List[Dict[str, Any]],
        available_sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """迭代评估和优化段落"""

        logger.info(f"[{self.name}] 开始迭代优化")

        optimized = []

        for section_result in section_results:
            section_id = section_result.get("section_id")
            logger.info(f"[{self.name}] 优化段落 {section_id}")

            # 找到对应的要求
            requirements = next(
                (r for r in section_requirements if r.get("id") == section_id),
                {}
            )

            # 迭代优化
            iteration = 0
            current_result = section_result

            while iteration < self.max_iterations:
                # 评估
                evaluation = await self.section_evaluator.evaluate_section(
                    current_result, requirements, available_sources
                )

                # 检查是否通过
                if evaluation["passed"]:
                    logger.info(
                        f"[{self.name}] 段落 {section_id} 通过评估 "
                        f"(置信度: {evaluation['confidence']:.2f})"
                    )
                    current_result["evaluation"] = evaluation
                    break

                # 未通过，根据建议采取行动
                recommendation = evaluation["recommendation"]
                action = recommendation.get("action")

                logger.info(
                    f"[{self.name}] 段落 {section_id} 需要优化 "
                    f"(动作: {action}, 迭代: {iteration + 1}/{self.max_iterations})"
                )

                if action == "need_more_content":
                    # 需要补充内容
                    logger.info(f"[{self.name}] 段落 {section_id} 需要补充信息")
                    # TODO: 集成 ContentSearcher 补充内容
                    # 暂时直接重写
                    current_result = await self.section_writer.rewrite_section(
                        current_result,
                        recommendation.get("suggestions", [])
                    )

                elif action == "need_rewrite":
                    # 需要重写
                    logger.info(f"[{self.name}] 段落 {section_id} 需要重写")
                    current_result = await self.section_writer.rewrite_section(
                        current_result,
                        recommendation.get("suggestions", [])
                    )

                iteration += 1

            # 达到最大迭代次数
            if iteration >= self.max_iterations and not evaluation.get("passed"):
                logger.warning(
                    f"[{self.name}] 段落 {section_id} 达到最大迭代次数，"
                    f"置信度: {evaluation['confidence']:.2f}"
                )
                current_result["warnings"] = [
                    f"质量阈值未达到 (置信度: {evaluation['confidence']:.2f})"
                ]
                current_result["evaluation"] = evaluation

            optimized.append(current_result)

        passed_count = sum(
            1 for s in optimized
            if s.get("evaluation", {}).get("passed", False)
        )

        logger.info(
            f"[{self.name}] 迭代优化完成，"
            f"{passed_count}/{len(optimized)} 个段落通过质量阈值"
        )

        return optimized

    async def _assemble_report(
        self,
        outline: Dict[str, Any],
        sections: List[Dict[str, Any]],
        query: str,
        report_type: str
    ) -> Dict[str, Any]:
        """组装最终报告"""

        logger.info(f"[{self.name}] 开始组装最终报告")

        # 排序段落
        sections_sorted = sorted(sections, key=lambda x: x.get("section_id", 0))

        # 构建报告内容
        report_parts = []

        # 标题
        title = outline.get("title", "分析报告")
        report_parts.append(f"# {title}\n")

        # 元数据
        from datetime import datetime
        report_parts.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_parts.append(f"**查询**: {query}")
        report_parts.append(f"**报告类型**: {report_type}\n")
        report_parts.append("---\n")

        # 各段落内容
        section_entries: List[Dict[str, Any]] = []

        for section in sections_sorted:
            section_id = section.get("section_id")
            title = section.get("title")
            original_content = section.get("content", "")
            clean_content = self._clean_section_content(original_content, title)
            confidence = section.get("evaluation", {}).get("confidence", 0.0)
            images = section.get("images", [])

            report_parts.append(f"\n## {section_id}. {title}\n")
            report_parts.append(clean_content)

            # 插入章节配图（如果有）
            if images and not section.get("images_inserted"):
                from ...utils.image_processor import ImageProcessor
                image_markdown = ImageProcessor._generate_image_gallery(
                    images, title=f"{title} - 配图"
                )
                report_parts.append(f"\n\n{image_markdown}\n")

            # 如果置信度不足，添加警告
            if confidence < self.confidence_threshold:
                report_parts.append(
                    f"\n\n> ⚠️ 本段质量置信度较低 ({confidence:.2f})，建议人工review\n"
                )

            section_entries.append({
                "id": section_id,
                "title": title,
                "content": clean_content,
                "content_html": self._render_section_html(clean_content),
                "confidence": confidence,
                "visualizations": section.get("visualizations", []),
                "level": 2
            })

        # 参考来源
        report_parts.append("\n\n---\n")
        report_parts.append("\n## 📚 参考来源\n")

        all_sources = set()
        for section in sections:
            sources = section.get("sources_used", [])
            all_sources.update(sources)

        for i, source in enumerate(sorted(all_sources), 1):
            if source:
                report_parts.append(f"{i}. {source}\n")

        # 生成元数据
        report_parts.append("\n\n---\n")
        report_parts.append("\n## 📊 报告元数据\n")

        total_words = sum(len(s.get("content", "")) for s in sections)
        avg_confidence = sum(
            s.get("evaluation", {}).get("confidence", 0.0) for s in sections
        ) / len(sections) if sections else 0.0

        report_parts.append(f"- **总字数**: {total_words}\n")
        report_parts.append(f"- **段落数**: {len(sections)}\n")
        report_parts.append(f"- **平均置信度**: {avg_confidence:.2f}\n")
        report_parts.append(f"- **参考来源**: {len(all_sources)} 个\n")

        # 合并报告
        full_content = "".join(report_parts)

        report = {
            "title": title,
            "content": full_content,
            "type": report_type,
            "sections": section_entries,
            "metadata": {
                "query": query,
                "report_type": report_type,
                "generation_time": datetime.now().isoformat(),
                "total_words": total_words,
                "section_count": len(sections),
                "average_confidence": round(avg_confidence, 2),
                "sources_count": len(all_sources)
            }
        }

        # 添加字数统计
        report["word_count"] = total_words

        logger.info(f"[{self.name}] 报告组装完成，总字数: {total_words}")

        return report

    async def _convert_to_html(
        self,
        report: Dict[str, Any],
        query: str,
        html_config: Dict[str, Any]
    ) -> str:
        """将Markdown报告转换为HTML"""
        try:
            from ..html import DocumentHTMLAgent

            # 获取HTML配置
            template = html_config.get('template', 'academic')
            theme = html_config.get('theme', 'light')

            # 创建HTML转换智能体
            html_agent = DocumentHTMLAgent()

            # 准备元数据（包含sections以便直接渲染可视化）
            metadata = {
                'title': report.get('title', query),
                'author': 'XunLong AI',
                'date': report.get('metadata', {}).get('generation_time', ''),
                'keywords': [],  # 可以从报告中提取关键词
                'sections': report.get('sections', []),  # 传递sections以保留visualizations
                'stats': {
                    'words': report.get('word_count', 0),
                    'paragraphs': report.get('metadata', {}).get('section_count', 0)
                }
            }

            # 转换为HTML
            html_content = html_agent.convert_to_html(
                content=report.get('content', ''),
                metadata=metadata,
                template=template,
                theme=theme
            )

            logger.info(f"[{self.name}] HTML转换完成，使用模板: {template}, 主题: {theme}")
            return html_content

        except Exception as e:
            logger.error(f"[{self.name}] HTML转换失败: {e}")
            # 返回原始Markdown
            return report.get('content', '')

    async def _add_visualizations(
        self,
        sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        为段落添加数据可视化

        Args:
            sections: 段落列表

        Returns:
            增强后的段落列表
        """
        if not self.enable_visualization:
            return sections

        pending_indices: List[int] = []
        tasks = []

        for idx, section in enumerate(sections):
            if not section.get("content"):
                continue
            if section.get("visualizations"):
                continue

            tasks.append(self.data_visualizer.process({
                "content": section.get("content", ""),
                "title": section.get("title", "")
            }))
            pending_indices.append(idx)

        if not tasks:
            return sections

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, result in zip(pending_indices, results):
            if isinstance(result, Exception):
                logger.warning(f"[{self.name}] 可视化生成失败: {result}")
                continue

            if result.get("status") == "success" and result.get("visualizations"):
                sections[idx]["visualizations"] = result["visualizations"]
                viz_count = len(result["visualizations"])
                logger.info(
                    f"[{self.name}] 为段落 '{sections[idx].get('title', '')}' 添加了 {viz_count} 个可视化 "
                    f"({sum(1 for v in result['visualizations'] if v['type'] == 'table')} 表格, "
                    f"{sum(1 for v in result['visualizations'] if v['type'] == 'chart')} 图表)"
                )

        return sections

    def _clean_section_content(self, content: str, section_title: Optional[str]) -> str:
        """移除章节文本中冗余的标题或重复前缀"""

        if not content:
            return ""

        lines = content.splitlines()
        cleaned_lines: List[str] = []
        skip_heading = True
        normalized_title = re.sub(r"\s+", " ", section_title or "").strip().lower()

        for line in lines:
            stripped = line.strip()

            if skip_heading:
                if not stripped:
                    continue  # 跳过开头空行

                is_markdown_heading = stripped.startswith('#')
                is_numbered_heading = bool(re.match(r'^\d+(\.\d+)*\s+', stripped))
                normalized_line = re.sub(r"\s+", " ", stripped.strip('#').strip()).lower()
                matches_title = normalized_title and normalized_line.startswith(normalized_title)

                if is_markdown_heading or is_numbered_heading or matches_title:
                    skip_heading = False
                    continue

                skip_heading = False

            cleaned_lines.append(line)

        cleaned = '\n'.join(cleaned_lines).strip()
        return cleaned or content

    def _render_section_html(self, content: str) -> str:
        """将章节Markdown转换为HTML片段"""

        if not content:
            return ""

        if markdown:
            return markdown.markdown(
                content,
                extensions=['extra', 'codehilite', 'toc', 'tables']
            )

        # 简单降级处理
        escaped = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return '<p>' + escaped.replace('\n\n', '</p><p>').replace('\n', '<br>') + '</p>'

    async def _add_images_to_sections(
        self,
        sections: List[Dict[str, Any]],
        images_per_section: int = 2,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        为章节添加配图

        Args:
            sections: 章节列表
            images_per_section: 每个章节的配图数量

        Returns:
            增强后的章节列表（包含图片）
        """
        enhanced_sections = []

        logger.info(f"[{self.name}] 暂停章节配图流程，直接返回原始章节内容")
        enhanced_sections.extend(sections)
        return enhanced_sections

    def get_status(self) -> Dict[str, Any]:
        """获取协调器状态"""
        return {
            "name": self.name,
            "max_iterations": self.max_iterations,
            "confidence_threshold": self.confidence_threshold,
            "enable_visualization": self.enable_visualization,
            "agents": {
                "outline_generator": self.outline_generator.name,
                "section_writer": self.section_writer.name,
                "section_evaluator": self.section_evaluator.name,
                "data_visualizer": self.data_visualizer.name
            }
        }
