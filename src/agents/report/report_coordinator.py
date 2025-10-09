"""
 - 
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
    """ - """

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
        self.name = ""

        # 
        self.outline_generator = OutlineGenerator(llm_manager, prompt_manager)
        self.section_writer = SectionWriter(llm_manager, prompt_manager)
        self.section_evaluator = SectionEvaluator(
            llm_manager, prompt_manager, confidence_threshold
        )
        self.data_visualizer = DataVisualizer(llm_manager, prompt_manager)

        # 
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
        project_id: Optional[str] = None,
        refined_subtasks: Optional[List[Dict[str, Any]]] = None  # NEW parameter
    ) -> Dict[str, Any]:
        """


        Args:
            query:
            search_results:
            synthesis_results:
            report_type:
            output_format:  ('md'  'html')
            html_config: HTML {'template': 'academic', 'theme': 'light'}
            refined_subtasks: NEW -
        """

        logger.info(f"[{self.name}]  (: {report_type}, : {output_format})")

        # NEW: Prepare context with refined subtasks if available
        has_refined = refined_subtasks and len(refined_subtasks) > 0
        if has_refined:
            logger.info(f"[{self.name}]  {len(refined_subtasks)} ")
            # Build a rich context from refined subtasks
            available_content = self._prepare_refined_content(refined_subtasks, search_results)
        else:
            logger.info(f"[{self.name}] ")
            available_content = search_results

        try:
            # Phase 1:
            logger.info(f"[{self.name}] Phase 1: ")
            outline_result = await self.outline_generator.generate_outline(
                query, available_content, synthesis_results, report_type, refined_subtasks
            )

            if outline_result["status"] != "success":
                raise Exception("")

            outline = outline_result["outline"]
            sections = outline["sections"]

            logger.info(f"[{self.name}]  {len(sections)} ")

            # Phase 2:
            logger.info(f"[{self.name}] Phase 2:  {len(sections)} ")
            section_results = await self._parallel_section_writing(
                sections, available_content, query, report_type, refined_subtasks
            )

            # Phase 3:
            logger.info(f"[{self.name}] Phase 3: ")
            optimized_sections = await self._iterative_optimization(
                section_results, sections, available_content
            )

            # Phase 3.5: 
            if self.enable_visualization:
                logger.info(f"[{self.name}] Phase 3.5: ")
                optimized_sections = await self._add_visualizations(optimized_sections)

            # Phase 3.6: 
            if (
                self.enable_images
                and self.image_searcher
                and self.image_searcher.is_available()
                and not all(section.get("images_inserted") for section in optimized_sections)
            ):
                logger.info(f"[{self.name}] Phase 3.6: ")
                optimized_sections = await self._add_images_to_sections(
                    optimized_sections,
                    project_id=project_id
                )

            # Phase 4: 
            logger.info(f"[{self.name}] Phase 4: ")
            final_report = await self._assemble_report(
                outline, optimized_sections, query, report_type
            )

            logger.info(f"[{self.name}] : {final_report['word_count']}")

            # Phase 5: HTML
            html_content = None
            if output_format == 'html':
                logger.info(f"[{self.name}] Phase 5: HTML")
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
            logger.error(f"[{self.name}] : {e}")
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
        report_type: str,
        refined_subtasks: Optional[List[Dict[str, Any]]] = None  # NEW
    ) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""

        logger.info(f"[{self.name}]  {len(sections)} ")

        # NEW: Check if we have refined content
        has_refined = any(item.get("is_refined") for item in available_content) if available_content else False
        if has_refined:
            logger.info(f"[{self.name}] ")

        # 
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
                logger.error(f"[{self.name}]  {i+1} : {result}")
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

        logger.info(f"[{self.name}] ")
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
        """TODO: Add docstring."""

        logger.info(f"[{self.name}] ")

        optimized = []

        for section_result in section_results:
            section_id = section_result.get("section_id")
            logger.info(f"[{self.name}]  {section_id}")

            # 
            requirements = next(
                (r for r in section_requirements if r.get("id") == section_id),
                {}
            )

            # 
            iteration = 0
            current_result = section_result

            while iteration < self.max_iterations:
                # 
                evaluation = await self.section_evaluator.evaluate_section(
                    current_result, requirements, available_sources
                )

                # 
                if evaluation["passed"]:
                    logger.info(
                        f"[{self.name}]  {section_id}  "
                        f"(: {evaluation['confidence']:.2f})"
                    )
                    current_result["evaluation"] = evaluation
                    break

                # 
                recommendation = evaluation["recommendation"]
                action = recommendation.get("action")

                logger.info(
                    f"[{self.name}]  {section_id}  "
                    f"(: {action}, : {iteration + 1}/{self.max_iterations})"
                )

                if action == "need_more_content":
                    # 
                    logger.info(f"[{self.name}]  {section_id} ")
                    # TODO:  ContentSearcher 
                    # 
                    current_result = await self.section_writer.rewrite_section(
                        current_result,
                        recommendation.get("suggestions", [])
                    )

                elif action == "need_rewrite":
                    # 
                    logger.info(f"[{self.name}]  {section_id} ")
                    current_result = await self.section_writer.rewrite_section(
                        current_result,
                        recommendation.get("suggestions", [])
                    )

                iteration += 1

            # 
            if iteration >= self.max_iterations and not evaluation.get("passed"):
                logger.warning(
                    f"[{self.name}]  {section_id} "
                    f": {evaluation['confidence']:.2f}"
                )
                current_result["warnings"] = [
                    f" (: {evaluation['confidence']:.2f})"
                ]
                current_result["evaluation"] = evaluation

            optimized.append(current_result)

        passed_count = sum(
            1 for s in optimized
            if s.get("evaluation", {}).get("passed", False)
        )

        logger.info(
            f"[{self.name}] "
            f"{passed_count}/{len(optimized)} "
        )

        return optimized

    async def _assemble_report(
        self,
        outline: Dict[str, Any],
        sections: List[Dict[str, Any]],
        query: str,
        report_type: str
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        logger.info(f"[{self.name}] ")

        # 
        sections_sorted = sorted(sections, key=lambda x: x.get("section_id", 0))

        # 
        report_parts = []

        # 
        title = outline.get("title", "")
        report_parts.append(f"# {title}\n")

        # 
        from datetime import datetime
        report_parts.append(f"\n****: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_parts.append(f"****: {query}")
        report_parts.append(f"****: {report_type}\n")
        report_parts.append("---\n")

        # 
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

            # 
            if images and not section.get("images_inserted"):
                from ...utils.image_processor import ImageProcessor
                image_markdown = ImageProcessor._generate_image_gallery(
                    images, title=f"{title} - "
                )
                report_parts.append(f"\n\n{image_markdown}\n")

            # 
            if confidence < self.confidence_threshold:
                report_parts.append(
                    f"\n\n>   ({confidence:.2f})review\n"
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

        # 
        report_parts.append("\n\n---\n")
        report_parts.append("\n##  \n")

        all_sources = set()
        for section in sections:
            sources = section.get("sources_used", [])
            all_sources.update(sources)

        for i, source in enumerate(sorted(all_sources), 1):
            if source:
                report_parts.append(f"{i}. {source}\n")

        # 
        report_parts.append("\n\n---\n")
        report_parts.append("\n##  \n")

        total_words = sum(len(s.get("content", "")) for s in sections)
        avg_confidence = sum(
            s.get("evaluation", {}).get("confidence", 0.0) for s in sections
        ) / len(sections) if sections else 0.0

        report_parts.append(f"- ****: {total_words}\n")
        report_parts.append(f"- ****: {len(sections)}\n")
        report_parts.append(f"- ****: {avg_confidence:.2f}\n")
        report_parts.append(f"- ****: {len(all_sources)} \n")

        # 
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

        # 
        report["word_count"] = total_words

        logger.info(f"[{self.name}] : {total_words}")

        return report

    async def _convert_to_html(
        self,
        report: Dict[str, Any],
        query: str,
        html_config: Dict[str, Any]
    ) -> str:
        """MarkdownHTML"""
        try:
            from ..html import DocumentHTMLAgent

            # HTML - Use enhanced professional template by default
            template = html_config.get('template', 'enhanced_professional')
            theme = html_config.get('theme', 'light')

            # HTML
            html_agent = DocumentHTMLAgent()

            # sections
            metadata = {
                'title': report.get('title', query),
                'author': 'XunLong AI',
                'date': report.get('metadata', {}).get('generation_time', ''),
                'keywords': [],  # 
                'sections': report.get('sections', []),  # sectionsvisualizations
                'stats': {
                    'words': report.get('word_count', 0),
                    'paragraphs': report.get('metadata', {}).get('section_count', 0)
                }
            }

            # HTML
            html_content = html_agent.convert_to_html(
                content=report.get('content', ''),
                metadata=metadata,
                template=template,
                theme=theme
            )

            logger.info(f"[{self.name}] HTML: {template}, : {theme}")
            return html_content

        except Exception as e:
            logger.error(f"[{self.name}] HTML: {e}")
            # Re-raise the exception instead of returning Markdown as HTML
            raise Exception(f"Failed to convert to HTML: {e}") from e

    async def _add_visualizations(
        self,
        sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        

        Args:
            sections: 

        Returns:
            
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
                logger.warning(f"[{self.name}] : {result}")
                continue

            if result.get("status") == "success" and result.get("visualizations"):
                sections[idx]["visualizations"] = result["visualizations"]
                viz_count = len(result["visualizations"])
                logger.info(
                    f"[{self.name}]  '{sections[idx].get('title', '')}'  {viz_count}  "
                    f"({sum(1 for v in result['visualizations'] if v['type'] == 'table')} , "
                    f"{sum(1 for v in result['visualizations'] if v['type'] == 'chart')} )"
                )

        return sections

    def _clean_section_content(self, content: str, section_title: Optional[str]) -> str:
        """TODO: Add docstring."""

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
                    continue  # 

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
        """MarkdownHTML"""

        if not content:
            return ""

        if markdown:
            return markdown.markdown(
                content,
                extensions=['extra', 'codehilite', 'toc', 'tables']
            )

        # 
        escaped = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return '<p>' + escaped.replace('\n\n', '</p><p>').replace('\n', '<br>') + '</p>'

    async def _add_images_to_sections(
        self,
        sections: List[Dict[str, Any]],
        images_per_section: int = 2,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        

        Args:
            sections: 
            images_per_section: 

        Returns:
            
        """
        enhanced_sections = []

        logger.info(f"[{self.name}] ")
        enhanced_sections.extend(sections)
        return enhanced_sections

    def _prepare_refined_content(
        self,
        refined_subtasks: List[Dict[str, Any]],
        raw_search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        NEW METHOD: Prepare enriched content from refined subtasks.
        Each item combines the refined synthesis with original search metadata.
        """
        enriched_content = []

        for subtask in refined_subtasks:
            # Create a rich content item from refined subtask
            enriched_item = {
                # Core refined content
                "title": subtask.get("subtask_title", ""),
                "content": subtask.get("refined_content", ""),
                "subtask_id": subtask.get("subtask_id", ""),

                # Analysis metadata
                "key_points": subtask.get("key_points", []),
                "analysis_summary": subtask.get("analysis", {}).get("analysis_summary", ""),
                "quality_score": subtask.get("analysis", {}).get("quality_score", 0.5),

                # Original sources for reference
                "sources": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("snippet", "")
                    }
                    for r in subtask.get("raw_results", [])[:5]
                ],

                # Metadata
                "is_refined": True,
                "subtask_index": subtask.get("subtask_index", 0),
                "metadata": subtask.get("metadata", {})
            }

            enriched_content.append(enriched_item)

        logger.info(f"[{self.name}]  {len(enriched_content)} ")

        # Also include raw search results for fallback/additional context
        for result in raw_search_results:
            if not result.get("subtask_id"):  # Only add items not from subtasks
                enriched_content.append({
                    **result,
                    "is_refined": False
                })

        return enriched_content

    def get_status(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
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
