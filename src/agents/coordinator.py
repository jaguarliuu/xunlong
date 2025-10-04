"""深度搜索智能体协调器 - 管理多智能体深度搜索协作"""

import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
    logger.info("LangGraph库导入成功，启用多agent协作功能")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    logger.warning(f"LangGraph库导入失败: {e}")
    
# 定义消息类型
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
from ..storage import SearchStorage
from .report import ReportCoordinator
from .output_type_detector import OutputTypeDetector
from .fiction import FictionElementsDesigner, FictionOutlineGenerator
from .ppt import PPTCoordinator


class DeepSearchState(TypedDict):
    """深度搜索状态"""
    query: str
    context: Dict[str, Any]
    messages: List[Dict[str, Any]]
    current_step: str

    # 输出类型检测
    output_type: str  # "report", "fiction", "ppt"
    output_type_confidence: float

    # 任务分解结果
    task_analysis: Dict[str, Any]
    decomposition_status: str

    # 深度搜索结果
    search_results: List[Dict[str, Any]]
    search_status: str
    total_results: int

    # 分析结果
    analysis_results: Dict[str, Any]
    analysis_status: str

    # 综合结果
    synthesis_results: Dict[str, Any]
    synthesis_status: str

    # 小说创作特有字段
    fiction_requirements: Dict[str, Any]  # 小说要求
    fiction_elements: Dict[str, Any]  # 六要素
    fiction_outline: Dict[str, Any]  # 章节大纲

    # PPT生成特有字段
    ppt_config: Dict[str, Any]  # PPT配置
    ppt_outline: Dict[str, Any]  # PPT大纲
    ppt_data: Dict[str, Any]  # PPT数据

    # 最终报告
    final_report: Dict[str, Any]
    report_status: str

    # 错误信息
    errors: List[str]

    # 元数据
    workflow_id: str
    timestamp: str


@dataclass
class DeepSearchConfig:
    """深度搜索配置"""
    max_iterations: int = 10
    timeout_seconds: int = 600  # 增加超时时间
    enable_parallel: bool = True
    retry_attempts: int = 3
    llm_config_name: str = "default"
    search_depth: str = "deep"  # surface, medium, deep
    max_search_results: int = 20


class DeepSearchCoordinator:
    """深度搜索协调器 - 管理多智能体深度搜索协作"""
    
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

        # 初始化所有智能体
        self.agents = {
            "task_decomposer": TaskDecomposerAgent(self.llm_manager, self.prompt_manager),
            "deep_searcher": DeepSearcherAgent(self.llm_manager, self.prompt_manager),
            "query_optimizer": QueryOptimizerAgent(self.llm_manager, self.prompt_manager),
            "search_analyzer": SearchAnalyzerAgent(self.llm_manager, self.prompt_manager),
            "content_synthesizer": ContentSynthesizerAgent(self.llm_manager, self.prompt_manager),
            "report_generator": ReportGeneratorAgent(self.llm_manager, self.prompt_manager),
            "content_evaluator": ContentEvaluator(self.llm_manager, self.prompt_manager)
        }

        # 初始化报告协调器（多智能体协作）
        self.report_coordinator = ReportCoordinator(
            self.llm_manager,
            self.prompt_manager,
            max_iterations=3,
            confidence_threshold=0.7
        )

        # 初始化输出类型检测器
        self.output_type_detector = OutputTypeDetector(self.llm_manager, self.prompt_manager)

        # 初始化小说创作智能体
        self.fiction_elements_designer = FictionElementsDesigner(self.llm_manager, self.prompt_manager)
        self.fiction_outline_generator = FictionOutlineGenerator(self.llm_manager, self.prompt_manager)
        
        # 如果LangGraph可用，初始化工作流
        if LANGGRAPH_AVAILABLE:
            try:
                self.workflow = self._create_langgraph_workflow()
                if self.workflow:
                    logger.info("LangGraph深度搜索工作流初始化成功")
                else:
                    logger.warning("LangGraph工作流创建失败，使用简化模式")
                    self.workflow = None
            except Exception as e:
                logger.error(f"LangGraph工作流初始化失败: {e}")
                self.workflow = None
        else:
            self.workflow = None
            logger.info("使用简化深度搜索工作流模式（无LangGraph）")
        
        logger.info("深度搜索协调器初始化完成")
    
    def _create_langgraph_workflow(self):
        """创建LangGraph深度搜索工作流"""
        if not LANGGRAPH_AVAILABLE:
            logger.warning("LangGraph不可用，无法创建工作流")
            return None
        
        try:
            logger.info("开始创建LangGraph深度搜索工作流...")
            
            # 创建状态图
            workflow = StateGraph(DeepSearchState)

            # 添加节点
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

            # 设置入口点
            workflow.set_entry_point("output_type_detector")

            # 添加条件边 - 根据输出类型路由
            workflow.add_conditional_edges(
                "output_type_detector",
                self._route_by_output_type,
                {
                    "report": "task_decomposer",
                    "fiction": "fiction_elements_designer",
                    "ppt": "task_decomposer"
                }
            )

            # 任务分解后的路由
            workflow.add_conditional_edges(
                "task_decomposer",
                self._route_after_task_decomposer,
                {
                    "deep_searcher": "deep_searcher"
                }
            )

            # 深度搜索后的路由 - 根据输出类型分流
            workflow.add_conditional_edges(
                "deep_searcher",
                self._route_after_deep_search,
                {
                    "search_analyzer": "search_analyzer",
                    "fiction_outline_generator": "fiction_outline_generator"
                }
            )

            # 搜索分析后的路由 - 区分报告和PPT
            workflow.add_conditional_edges(
                "search_analyzer",
                self._route_after_search_analyzer,
                {
                    "content_synthesizer": "content_synthesizer",
                    "ppt_generator": "ppt_generator"
                }
            )

            # 内容综合后生成报告
            workflow.add_edge("content_synthesizer", "report_generator")

            # 终止节点
            workflow.add_edge("report_generator", END)
            workflow.add_edge("ppt_generator", END)

            # 小说流程的边
            workflow.add_edge("fiction_elements_designer", "task_decomposer")  # 六要素设计后，搜索素材
            workflow.add_edge("fiction_outline_generator", "fiction_writer")
            workflow.add_edge("fiction_writer", END)
            
            # 编译工作流
            compiled_workflow = workflow.compile()
            logger.info("LangGraph工作流编译成功")
            
            return compiled_workflow
            
        except Exception as e:
            logger.error(f"创建LangGraph工作流失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _task_decomposer_node(self, state: DeepSearchState) -> DeepSearchState:
        """任务分解节点"""
        try:
            logger.info("执行任务分解...")

            # 构建上下文，包含输出类型和小说要素
            context = state.get("context", {})
            context["output_type"] = state.get("output_type", "report")

            # 如果是小说类型，添加六要素信息
            if context["output_type"] == "fiction":
                context["fiction_requirements"] = state.get("fiction_requirements", {})
                context["fiction_elements"] = state.get("fiction_elements", {})

            result = await self.agents["task_decomposer"].process({
                "query": state["query"],
                "context": context
            })

            state["task_analysis"] = result.get("result", {})
            state["decomposition_status"] = result.get("status", "unknown")

            subtasks_count = len(state["task_analysis"].get("subtasks", []))
            state["messages"].append({
                "role": "assistant",
                "content": f"任务分解完成: 生成了 {subtasks_count} 个子任务",
                "agent": "task_decomposer"
            })

            state["current_step"] = "deep_searcher"

        except Exception as e:
            logger.error(f"任务分解失败: {e}")
            state["errors"].append(f"任务分解失败: {e}")
            state["decomposition_status"] = "failed"

        return state
    
    async def _deep_searcher_node(self, state: DeepSearchState) -> DeepSearchState:
        """深度搜索节点"""
        try:
            logger.info("执行深度搜索...")
            
            task_analysis = state.get("task_analysis", {})
            subtasks = task_analysis.get("subtasks", [])
            
            if not subtasks:
                # 如果没有子任务，创建默认搜索任务
                subtasks = [{
                    "id": "default_search",
                    "type": "search",
                    "title": "默认搜索",
                    "search_queries": [state.get("query", "")],
                    "depth_level": self.config.search_depth
                }]
            
            all_search_results = []
            
            # 执行所有搜索子任务
            for subtask in subtasks:
                if subtask.get("type") == "search":
                    logger.info(f"执行搜索子任务: {subtask.get('title', 'Unknown')}")
                    
                    search_input = {
                        "query": state.get("query", ""),
                        "decomposition": {"subtasks": [subtask]},  # 将单个子任务包装成分解结果格式
                        "context": state.get("context", {})
                    }
                    
                    search_result = await self.agents["deep_searcher"].process(search_input)
                    logger.debug(f"深度搜索返回结果: status={search_result.get('status')}, keys={list(search_result.keys())}")
                    
                    if search_result.get("status") == "success":
                        # 深度搜索智能体的内容在result字段中
                        result_data = search_result.get("result", {})
                        task_results = result_data.get("all_content", [])
                        logger.debug(f"从深度搜索获得 {len(task_results)} 个结果")
                        if task_results:
                            logger.debug(f"第一个结果示例: {task_results[0]}")
                        all_search_results.extend(task_results)
                    
                    # 避免过于频繁的请求
                    await asyncio.sleep(1)
            
            # 限制结果数量
            if len(all_search_results) > self.config.max_search_results:
                all_search_results = all_search_results[:self.config.max_search_results]
            
            state["search_results"] = all_search_results
            state["search_status"] = "success" if all_search_results else "failed"
            state["total_results"] = len(all_search_results)
            
            state["messages"].append({
                "role": "assistant",
                "content": f"深度搜索完成: 获得 {len(all_search_results)} 个高质量结果",
                "agent": "deep_searcher"
            })
            
            state["current_step"] = "search_analyzer"
            
        except Exception as e:
            logger.error(f"深度搜索失败: {e}")
            state["errors"].append(f"深度搜索失败: {e}")
            state["search_status"] = "failed"
            state["search_results"] = []
            state["total_results"] = 0
        
        return state
    
    async def _search_analyzer_node(self, state: DeepSearchState) -> DeepSearchState:
        """搜索分析节点"""
        try:
            logger.info("执行搜索分析...")
            
            search_results = state.get("search_results", [])
            logger.info(f"传递给搜索分析智能体的结果数量: {len(search_results)}")
            if search_results:
                logger.debug(f"第一个搜索结果示例: {search_results[0]}")
            
            result = await self.agents["search_analyzer"].process({
                "query": state["query"],
                "search_results": search_results
            })
            
            state["analysis_results"] = result.get("result", {})
            state["analysis_status"] = result.get("status", "unknown")
            
            state["messages"].append({
                "role": "assistant",
                "content": f"搜索分析完成: 分析了 {len(state.get('search_results', []))} 个结果",
                "agent": "search_analyzer"
            })
            
            state["current_step"] = "content_synthesizer"
            
        except Exception as e:
            logger.error(f"搜索分析失败: {e}")
            state["errors"].append(f"搜索分析失败: {e}")
            state["analysis_status"] = "failed"
        
        return state
    
    async def _content_synthesizer_node(self, state: DeepSearchState) -> DeepSearchState:
        """内容综合节点"""
        try:
            logger.info("执行内容综合...")
            
            result = await self.agents["content_synthesizer"].process({
                "query": state["query"],
                "search_results": state.get("search_results", []),
                "analysis_results": state.get("analysis_results", {})
            })
            
            state["synthesis_results"] = result.get("result", {})
            state["synthesis_status"] = result.get("status", "unknown")
            
            state["messages"].append({
                "role": "assistant",
                "content": f"内容综合完成",
                "agent": "content_synthesizer"
            })
            
            state["current_step"] = "report_generator"
            
        except Exception as e:
            logger.error(f"内容综合失败: {e}")
            state["errors"].append(f"内容综合失败: {e}")
            state["synthesis_status"] = "failed"
        
        return state
    
    async def _report_generator_node(self, state: DeepSearchState) -> DeepSearchState:
        """报告生成节点（多智能体协作）"""
        try:
            logger.info("执行多智能体协作报告生成...")

            query = state.get("query", "")
            search_results = state.get("search_results", [])
            synthesis_results = state.get("synthesis_results", {})

            # 判断报告类型
            task_analysis = state.get("task_analysis", {})
            report_type = task_analysis.get("report_type", "comprehensive")

            # 获取输出格式和HTML配置
            context = state.get("context", {})
            output_format = context.get("output_format", "md")
            html_config = {
                "template": context.get("html_template", "academic"),
                "theme": context.get("html_theme", "light")
            }

            # 使用报告协调器进行多智能体协作生成
            result = await self.report_coordinator.generate_report(
                query=query,
                search_results=search_results,
                synthesis_results=synthesis_results,
                report_type=report_type,
                output_format=output_format,
                html_config=html_config
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
                    "content": f"报告生成完成: 生成了 {word_count} 字的详细报告 (置信度: {avg_confidence:.2f})",
                    "agent": "report_coordinator"
                })
            else:
                # 协作生成失败，回退到单智能体
                logger.warning("多智能体报告生成失败，回退到单智能体模式")

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
                    "content": "报告生成完成（使用备用模式）",
                    "agent": "report_generator"
                })

            state["current_step"] = "completed"

        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            state["errors"].append(f"报告生成失败: {e}")
            state["report_status"] = "failed"

        return state

    async def _output_type_detector_node(self, state: DeepSearchState) -> DeepSearchState:
        """输出类型检测节点"""
        try:
            logger.info("执行输出类型检测...")

            query = state.get("query", "")
            context = state.get("context", {})

            # 优先使用显式指定的输出类型（来自CLI参数）
            explicit_output_type = context.get("output_type")

            if explicit_output_type:
                # 使用显式指定的类型
                output_type = explicit_output_type
                confidence = 1.0  # 显式指定的置信度为100%
                logger.info(f"使用显式指定的输出类型: {output_type}")

                state["output_type"] = output_type
                state["output_type_confidence"] = confidence

                state["messages"].append({
                    "role": "assistant",
                    "content": f"使用指定输出类型: {output_type}",
                    "agent": "output_type_detector"
                })

                # 如果是fiction类型，使用提供的要求或提取
                if output_type == "fiction":
                    # 优先使用显式提供的fiction_requirements
                    if "fiction_requirements" in context:
                        fiction_requirements = context["fiction_requirements"]
                        logger.info(f"使用提供的小说创作要求: {fiction_requirements}")
                    else:
                        fiction_requirements = self.output_type_detector.extract_fiction_requirements(query)
                        logger.info(f"从查询提取小说创作要求: {fiction_requirements}")

                    state["fiction_requirements"] = fiction_requirements

                # 如果是ppt类型，保存PPT配置
                elif output_type == "ppt":
                    if "ppt_config" in context:
                        ppt_config = context["ppt_config"]
                        state["ppt_config"] = ppt_config
                        logger.info(f"使用提供的PPT配置: style={ppt_config.get('style')}, slides={ppt_config.get('slides')}")
                    else:
                        # 使用默认PPT配置
                        state["ppt_config"] = {
                            "style": "business",
                            "slides": 10,
                            "depth": "medium",
                            "theme": "default"
                        }
                        logger.info(f"使用默认PPT配置")

            else:
                # 没有显式指定，使用自动检测
                logger.info("未指定输出类型，使用自动检测")

                detection_result = await self.output_type_detector.detect_output_type(query)

                output_type = detection_result.get("output_type", "report")
                confidence = detection_result.get("confidence", 0.0)

                state["output_type"] = output_type
                state["output_type_confidence"] = confidence

                logger.info(f"自动检测输出类型: {output_type} (置信度: {confidence:.2f})")

                state["messages"].append({
                    "role": "assistant",
                    "content": f"检测到输出类型: {output_type} (置信度: {confidence:.2f})",
                    "agent": "output_type_detector"
                })

                # 如果是fiction类型，提取小说创作要求
                if output_type == "fiction":
                    fiction_requirements = self.output_type_detector.extract_fiction_requirements(query)
                    state["fiction_requirements"] = fiction_requirements
                    logger.info(f"小说创作要求: {fiction_requirements}")

        except Exception as e:
            logger.error(f"输出类型检测失败: {e}")
            state["errors"].append(f"输出类型检测失败: {e}")
            state["output_type"] = "report"  # 默认为报告类型
            state["output_type_confidence"] = 0.5

        return state

    async def _fiction_elements_designer_node(self, state: DeepSearchState) -> DeepSearchState:
        """小说六要素设计节点"""
        try:
            logger.info("执行小说六要素设计...")

            query = state.get("query", "")
            fiction_requirements = state.get("fiction_requirements", {})

            # 设计六要素
            result = await self.fiction_elements_designer.design_elements(
                query=query,
                requirements=fiction_requirements,
                search_results=None  # 初次设计时没有搜索结果
            )

            if result["status"] == "success":
                state["fiction_elements"] = result["elements"]
                logger.info("小说六要素设计完成")

                state["messages"].append({
                    "role": "assistant",
                    "content": f"小说六要素设计完成",
                    "agent": "fiction_elements_designer"
                })
            else:
                state["errors"].append(f"六要素设计失败: {result.get('error', '未知错误')}")

        except Exception as e:
            logger.error(f"小说六要素设计失败: {e}")
            state["errors"].append(f"六要素设计失败: {e}")

        return state

    async def _fiction_outline_generator_node(self, state: DeepSearchState) -> DeepSearchState:
        """小说大纲生成节点"""
        try:
            logger.info("执行小说大纲生成...")

            query = state.get("query", "")
            fiction_elements = state.get("fiction_elements", {})
            fiction_requirements = state.get("fiction_requirements", {})

            # 生成大纲
            result = await self.fiction_outline_generator.generate_outline(
                query=query,
                elements=fiction_elements,
                requirements=fiction_requirements
            )

            if result["status"] == "success":
                state["fiction_outline"] = result["outline"]
                total_chapters = result.get("total_chapters", 0)
                logger.info(f"小说大纲生成完成，共 {total_chapters} 个章节")

                state["messages"].append({
                    "role": "assistant",
                    "content": f"小说大纲生成完成，共 {total_chapters} 个章节",
                    "agent": "fiction_outline_generator"
                })
            else:
                state["errors"].append(f"大纲生成失败: {result.get('error', '未知错误')}")

        except Exception as e:
            logger.error(f"小说大纲生成失败: {e}")
            state["errors"].append(f"大纲生成失败: {e}")

        return state

    async def _fiction_writer_node(self, state: DeepSearchState) -> DeepSearchState:
        """小说写作节点 - 使用SectionWriter实际撰写章节内容"""
        try:
            logger.info("执行小说写作...")

            query = state.get("query", "")
            fiction_outline = state.get("fiction_outline", {})
            fiction_elements = state.get("fiction_elements", {})
            search_results = state.get("search_results", [])
            synthesis_results = state.get("synthesis_results", {})

            chapters = fiction_outline.get("chapters", [])

            if not chapters:
                raise ValueError("没有章节大纲，无法写作")

            logger.info(f"开始并行写作 {len(chapters)} 个章节...")

            # 准备可用内容（搜索结果 + 综合内容）
            available_content = search_results.copy()
            if synthesis_results and synthesis_results.get("synthesis"):
                available_content.append({
                    "title": "综合分析",
                    "content": synthesis_results["synthesis"],
                    "source": "content_synthesizer"
                })

            # 并行写作所有章节
            write_tasks = []
            for i, chapter in enumerate(chapters):
                # 构建章节写作要求
                section_requirements = {
                    "id": chapter.get("id", i + 1),
                    "title": f"第{chapter.get('id', i + 1)}章: {chapter.get('title', '')}",
                    "requirements": self._build_chapter_writing_requirements(
                        chapter,
                        fiction_elements,
                        fiction_outline,
                        query
                    ),
                    "word_count": chapter.get("word_count", 800),
                    "importance": 0.8
                }

                # 添加上下文（前一章的内容）
                context = None
                if i > 0:
                    context = {
                        "previous_section_title": f"第{chapters[i-1].get('id', i)}章: {chapters[i-1].get('title', '')}",
                        "previous_section_summary": chapters[i-1].get("writing_points", "")
                    }

                # 使用报告协调器的section_writer写作章节
                task = self.report_coordinator.section_writer.write_section(
                    section=section_requirements,
                    available_content=available_content,
                    context=context
                )
                write_tasks.append(task)

            # 等待所有章节写作完成
            chapter_results = await asyncio.gather(*write_tasks, return_exceptions=True)

            # 组装小说内容
            fiction_content = f"# {fiction_outline.get('title', '小说')}\n\n"
            fiction_content += f"**概要**: {fiction_outline.get('synopsis', '')}\n\n"
            fiction_content += "---\n\n"

            total_words = 0
            successful_chapters = 0

            for i, result in enumerate(chapter_results):
                if isinstance(result, Exception):
                    logger.error(f"章节 {i+1} 写作失败: {result}")
                    # 失败时使用大纲代替
                    chapter = chapters[i]
                    fiction_content += f"## 第{chapter['id']}章: {chapter['title']}\n\n"
                    fiction_content += f"（本章写作失败，暂用大纲代替）\n\n"
                    fiction_content += f"**写作要点**: {chapter.get('writing_points', '')}\n\n"
                    fiction_content += "---\n\n"
                else:
                    # 成功时使用实际内容
                    chapter_content = result.get("content", "")
                    chapter_title = chapters[i].get("title", f"第{i+1}章")

                    fiction_content += f"## 第{chapters[i]['id']}章: {chapter_title}\n\n"
                    fiction_content += chapter_content + "\n\n"
                    fiction_content += "---\n\n"

                    total_words += len(chapter_content)
                    successful_chapters += 1

            # 准备报告数据
            report_data = {
                "title": fiction_outline.get("title", "小说"),
                "content": fiction_content,
                "word_count": total_words,
                "metadata": {
                    "type": "fiction",
                    "total_chapters": len(chapters),
                    "successful_chapters": successful_chapters,
                    "genre": state.get("fiction_requirements", {}).get("genre", "未知"),
                    "elements": fiction_elements
                }
            }

            # 转换为HTML（如果需要）
            html_content = None
            output_format = state.get("context", {}).get("output_format", "md")
            if output_format == "html":
                logger.info("开始转换小说为HTML格式")
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

            logger.info(f"小说生成完成，共 {len(chapters)} 个章节，成功写作 {successful_chapters} 章，总字数 {total_words}")

            state["messages"].append({
                "role": "assistant",
                "content": f"小说生成完成，共 {len(chapters)} 个章节，成功写作 {successful_chapters} 章，总字数 {total_words}",
                "agent": "fiction_writer"
            })

        except Exception as e:
            logger.error(f"小说写作失败: {e}")
            state["errors"].append(f"小说写作失败: {e}")
            state["report_status"] = "failed"

        return state

    async def _ppt_generator_node(self, state: DeepSearchState) -> DeepSearchState:
        """PPT生成节点"""
        try:
            logger.info("执行PPT生成...")

            query = state.get("query", "")
            search_results = state.get("search_results", [])
            ppt_config = state.get("ppt_config", {})

            # 创建PPT协调器
            ppt_coordinator = PPTCoordinator(self.llm_manager, self.prompt_manager)

            # 生成PPT（使用新的多智能体架构）
            result = await ppt_coordinator.generate_ppt_v2(
                topic=query,
                search_results=search_results,
                ppt_config=ppt_config
            )

            if result["status"] == "success":
                state["ppt_data"] = result.get("ppt", {})
                state["final_report"] = {
                    "result": {
                        "ppt": result.get("ppt", {}),
                        "html_content": result.get("html_content", ""),
                        "output_format": "html"
                    },
                    "status": "success"
                }
                state["report_status"] = "success"

                slide_count = len(result.get("ppt", {}).get("slides", []))
                logger.info(f"PPT生成完成，共 {slide_count} 页")

                state["messages"].append({
                    "role": "assistant",
                    "content": f"PPT生成完成，共 {slide_count} 页",
                    "agent": "ppt_generator"
                })
            else:
                raise Exception(result.get("error", "PPT生成失败"))

        except Exception as e:
            logger.error(f"PPT生成失败: {e}")
            state["errors"].append(f"PPT生成失败: {e}")
            state["report_status"] = "failed"

        return state

    def _build_chapter_writing_requirements(
        self,
        chapter: Dict[str, Any],
        fiction_elements: Dict[str, Any],
        fiction_outline: Dict[str, Any],
        query: str
    ) -> str:
        """构建章节写作要求"""

        # 提取六要素信息
        characters = fiction_elements.get("characters", [])
        place = fiction_elements.get("place", {})
        theme = fiction_elements.get("theme", {})

        # 提取章节信息
        writing_points = chapter.get("writing_points", "")
        key_scenes = chapter.get("key_scenes", [])
        characters_involved = chapter.get("characters_involved", [])
        suspense = chapter.get("suspense", "")

        requirements = f"""# 章节写作要求

## 原始需求
{query}

## 本章任务
{writing_points}

## 关键场景
{', '.join(key_scenes) if key_scenes else '无'}

## 涉及人物
{', '.join(characters_involved) if characters_involved else '无'}

## 人物设定
"""
        # 添加涉及人物的详细信息
        for char in characters:
            if char.get("name") in characters_involved:
                requirements += f"- **{char.get('name')}**: {char.get('occupation', '')}, {char.get('personality', '')}\n"

        requirements += f"""

## 场景设定
- **地点**: {place.get('main_location', '')}
- **描述**: {place.get('description', '')}

## 主题氛围
- **核心主题**: {theme.get('core_theme', '')}
- **情感基调**: {theme.get('tone', '')}

## 本章悬念
{suspense}

## 写作要求
1. **叙事视角**: 严格按照用户要求的视角（如第一人称、凶手视角等）
2. **场景描写**: 详细描写关键场景，营造氛围
3. **人物刻画**: 通过对话和动作展现人物性格
4. **悬念设置**: 在章节结尾留下悬念
5. **字数要求**: 约{chapter.get('word_count', 800)}字
6. **文学性**: 使用生动的语言，避免大纲式写作

请撰写这一章节的完整内容，要求：
- 是真正的小说叙事文本，不是大纲或要点
- 包含完整的场景描写、对话、心理描写
- 符合推理小说的叙事风格
- 严格遵循用户指定的视角和要求
"""

        return requirements

    def _route_by_output_type(self, state: DeepSearchState) -> str:
        """根据输出类型路由"""
        output_type = state.get("output_type", "report")
        logger.info(f"路由到: {output_type} 流程")
        return output_type

    def _route_after_task_decomposer(self, state: DeepSearchState) -> str:
        """任务分解后的路由"""
        return "deep_searcher"

    def _route_after_deep_search(self, state: DeepSearchState) -> str:
        """深度搜索后的路由 - 区分fiction和其他"""
        output_type = state.get("output_type", "report")
        if output_type == "fiction":
            return "fiction_outline_generator"
        else:
            return "search_analyzer"

    def _route_after_search_analyzer(self, state: DeepSearchState) -> str:
        """搜索分析后的路由 - 区分report和ppt"""
        output_type = state.get("output_type", "report")
        if output_type == "ppt":
            logger.info("路由到PPT生成节点")
            return "ppt_generator"
        else:
            logger.info("路由到内容综合节点")
            return "content_synthesizer"

    def _route_after_synthesis(self, state: DeepSearchState) -> str:
        """内容综合后的路由"""
        output_type = state.get("output_type", "report")
        if output_type == "fiction":
            return "fiction_outline_generator"
        else:
            return "report_generator"

    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理深度搜索查询"""
        try:
            # 创建存储项目
            project_id = self.storage.create_project(query)
            logger.info(f"创建搜索项目: {project_id}")

            # 初始化状态
            workflow_id = f"deep_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            initial_state: DeepSearchState = {
                "query": query,
                "context": context or {},
                "messages": [{"role": "user", "content": query}],
                "current_step": "output_type_detector",

                # 输出类型检测
                "output_type": "report",
                "output_type_confidence": 0.0,

                # 任务分解结果
                "task_analysis": {},
                "decomposition_status": "pending",

                # 深度搜索结果
                "search_results": [],
                "search_status": "pending",
                "total_results": 0,

                # 分析结果
                "analysis_results": {},
                "analysis_status": "pending",

                # 综合结果
                "synthesis_results": {},
                "synthesis_status": "pending",

                # 小说创作特有字段
                "fiction_requirements": {},
                "fiction_elements": {},
                "fiction_outline": {},

                # PPT生成特有字段
                "ppt_config": {},
                "ppt_outline": {},
                "ppt_data": {},

                # 最终报告
                "final_report": {},
                "report_status": "pending",

                # 错误信息
                "errors": [],

                # 元数据
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat()
            }
            
            if LANGGRAPH_AVAILABLE and self.workflow:
                # 使用LangGraph工作流
                logger.info("使用LangGraph深度搜索工作流处理查询")
                final_state = await self.workflow.ainvoke(initial_state)
            else:
                # 使用简化工作流
                logger.info("使用简化深度搜索工作流处理查询")
                final_state = await self._simple_deep_search_workflow(initial_state)
            
            # 确定最终状态
            if final_state["errors"]:
                status = "partial_success" if final_state.get("final_report") else "error"
            else:
                status = "success"

            # 保存所有中间产物和最终报告
            self._save_search_results(final_state, query)

            return {
                "status": status,
                "workflow_id": workflow_id,
                "query": query,
                "messages": final_state["messages"],
                "execution_steps": self._extract_execution_steps(final_state),

                # 详细结果
                "task_analysis": final_state["task_analysis"],
                "search_results": final_state["search_results"],
                "analysis_results": final_state["analysis_results"],
                "synthesis_results": final_state["synthesis_results"],
                "final_report": final_state["final_report"],

                # 统计信息
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
            logger.error(f"深度搜索查询处理失败: {e}")
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
        """简化深度搜索工作流（不使用LangGraph）"""
        try:
            # 步骤1: 输出类型检测
            logger.info("步骤 1/6: 输出类型检测")
            state = await self._output_type_detector_node(state)

            output_type = state.get("output_type", "report")

            if output_type == "fiction":
                # 小说创作流程
                logger.info("步骤 2/6: 小说六要素设计")
                state = await self._fiction_elements_designer_node(state)

                logger.info("步骤 3/6: 任务分解（搜集素材）")
                state = await self._task_decomposer_node(state)

                logger.info("步骤 4/6: 深度搜索")
                state = await self._deep_searcher_node(state)

                logger.info("步骤 5/6: 小说大纲生成")
                state = await self._fiction_outline_generator_node(state)

                logger.info("步骤 6/6: 小说写作")
                state = await self._fiction_writer_node(state)

            elif output_type == "ppt":
                # PPT生成流程
                logger.info("步骤 2/5: 任务分解（搜集资料）")
                state = await self._task_decomposer_node(state)

                logger.info("步骤 3/5: 深度搜索")
                state = await self._deep_searcher_node(state)

                logger.info("步骤 4/5: 搜索分析")
                state = await self._search_analyzer_node(state)

                logger.info("步骤 5/5: PPT生成")
                state = await self._ppt_generator_node(state)

            else:
                # 报告流程
                logger.info("步骤 2/6: 任务分解")
                state = await self._task_decomposer_node(state)

                logger.info("步骤 3/6: 深度搜索")
                state = await self._deep_searcher_node(state)

                logger.info("步骤 4/6: 搜索分析")
                state = await self._search_analyzer_node(state)

                logger.info("步骤 5/6: 内容综合")
                state = await self._content_synthesizer_node(state)

                logger.info("步骤 6/6: 报告生成")
                state = await self._report_generator_node(state)

            return state

        except Exception as e:
            logger.error(f"简化深度搜索工作流执行失败: {e}")
            state["errors"].append(f"工作流执行失败: {e}")
            return state
    
    def _save_search_results(self, final_state: DeepSearchState, query: str):
        """保存搜索结果到存储"""
        try:
            # 1. 保存任务分解
            if final_state.get("task_analysis"):
                self.storage.save_task_decomposition(final_state["task_analysis"])

            # 2. 保存搜索结果
            if final_state.get("search_results"):
                search_data = {
                    "all_content": final_state["search_results"],
                    "total_results": final_state.get("total_results", 0),
                    "search_status": final_state.get("search_status", "unknown")
                }
                self.storage.save_search_results(search_data)

            # 3. 保存搜索分析
            if final_state.get("analysis_results"):
                self.storage.save_search_analysis(final_state["analysis_results"])

            # 4. 保存内容综合
            if final_state.get("synthesis_results"):
                self.storage.save_content_synthesis(final_state["synthesis_results"])

            # 5. 保存最终报告
            if final_state.get("final_report"):
                # 提取正确的报告数据结构
                final_report_data = final_state["final_report"]

                # 如果是嵌套结构 {"result": {"report": ...}}，提取出来
                if "result" in final_report_data and isinstance(final_report_data["result"], dict):
                    report_to_save = final_report_data["result"]
                else:
                    report_to_save = final_report_data

                self.storage.save_final_report(report_to_save, query)

            # 6. 保存执行日志
            if final_state.get("messages"):
                self.storage.save_execution_log(final_state["messages"])

            logger.info(f"[Coordinator] 所有搜索结果已保存到: {self.storage.get_project_dir()}")

        except Exception as e:
            logger.error(f"[Coordinator] 保存搜索结果失败: {e}")

    def _extract_execution_steps(self, final_state: DeepSearchState) -> List[str]:
        """提取执行步骤"""
        steps = []
        
        # 任务分解
        if final_state.get("decomposition_status") == "success":
            task_count = len(final_state.get("task_analysis", {}).get("subtasks", []))
            steps.append(f"✓ 任务分解完成 ({task_count} 个子任务)")
        else:
            steps.append("✗ 任务分解失败")
        
        # 深度搜索
        if final_state.get("search_status") == "success":
            search_count = final_state.get("total_results", 0)
            steps.append(f"✓ 深度搜索完成 ({search_count} 个结果)")
        else:
            steps.append("✗ 深度搜索失败")
        
        # 搜索分析
        if final_state.get("analysis_status") == "success":
            steps.append("✓ 搜索分析完成")
        else:
            steps.append("✗ 搜索分析失败")
        
        # 内容综合
        if final_state.get("synthesis_status") == "success":
            steps.append("✓ 内容综合完成")
        else:
            steps.append("✗ 内容综合失败")
        
        # 报告生成
        if final_state.get("report_status") == "success":
            report = final_state.get("final_report", {}).get("report", {})
            word_count = len(report.get("content", ""))
            steps.append(f"✓ 报告生成完成 ({word_count} 字)")
        else:
            steps.append("✗ 报告生成失败")
        
        return steps
    
    async def quick_answer(self, query: str) -> str:
        """快速回答（不使用完整工作流）"""
        try:
            # 使用默认LLM客户端直接回答
            client = self.llm_manager.get_client("default")
            answer = await client.simple_chat(
                query,
                "你是一个有用的AI助手，请简洁准确地回答用户的问题。"
            )
            return answer
            
        except Exception as e:
            logger.error(f"快速回答失败: {e}")
            return f"抱歉，我无法回答这个问题。错误: {e}"
    
    async def _convert_fiction_to_html(
        self,
        fiction_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """将小说转换为HTML"""
        try:
            from .html import FictionHTMLAgent

            # 获取HTML配置
            template = context.get('html_template', 'novel')
            theme = context.get('html_theme', 'sepia')

            # 创建HTML转换智能体
            html_agent = FictionHTMLAgent()

            # 准备元数据
            metadata = {
                'title': fiction_data.get('title', '小说'),
                'author': 'XunLong AI',
                'genre': fiction_data.get('metadata', {}).get('genre', '小说'),
                'synopsis': ''  # 可以从elements中提取
            }

            # 转换为HTML
            html_content = html_agent.convert_to_html(
                content=fiction_data.get('content', ''),
                metadata=metadata,
                template=template,
                theme=theme
            )

            logger.info(f"小说HTML转换完成，使用模板: {template}, 主题: {theme}")
            return html_content

        except Exception as e:
            logger.error(f"小说HTML转换失败: {e}")
            # 返回原始Markdown
            return fiction_data.get('content', '')

    def get_agent_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
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
                    "description": getattr(agent, 'description', f"{agent.name}智能体"),
                    "status": "active"
                }
                for name, agent in self.agents.items()
            },
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "workflow_type": "langgraph" if LANGGRAPH_AVAILABLE else "simple"
        }


# 保持向后兼容性
class AgentCoordinator(DeepSearchCoordinator):
    """向后兼容的智能体协调器"""
    pass