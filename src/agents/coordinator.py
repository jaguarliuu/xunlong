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


class DeepSearchState(TypedDict):
    """深度搜索状态"""
    query: str
    context: Dict[str, Any]
    messages: List[Dict[str, Any]]
    current_step: str
    
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
        prompt_manager: Optional[PromptManager] = None
    ):
        self.config = config or DeepSearchConfig()
        self.llm_manager = llm_manager or LLMManager()
        self.prompt_manager = prompt_manager
        self.pipeline = DeepSearchPipeline()
        
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
            workflow.add_node("task_decomposer", self._task_decomposer_node)
            workflow.add_node("deep_searcher", self._deep_searcher_node)
            workflow.add_node("search_analyzer", self._search_analyzer_node)
            workflow.add_node("content_synthesizer", self._content_synthesizer_node)
            workflow.add_node("report_generator", self._report_generator_node)
            
            # 设置入口点
            workflow.set_entry_point("task_decomposer")
            
            # 添加边
            workflow.add_edge("task_decomposer", "deep_searcher")
            workflow.add_edge("deep_searcher", "search_analyzer")
            workflow.add_edge("search_analyzer", "content_synthesizer")
            workflow.add_edge("content_synthesizer", "report_generator")
            workflow.add_edge("report_generator", END)
            
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
            
            result = await self.agents["task_decomposer"].process({
                "query": state["query"],
                "context": state.get("context", {})
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
        """报告生成节点"""
        try:
            logger.info("执行报告生成...")
            
            # 准备报告生成输入
            report_input = {
                "query": state.get("query", ""),
                "task_analysis": state.get("task_analysis", {}),
                "search_results": state.get("search_results", []),
                "analysis_results": state.get("analysis_results", {}),
                "synthesis_results": state.get("synthesis_results", {})
            }
            
            result = await self.agents["report_generator"].process(report_input)
            
            state["final_report"] = result.get("result", {})
            state["report_status"] = result.get("status", "unknown")
            
            report = state["final_report"].get("report", {})
            word_count = len(report.get("content", ""))
            
            state["messages"].append({
                "role": "assistant",
                "content": f"报告生成完成: 生成了 {word_count} 字的详细报告",
                "agent": "report_generator"
            })
            
            state["current_step"] = "completed"
            
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            state["errors"].append(f"报告生成失败: {e}")
            state["report_status"] = "failed"
        
        return state
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理深度搜索查询"""
        try:
            # 初始化状态
            workflow_id = f"deep_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            initial_state: DeepSearchState = {
                "query": query,
                "context": context or {},
                "messages": [{"role": "user", "content": query}],
                "current_step": "task_decomposer",
                
                "task_analysis": {},
                "decomposition_status": "pending",
                
                "search_results": [],
                "search_status": "pending",
                "total_results": 0,
                
                "analysis_results": {},
                "analysis_status": "pending",
                
                "synthesis_results": {},
                "synthesis_status": "pending",
                
                "final_report": {},
                "report_status": "pending",
                
                "errors": [],
                
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
                
                "errors": final_state["errors"]
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
            # 步骤1: 任务分解
            logger.info("步骤 1/5: 任务分解")
            state = await self._task_decomposer_node(state)
            
            # 步骤2: 深度搜索
            logger.info("步骤 2/5: 深度搜索")
            state = await self._deep_searcher_node(state)
            
            # 步骤3: 搜索分析
            logger.info("步骤 3/5: 搜索分析")
            state = await self._search_analyzer_node(state)
            
            # 步骤4: 内容综合
            logger.info("步骤 4/5: 内容综合")
            state = await self._content_synthesizer_node(state)
            
            # 步骤5: 报告生成
            logger.info("步骤 5/5: 报告生成")
            state = await self._report_generator_node(state)
            
            return state
            
        except Exception as e:
            logger.error(f"简化深度搜索工作流执行失败: {e}")
            state["errors"].append(f"工作流执行失败: {e}")
            return state
    
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