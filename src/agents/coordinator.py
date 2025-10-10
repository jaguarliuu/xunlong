""" - """

import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
    logger.info("LangGraphagent")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    logger.warning(f"LangGraph: {e}")
    
# 
class BaseMessage:
    def __init__(self, content: str):
        self.content = content

class AIMessage(BaseMessage):
    pass

class HumanMessage(BaseMessage):
    pass

from ..llm import LLMManager, PromptManager
from ..pipeline import DeepSearchPipeline
from .base import BaseAgent
from .task_decomposer import TaskDecomposer as TaskDecomposerAgent
from .deep_searcher import DeepSearcher as DeepSearcherAgent
from .query_optimizer import QueryOptimizerAgent
from .search_analyzer import SearchAnalyzerAgent
from .content_synthesizer import ContentSynthesizerAgent
from .report_generator import ReportGenerator as ReportGeneratorAgent
from .content_evaluator import ContentEvaluator
from ..tools.time_tool import time_tool
try:
    from src.storage import SearchStorage
except ModuleNotFoundError:
    try:
        from storage import SearchStorage
    except ModuleNotFoundError:
        from ..storage import SearchStorage
from .report import ReportCoordinator
from .output_type_detector import OutputTypeDetector
from .fiction import FictionElementsDesigner, FictionOutlineGenerator
from .ppt import PPTCoordinator


class DeepSearchState(TypedDict):
    """TODO: Add docstring."""
    query: str
    context: Dict[str, Any]
    messages: List[Dict[str, Any]]
    current_step: str

    # 
    user_document: Optional[str]
    user_document_meta: Dict[str, Any]
    time_context: Dict[str, Any]

    # 
    output_type: str  # "report", "fiction", "ppt"
    output_type_confidence: float

    # 
    task_analysis: Dict[str, Any]
    decomposition_status: str

    #
    search_results: List[Dict[str, Any]]
    search_status: str
    total_results: int
    refined_subtasks: List[Dict[str, Any]]  # NEW: Refined content organized by subtask

    #
    analysis_results: Dict[str, Any]
    analysis_status: str

    # 
    synthesis_results: Dict[str, Any]
    synthesis_status: str

    # 
    fiction_requirements: Dict[str, Any]  # 
    fiction_elements: Dict[str, Any]  # 
    fiction_outline: Dict[str, Any]  # 

    # PPT
    ppt_config: Dict[str, Any]  # PPT
    ppt_outline: Dict[str, Any]  # PPT
    ppt_data: Dict[str, Any]  # PPT

    # 
    final_report: Dict[str, Any]
    report_status: str

    # 
    errors: List[str]

    # 
    workflow_id: str
    timestamp: str


@dataclass
class DeepSearchConfig:
    """TODO: Add docstring."""
    max_iterations: int = 10
    timeout_seconds: int = 600  # 
    enable_parallel: bool = True
    retry_attempts: int = 3
    llm_config_name: str = "default"
    search_depth: str = "deep"  # surface, medium, deep
    max_search_results: int = 20


class DeepSearchCoordinator:
    """ - """
    
    def __init__(
        self,
        config: Optional[DeepSearchConfig] = None,
        llm_manager: Optional[LLMManager] = None,
        prompt_manager: Optional[PromptManager] = None,
        storage: Optional[SearchStorage] = None
    ):
        self.config = config or DeepSearchConfig()
        self.llm_manager = llm_manager or LLMManager()
        self.prompt_manager = prompt_manager
        self.pipeline = DeepSearchPipeline()
        self.storage = storage or SearchStorage()

        # 
        self.agents = {
            "task_decomposer": TaskDecomposerAgent(self.llm_manager, self.prompt_manager),
            "deep_searcher": DeepSearcherAgent(self.llm_manager, self.prompt_manager),
            "query_optimizer": QueryOptimizerAgent(self.llm_manager, self.prompt_manager),
            "search_analyzer": SearchAnalyzerAgent(self.llm_manager, self.prompt_manager),
            "content_synthesizer": ContentSynthesizerAgent(self.llm_manager, self.prompt_manager),
            "report_generator": ReportGeneratorAgent(self.llm_manager, self.prompt_manager),
            "content_evaluator": ContentEvaluator(self.llm_manager, self.prompt_manager)
        }

        #
        self.report_coordinator = ReportCoordinator(
            self.llm_manager,
            self.prompt_manager,
            max_iterations=3,
            confidence_threshold=0.7,
            enable_images=False  # Disabled - saves time and network resources
        )

        # 
        self.output_type_detector = OutputTypeDetector(self.llm_manager, self.prompt_manager)

        # 
        self.fiction_elements_designer = FictionElementsDesigner(self.llm_manager, self.prompt_manager)
        self.fiction_outline_generator = FictionOutlineGenerator(self.llm_manager, self.prompt_manager)
        
        # LangGraph
        if LANGGRAPH_AVAILABLE:
            try:
                self.workflow = self._create_langgraph_workflow()
                if self.workflow:
                    logger.info("LangGraph")
                else:
                    logger.warning("LangGraph")
                    self.workflow = None
            except Exception as e:
                logger.error(f"LangGraph: {e}")
                self.workflow = None
        else:
            self.workflow = None
            logger.info("LangGraph")
        
        logger.info("")
    
    def _create_langgraph_workflow(self):
        """LangGraph"""
        if not LANGGRAPH_AVAILABLE:
            logger.warning("LangGraph")
            return None
        
        try:
            logger.info("LangGraph...")
            
            # 
            workflow = StateGraph(DeepSearchState)

            # 
            workflow.add_node("output_type_detector", self._output_type_detector_node)
            workflow.add_node("task_decomposer", self._task_decomposer_node)
            workflow.add_node("deep_searcher", self._deep_searcher_node)
            workflow.add_node("search_analyzer", self._search_analyzer_node)
            workflow.add_node("content_synthesizer", self._content_synthesizer_node)
            workflow.add_node("report_generator", self._report_generator_node)
            workflow.add_node("fiction_elements_designer", self._fiction_elements_designer_node)
            workflow.add_node("fiction_outline_generator", self._fiction_outline_generator_node)
            workflow.add_node("fiction_writer", self._fiction_writer_node)
            workflow.add_node("ppt_generator", self._ppt_generator_node)

            # 
            workflow.set_entry_point("output_type_detector")

            #  - 
            workflow.add_conditional_edges(
                "output_type_detector",
                self._route_by_output_type,
                {
                    "report": "task_decomposer",
                    "fiction": "fiction_elements_designer",
                    "ppt": "task_decomposer"
                }
            )

            # 
            workflow.add_conditional_edges(
                "task_decomposer",
                self._route_after_task_decomposer,
                {
                    "deep_searcher": "deep_searcher"
                }
            )

            #  - 
            workflow.add_conditional_edges(
                "deep_searcher",
                self._route_after_deep_search,
                {
                    "search_analyzer": "search_analyzer",
                    "fiction_outline_generator": "fiction_outline_generator"
                }
            )

            #  - PPT
            workflow.add_conditional_edges(
                "search_analyzer",
                self._route_after_search_analyzer,
                {
                    "content_synthesizer": "content_synthesizer",
                    "ppt_generator": "ppt_generator"
                }
            )

            # 
            workflow.add_edge("content_synthesizer", "report_generator")

            # 
            workflow.add_edge("report_generator", END)
            workflow.add_edge("ppt_generator", END)

            # 
            workflow.add_edge("fiction_elements_designer", "task_decomposer")  # 
            workflow.add_edge("fiction_outline_generator", "fiction_writer")
            workflow.add_edge("fiction_writer", END)
            
            # 
            compiled_workflow = workflow.compile()
            logger.info("LangGraph")
            
            return compiled_workflow
            
        except Exception as e:
            logger.error(f"LangGraph: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _task_decomposer_node(self, state: DeepSearchState) -> DeepSearchState:
        """TODO: Add docstring."""
        try:
            logger.info("...")

            # 
            context = state.get("context", {})
            context["output_type"] = state.get("output_type", "report")

            # 
            if context["output_type"] == "fiction":
                context["fiction_requirements"] = state.get("fiction_requirements", {})
                context["fiction_elements"] = state.get("fiction_elements", {})

            result = await self.agents["task_decomposer"].process({
                "query": state["query"],
                "context": context
            })

            state["task_analysis"] = result.get("result", {})
            state["decomposition_status"] = result.get("status", "unknown")

            # 
            time_context = state["task_analysis"].get("time_context") if state.get("task_analysis") else None
            if time_context:
                state["time_context"] = time_context

            subtasks_count = len(state["task_analysis"].get("subtasks", []))
            state["messages"].append({
                "role": "assistant",
                "content": f":  {subtasks_count} ",
                "agent": "task_decomposer"
            })

            state["current_step"] = "deep_searcher"

        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")
            state["decomposition_status"] = "failed"

        return state
    
    async def _deep_searcher_node(self, state: DeepSearchState) -> DeepSearchState:
        """TODO: Add docstring."""
        try:
            logger.info("...")
            
            task_analysis = state.get("task_analysis", {})
            subtasks = task_analysis.get("subtasks", [])
            
            if not subtasks:
                # 
                subtasks = [{
                    "id": "default_search",
                    "type": "search",
                    "title": "",
                    "search_queries": [state.get("query", "")],
                    "depth_level": self.config.search_depth
                }]
            
            all_search_results = []
            user_document = state.get("user_document")
            if user_document:
                doc_meta = state.get("user_document_meta", {})
                doc_title = doc_meta.get("filename") or ""
                doc_result = {
                    "url": doc_meta.get("source_path", "user://document"),
                    "title": doc_title,
                    "snippet": user_document[:200],
                    "content": user_document,
                    "full_content": user_document,
                    "content_length": len(user_document),
                    "search_query": state.get("query", ""),
                    "subtask_id": "user_document",
                    "subtask_title": "",
                    "extraction_time": datetime.now().isoformat(),
                    "extracted_time": datetime.now().strftime("%Y-%m-%d"),
                    "source": "user_document",
                    "rank": 0,
                    "images": [],
                    "image_count": 0,
                    "has_images": False,
                    "images_inserted": False,
                    "has_full_content": True,
                    "extraction_status": "user_document",
                    "document_meta": doc_meta
                }
                all_search_results.append(doc_result)

                state["messages"].append({
                    "role": "assistant",
                    "content": f"{doc_title}",
                    "agent": "document_loader"
                })
            
            # 
            for subtask in subtasks:
                if subtask.get("type") == "search":
                    logger.info(f": {subtask.get('title', 'Unknown')}")
                    
                    time_context = subtask.get("time_context") or state.get("time_context")

                    search_input = {
                        "query": state.get("query", ""),
                        "decomposition": {"subtasks": [subtask]},  # 
                        "context": state.get("context", {}),
                        "time_context": time_context
                    }

                    search_result = await self.agents["deep_searcher"].process(search_input)
                    logger.debug(f": status={search_result.get('status')}, keys={list(search_result.keys())}")

                    if search_result.get("status") == "success":
                        # result
                        result_data = search_result.get("result", {})
                        task_results = result_data.get("all_content", [])
                        refined_subtasks = result_data.get("refined_subtasks", [])  # NEW

                        logger.debug(f" {len(task_results)}  {len(refined_subtasks)} ")
                        if task_results:
                            logger.debug(f": {task_results[0]}")

                        all_search_results.extend(task_results)

                        # NEW: Store refined subtasks separately
                        if refined_subtasks:
                            if "refined_subtasks" not in state:
                                state["refined_subtasks"] = []
                            state["refined_subtasks"].extend(refined_subtasks)

                    #
                    await asyncio.sleep(1)
            
            # 
            if len(all_search_results) > self.config.max_search_results:
                all_search_results = all_search_results[:self.config.max_search_results]
            
            state["search_results"] = all_search_results
            state["search_status"] = "success" if all_search_results else "failed"
            state["total_results"] = len(all_search_results)
            
            state["messages"].append({
                "role": "assistant",
                "content": f":  {len(all_search_results)} ",
                "agent": "deep_searcher"
            })
            
            state["current_step"] = "search_analyzer"
            
        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")
            state["search_status"] = "failed"
            state["search_results"] = []
            state["total_results"] = 0
        
        return state
    
    async def _search_analyzer_node(self, state: DeepSearchState) -> DeepSearchState:
        """TODO: Add docstring."""
        try:
            logger.info("...")
            
            search_results = state.get("search_results", [])
            logger.info(f": {len(search_results)}")
            if search_results:
                logger.debug(f": {search_results[0]}")
            
            result = await self.agents["search_analyzer"].process({
                "query": state["query"],
                "search_results": search_results
            })
            
            state["analysis_results"] = result.get("result", {})
            state["analysis_status"] = result.get("status", "unknown")
            
            state["messages"].append({
                "role": "assistant",
                "content": f":  {len(state.get('search_results', []))} ",
                "agent": "search_analyzer"
            })
            
            state["current_step"] = "content_synthesizer"
            
        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")
            state["analysis_status"] = "failed"
        
        return state
    
    async def _content_synthesizer_node(self, state: DeepSearchState) -> DeepSearchState:
        """TODO: Add docstring."""
        try:
            logger.info("...")
            
            result = await self.agents["content_synthesizer"].process({
                "query": state["query"],
                "search_results": state.get("search_results", []),
                "analysis_results": state.get("analysis_results", {})
            })
            
            state["synthesis_results"] = result.get("result", {})
            state["synthesis_status"] = result.get("status", "unknown")
            
            state["messages"].append({
                "role": "assistant",
                "content": f"",
                "agent": "content_synthesizer"
            })
            
            state["current_step"] = "report_generator"
            
        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")
            state["synthesis_status"] = "failed"
        
        return state
    
    async def _report_generator_node(self, state: DeepSearchState) -> DeepSearchState:
        """TODO: Add docstring."""
        try:
            logger.info("...")

            query = state.get("query", "")
            search_results = state.get("search_results", [])
            synthesis_results = state.get("synthesis_results", {})

            # 
            task_analysis = state.get("task_analysis", {})
            report_type = task_analysis.get("report_type", "comprehensive")

            # HTML - Always generate HTML in addition to Markdown
            context = state.get("context", {})
            output_format = context.get("output_format", "html")  # Changed default to HTML
            html_config = {
                "template": context.get("html_template", "enhanced_professional"),  # Use enhanced template
                "theme": context.get("html_theme", "light")
            }

            # 
            # ID
            project_id = state.get("workflow_id")

            result = await self.report_coordinator.generate_report(
                query=query,
                search_results=search_results,
                synthesis_results=synthesis_results,
                report_type=report_type,
                output_format=output_format,
                html_config=html_config,
                project_id=project_id,  # ID
                refined_subtasks=state.get("refined_subtasks", [])  # NEW: Pass refined subtasks
            )

            if result["status"] == "success":
                state["final_report"] = {
                    "result": result,
                    "status": "success"
                }
                state["report_status"] = "success"

                report = result.get("report", {})
                word_count = report.get("word_count", 0)
                avg_confidence = report.get("metadata", {}).get("average_confidence", 0.0)

                state["messages"].append({
                    "role": "assistant",
                    "content": f":  {word_count}  (: {avg_confidence:.2f})",
                    "agent": "report_coordinator"
                })
            else:
                # 
                logger.warning("")

                report_input = {
                    "query": query,
                    "task_analysis": task_analysis,
                    "search_results": search_results,
                    "analysis_results": state.get("analysis_results", {}),
                    "synthesis_results": synthesis_results
                }

                fallback_result = await self.agents["report_generator"].process(report_input)

                state["final_report"] = fallback_result.get("result", {})
                state["report_status"] = fallback_result.get("status", "unknown")

                state["messages"].append({
                    "role": "assistant",
                    "content": "",
                    "agent": "report_generator"
                })

            state["current_step"] = "completed"

        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")
            state["report_status"] = "failed"

        return state

    async def _output_type_detector_node(self, state: DeepSearchState) -> DeepSearchState:
        """TODO: Add docstring."""
        try:
            logger.info("...")

            query = state.get("query", "")
            context = state.get("context", {})

            # CLI
            explicit_output_type = context.get("output_type")

            if explicit_output_type:
                # 
                output_type = explicit_output_type
                confidence = 1.0  # 100%
                logger.info(f": {output_type}")

                state["output_type"] = output_type
                state["output_type_confidence"] = confidence

                state["messages"].append({
                    "role": "assistant",
                    "content": f": {output_type}",
                    "agent": "output_type_detector"
                })

                # fiction
                if output_type == "fiction":
                    # fiction_requirements
                    if "fiction_requirements" in context:
                        fiction_requirements = context["fiction_requirements"]
                        logger.info(f": {fiction_requirements}")
                    else:
                        fiction_requirements = self.output_type_detector.extract_fiction_requirements(query)
                        logger.info(f": {fiction_requirements}")

                    state["fiction_requirements"] = fiction_requirements

                # pptPPT
                elif output_type == "ppt":
                    if "ppt_config" in context:
                        ppt_config = context["ppt_config"]
                        state["ppt_config"] = ppt_config
                        logger.info(f"PPT: style={ppt_config.get('style')}, slides={ppt_config.get('slides')}")
                    else:
                        # PPT
                        state["ppt_config"] = {
                            "style": "business",
                            "slides": 10,
                            "depth": "medium",
                            "theme": "default"
                        }
                        logger.info(f"PPT")

            else:
                # 
                logger.info("")

                detection_result = await self.output_type_detector.detect_output_type(query)

                output_type = detection_result.get("output_type", "report")
                confidence = detection_result.get("confidence", 0.0)

                state["output_type"] = output_type
                state["output_type_confidence"] = confidence

                logger.info(f": {output_type} (: {confidence:.2f})")

                state["messages"].append({
                    "role": "assistant",
                    "content": f": {output_type} (: {confidence:.2f})",
                    "agent": "output_type_detector"
                })

                # fiction
                if output_type == "fiction":
                    fiction_requirements = self.output_type_detector.extract_fiction_requirements(query)
                    state["fiction_requirements"] = fiction_requirements
                    logger.info(f": {fiction_requirements}")

        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")
            state["output_type"] = "report"  # 
            state["output_type_confidence"] = 0.5

        return state

    async def _fiction_elements_designer_node(self, state: DeepSearchState) -> DeepSearchState:
        """TODO: Add docstring."""
        try:
            logger.info("...")

            query = state.get("query", "")
            fiction_requirements = state.get("fiction_requirements", {})

            # 
            result = await self.fiction_elements_designer.design_elements(
                query=query,
                requirements=fiction_requirements,
                search_results=None  # 
            )

            if result["status"] == "success":
                state["fiction_elements"] = result["elements"]
                logger.info("")

                state["messages"].append({
                    "role": "assistant",
                    "content": f"",
                    "agent": "fiction_elements_designer"
                })
            else:
                state["errors"].append(f": {result.get('error', '')}")

        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")

        return state

    async def _fiction_outline_generator_node(self, state: DeepSearchState) -> DeepSearchState:
        """TODO: Add docstring."""
        try:
            logger.info("...")

            query = state.get("query", "")
            fiction_elements = state.get("fiction_elements", {})
            fiction_requirements = state.get("fiction_requirements", {})

            # 
            result = await self.fiction_outline_generator.generate_outline(
                query=query,
                elements=fiction_elements,
                requirements=fiction_requirements
            )

            if result["status"] == "success":
                state["fiction_outline"] = result["outline"]
                total_chapters = result.get("total_chapters", 0)
                logger.info(f" {total_chapters} ")

                state["messages"].append({
                    "role": "assistant",
                    "content": f" {total_chapters} ",
                    "agent": "fiction_outline_generator"
                })
            else:
                state["errors"].append(f": {result.get('error', '')}")

        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")

        return state

    async def _fiction_writer_node(self, state: DeepSearchState) -> DeepSearchState:
        """ - SectionWriter"""
        try:
            logger.info("...")

            query = state.get("query", "")
            fiction_outline = state.get("fiction_outline", {})
            fiction_elements = state.get("fiction_elements", {})
            search_results = state.get("search_results", [])
            synthesis_results = state.get("synthesis_results", {})

            chapters = fiction_outline.get("chapters", [])

            if not chapters:
                raise ValueError("")

            logger.info(f" {len(chapters)} ...")

            #  + 
            available_content = search_results.copy()
            if synthesis_results and synthesis_results.get("synthesis"):
                available_content.append({
                    "title": "",
                    "content": synthesis_results["synthesis"],
                    "source": "content_synthesizer"
                })

            # 
            write_tasks = []
            for i, chapter in enumerate(chapters):
                # 
                section_requirements = {
                    "id": chapter.get("id", i + 1),
                    "title": f"{chapter.get('id', i + 1)}: {chapter.get('title', '')}",
                    "requirements": self._build_chapter_writing_requirements(
                        chapter,
                        fiction_elements,
                        fiction_outline,
                        query
                    ),
                    "word_count": chapter.get("word_count", 800),
                    "importance": 0.8
                }

                # 
                context = None
                if i > 0:
                    context = {
                        "previous_section_title": f"{chapters[i-1].get('id', i)}: {chapters[i-1].get('title', '')}",
                        "previous_section_summary": chapters[i-1].get("writing_points", "")
                    }

                # section_writer
                task = self.report_coordinator.section_writer.write_section(
                    section=section_requirements,
                    available_content=available_content,
                    context=context
                )
                write_tasks.append(task)

            # 
            chapter_results = await asyncio.gather(*write_tasks, return_exceptions=True)

            # 
            fiction_content = f"# {fiction_outline.get('title', '')}\n\n"
            fiction_content += f"****: {fiction_outline.get('synopsis', '')}\n\n"
            fiction_content += "---\n\n"

            total_words = 0
            successful_chapters = 0

            for i, result in enumerate(chapter_results):
                if isinstance(result, Exception):
                    logger.error(f" {i+1} : {result}")
                    # 
                    chapter = chapters[i]
                    fiction_content += f"## {chapter['id']}: {chapter['title']}\n\n"
                    fiction_content += f"\n\n"
                    fiction_content += f"****: {chapter.get('writing_points', '')}\n\n"
                    fiction_content += "---\n\n"
                else:
                    # 
                    chapter_content = result.get("content", "")
                    chapter_title = chapters[i].get("title", f"{i+1}")

                    fiction_content += f"## {chapters[i]['id']}: {chapter_title}\n\n"
                    fiction_content += chapter_content + "\n\n"
                    fiction_content += "---\n\n"

                    total_words += len(chapter_content)
                    successful_chapters += 1

            # 
            report_data = {
                "title": fiction_outline.get("title", ""),
                "content": fiction_content,
                "word_count": total_words,
                "metadata": {
                    "type": "fiction",
                    "total_chapters": len(chapters),
                    "successful_chapters": successful_chapters,
                    "genre": state.get("fiction_requirements", {}).get("genre", ""),
                    "elements": fiction_elements
                }
            }

            # HTML
            html_content = None
            output_format = state.get("context", {}).get("output_format", "md")
            if output_format == "html":
                logger.info("HTML")
                html_content = await self._convert_fiction_to_html(
                    report_data,
                    state.get("context", {})
                )

            state["final_report"] = {
                "result": {
                    "report": report_data,
                    "html_content": html_content,
                    "output_format": output_format,
                    "status": "success"
                },
                "status": "success"
            }
            state["report_status"] = "success"

            logger.info(f" {len(chapters)}  {successful_chapters}  {total_words}")

            state["messages"].append({
                "role": "assistant",
                "content": f" {len(chapters)}  {successful_chapters}  {total_words}",
                "agent": "fiction_writer"
            })

        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")
            state["report_status"] = "failed"

        return state

    async def _ppt_generator_node(self, state: DeepSearchState) -> DeepSearchState:
        """PPT - V3"""
        try:
            logger.info("PPT (V3)...")

            query = state.get("query", "")
            search_results = state.get("search_results", [])
            ppt_config = state.get("ppt_config", {})

            # PPT
            ppt_coordinator = PPTCoordinator(self.llm_manager, self.prompt_manager)

            # output_dir (storage)
            from pathlib import Path
            output_dir = Path(self.storage.get_project_dir())

            # V3 -
            result = await ppt_coordinator.generate_ppt_v3(
                topic=query,
                search_results=search_results,
                ppt_config=ppt_config,
                output_dir=output_dir
            )

            if result["status"] == "success":
                state["ppt_data"] = {
                    "ppt_dir": result.get("ppt_dir"),
                    "total_slides": result.get("total_slides"),
                    "slide_files": result.get("slide_files"),
                    "index_page": result.get("index_page"),
                    "presenter_page": result.get("presenter_page")
                }

                # final_report - V3
                final_report_result = {
                    "ppt_dir": result.get("ppt_dir"),
                    "index_page": result.get("index_page"),
                    "presenter_page": result.get("presenter_page"),
                    "total_slides": result.get("total_slides"),
                    "output_format": "multi_html",  #
                    "slide_files": result.get("slide_files", [])
                }

                state["final_report"] = {
                    "result": final_report_result,
                    "status": "success"
                }
                state["report_status"] = "success"

                slide_count = result.get("total_slides", 0)
                logger.info(f"PPT {slide_count}  (V3)")
                logger.info(f": {result.get('index_page')}")

                state["messages"].append({
                    "role": "assistant",
                    "content": f"PPT {slide_count}  (V3)",
                    "agent": "ppt_generator"
                })
            else:
                raise Exception(result.get("error", "PPT"))

        except Exception as e:
            logger.error(f"PPT: {e}")
            import traceback
            traceback.print_exc()
            state["errors"].append(f"PPT: {e}")
            state["report_status"] = "failed"

        return state

    def _build_chapter_writing_requirements(
        self,
        chapter: Dict[str, Any],
        fiction_elements: Dict[str, Any],
        fiction_outline: Dict[str, Any],
        query: str
    ) -> str:
        """TODO: Add docstring."""

        # 
        characters = fiction_elements.get("characters", [])
        place = fiction_elements.get("place", {})
        theme = fiction_elements.get("theme", {})

        # 
        writing_points = chapter.get("writing_points", "")
        key_scenes = chapter.get("key_scenes", [])
        characters_involved = chapter.get("characters_involved", [])
        suspense = chapter.get("suspense", "")

        requirements = f"""# 

## 
{query}

## 
{writing_points}

## 
{', '.join(key_scenes) if key_scenes else ''}

## 
{', '.join(characters_involved) if characters_involved else ''}

## 
"""
        # 
        for char in characters:
            if char.get("name") in characters_involved:
                requirements += f"- **{char.get('name')}**: {char.get('occupation', '')}, {char.get('personality', '')}\n"

        requirements += f"""

## 
- ****: {place.get('main_location', '')}
- ****: {place.get('description', '')}

## 
- ****: {theme.get('core_theme', '')}
- ****: {theme.get('tone', '')}

## 
{suspense}

## 
1. ****: 
2. ****: 
3. ****: 
4. ****: 
5. ****: {chapter.get('word_count', 800)}
6. ****: 


- 
- 
- 
- 
"""

        return requirements

    def _route_by_output_type(self, state: DeepSearchState) -> str:
        """TODO: Add docstring."""
        output_type = state.get("output_type", "report")
        logger.info(f": {output_type} ")
        return output_type

    def _route_after_task_decomposer(self, state: DeepSearchState) -> str:
        """TODO: Add docstring."""
        return "deep_searcher"

    def _route_after_deep_search(self, state: DeepSearchState) -> str:
        """ - fiction"""
        output_type = state.get("output_type", "report")
        if output_type == "fiction":
            return "fiction_outline_generator"
        else:
            return "search_analyzer"

    def _route_after_search_analyzer(self, state: DeepSearchState) -> str:
        """ - reportppt"""
        output_type = state.get("output_type", "report")
        if output_type == "ppt":
            logger.info("PPT")
            return "ppt_generator"
        else:
            logger.info("")
            return "content_synthesizer"

    def _route_after_synthesis(self, state: DeepSearchState) -> str:
        """TODO: Add docstring."""
        output_type = state.get("output_type", "report")
        if output_type == "fiction":
            return "fiction_outline_generator"
        else:
            return "report_generator"

    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            # 
            project_id = self.storage.create_project(query)
            logger.info(f": {project_id}")

            # 
            workflow_id = f"deep_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            initial_state: DeepSearchState = {
                "query": query,
                "context": context or {},
                "messages": [{"role": "user", "content": query}],
                "current_step": "output_type_detector",
                "user_document": (context or {}).get("user_document"),
                "user_document_meta": (context or {}).get("user_document_meta", {}),
                "time_context": (context or {}).get("time_context", {}),

                # 
                "output_type": "report",
                "output_type_confidence": 0.0,

                # 
                "task_analysis": {},
                "decomposition_status": "pending",

                #
                "search_results": [],
                "search_status": "pending",
                "total_results": 0,
                "refined_subtasks": [],  # NEW

                #
                "analysis_results": {},
                "analysis_status": "pending",

                # 
                "synthesis_results": {},
                "synthesis_status": "pending",

                # 
                "fiction_requirements": {},
                "fiction_elements": {},
                "fiction_outline": {},

                # PPT
                "ppt_config": {},
                "ppt_outline": {},
                "ppt_data": {},

                # 
                "final_report": {},
                "report_status": "pending",

                # 
                "errors": [],

                # 
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat()
            }
            
            if LANGGRAPH_AVAILABLE and self.workflow:
                # LangGraph
                logger.info("LangGraph")
                final_state = await self.workflow.ainvoke(initial_state)
            else:
                # 
                logger.info("")
                final_state = await self._simple_deep_search_workflow(initial_state)
            
            # 
            if final_state["errors"]:
                status = "partial_success" if final_state.get("final_report") else "error"
            else:
                status = "success"

            # 
            self._save_search_results(final_state, query)

            return {
                "status": status,
                "workflow_id": workflow_id,
                "query": query,
                "messages": final_state["messages"],
                "execution_steps": self._extract_execution_steps(final_state),

                # 
                "task_analysis": final_state["task_analysis"],
                "search_results": final_state["search_results"],
                "analysis_results": final_state["analysis_results"],
                "synthesis_results": final_state["synthesis_results"],
                "final_report": final_state["final_report"],

                # 
                "statistics": {
                    "total_search_results": final_state["total_results"],
                    "subtasks_count": len(final_state["task_analysis"].get("subtasks", [])),
                    "execution_time": datetime.now().isoformat(),
                    "errors_count": len(final_state["errors"])
                },

                "errors": final_state["errors"],
                "project_id": project_id,
                "project_dir": str(self.storage.get_project_dir())
            }
            
        except Exception as e:
            logger.error(f": {e}")
            return {
                "status": "error",
                "workflow_id": f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "query": query,
                "error": str(e),
                "messages": [],
                "execution_steps": [],
                "task_analysis": {},
                "search_results": [],
                "analysis_results": {},
                "synthesis_results": {},
                "final_report": {},
                "statistics": {},
                "errors": [str(e)]
            }
    
    async def _simple_deep_search_workflow(self, state: DeepSearchState) -> DeepSearchState:
        """LangGraph"""
        try:
            # 1: 
            logger.info(" 1/6: ")
            state = await self._output_type_detector_node(state)

            output_type = state.get("output_type", "report")

            if output_type == "fiction":
                # 
                logger.info(" 2/6: ")
                state = await self._fiction_elements_designer_node(state)

                logger.info(" 3/6: ")
                state = await self._task_decomposer_node(state)

                logger.info(" 4/6: ")
                state = await self._deep_searcher_node(state)

                logger.info(" 5/6: ")
                state = await self._fiction_outline_generator_node(state)

                logger.info(" 6/6: ")
                state = await self._fiction_writer_node(state)

            elif output_type == "ppt":
                # PPT
                logger.info(" 2/5: ")
                state = await self._task_decomposer_node(state)

                logger.info(" 3/5: ")
                state = await self._deep_searcher_node(state)

                logger.info(" 4/5: ")
                state = await self._search_analyzer_node(state)

                logger.info(" 5/5: PPT")
                state = await self._ppt_generator_node(state)

            else:
                # 
                logger.info(" 2/6: ")
                state = await self._task_decomposer_node(state)

                logger.info(" 3/6: ")
                state = await self._deep_searcher_node(state)

                logger.info(" 4/6: ")
                state = await self._search_analyzer_node(state)

                logger.info(" 5/6: ")
                state = await self._content_synthesizer_node(state)

                logger.info(" 6/6: ")
                state = await self._report_generator_node(state)

            return state

        except Exception as e:
            logger.error(f": {e}")
            state["errors"].append(f": {e}")
            return state
    
    def _save_search_results(self, final_state: DeepSearchState, query: str):
        """TODO: Add docstring."""
        try:
            # 1. 
            if final_state.get("task_analysis"):
                self.storage.save_task_decomposition(final_state["task_analysis"])

            # 2.
            if final_state.get("search_results"):
                search_data = {
                    "all_content": final_state["search_results"],
                    "total_results": final_state.get("total_results", 0),
                    "search_status": final_state.get("search_status", "unknown")
                }
                self.storage.save_search_results(search_data)

            # 2b. NEW: Save refined subtasks
            if final_state.get("refined_subtasks"):
                self.storage.save_refined_subtasks(final_state["refined_subtasks"])
                logger.info(f"[Coordinator]  {len(final_state['refined_subtasks'])} ")

            # 3.
            if final_state.get("analysis_results"):
                self.storage.save_search_analysis(final_state["analysis_results"])

            # 4. 
            if final_state.get("synthesis_results"):
                self.storage.save_content_synthesis(final_state["synthesis_results"])

            # 5. 
            if final_state.get("final_report"):
                # 
                final_report_data = final_state["final_report"]

                #  {"result": {"report": ...}}
                if "result" in final_report_data and isinstance(final_report_data["result"], dict):
                    report_to_save = final_report_data["result"]
                else:
                    report_to_save = final_report_data

                self.storage.save_final_report(report_to_save, query)

            # 6. 
            if final_state.get("messages"):
                self.storage.save_execution_log(final_state["messages"])

            logger.info(f"[Coordinator] : {self.storage.get_project_dir()}")

        except Exception as e:
            logger.error(f"[Coordinator] : {e}")

    def _extract_execution_steps(self, final_state: DeepSearchState) -> List[str]:
        """TODO: Add docstring."""
        steps = []
        
        # 
        if final_state.get("decomposition_status") == "success":
            task_count = len(final_state.get("task_analysis", {}).get("subtasks", []))
            steps.append(f"  ({task_count} )")
        else:
            steps.append(" ")
        
        # 
        if final_state.get("search_status") == "success":
            search_count = final_state.get("total_results", 0)
            steps.append(f"  ({search_count} )")
        else:
            steps.append(" ")
        
        # 
        if final_state.get("analysis_status") == "success":
            steps.append(" ")
        else:
            steps.append(" ")
        
        # 
        if final_state.get("synthesis_status") == "success":
            steps.append(" ")
        else:
            steps.append(" ")
        
        # 
        if final_state.get("report_status") == "success":
            report = final_state.get("final_report", {}).get("report", {})
            word_count = len(report.get("content", ""))
            steps.append(f"  ({word_count} )")
        else:
            steps.append(" ")
        
        return steps
    
    async def quick_answer(self, query: str) -> str:
        """TODO: Add docstring."""
        try:
            # LLM
            client = self.llm_manager.get_client("default")
            answer = await client.simple_chat(
                query,
                "AI"
            )
            return answer
            
        except Exception as e:
            logger.error(f": {e}")
            return f": {e}"
    
    async def _convert_fiction_to_html(
        self,
        fiction_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """HTML"""
        try:
            from .html import FictionHTMLAgent

            # HTML
            template = context.get('html_template', 'novel')
            theme = context.get('html_theme', 'sepia')

            # HTML
            html_agent = FictionHTMLAgent()

            # 
            metadata = {
                'title': fiction_data.get('title', ''),
                'author': 'XunLong AI',
                'genre': fiction_data.get('metadata', {}).get('genre', ''),
                'synopsis': ''  # elements
            }

            # HTML
            html_content = html_agent.convert_to_html(
                content=fiction_data.get('content', ''),
                metadata=metadata,
                template=template,
                theme=theme
            )

            logger.info(f"HTML: {template}, : {theme}")
            return html_content

        except Exception as e:
            logger.error(f"HTML: {e}")
            # Markdown
            return fiction_data.get('content', '')

    def get_agent_status(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "coordinator_config": {
                "max_iterations": self.config.max_iterations,
                "timeout_seconds": self.config.timeout_seconds,
                "enable_parallel": self.config.enable_parallel,
                "retry_attempts": self.config.retry_attempts,
                "search_depth": self.config.search_depth,
                "max_search_results": self.config.max_search_results
            },
            "agents": {
                name: {
                    "name": agent.name,
                    "description": getattr(agent, 'description', f"{agent.name}"),
                    "status": "active"
                }
                for name, agent in self.agents.items()
            },
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "workflow_type": "langgraph" if LANGGRAPH_AVAILABLE else "simple"
        }


# 
class AgentCoordinator(DeepSearchCoordinator):
    """TODO: Add docstring."""
    pass
