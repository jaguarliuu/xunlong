"""
简化版深度搜索协调器 - 集成时间工具和内容评估
"""
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from ..llm.manager import LLMManager
from ..llm.prompts import PromptManager
from .task_decomposer import TaskDecomposer
from .deep_searcher import DeepSearcher
from .report_generator import ReportGenerator
from .content_evaluator import ContentEvaluator
from ..tools.time_tool import time_tool

# 导入监控模块
try:
    from ..monitoring.langfuse_monitor import monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("监控模块不可用")

class SimpleCoordinator:
    """简化版深度搜索协调器"""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "深度搜索协调器"
        
        # 初始化智能体
        self.task_decomposer = TaskDecomposer(llm_manager, prompt_manager)
        self.deep_searcher = DeepSearcher(llm_manager, prompt_manager)
        self.report_generator = ReportGenerator(llm_manager, prompt_manager)
        self.content_evaluator = ContentEvaluator(llm_manager, prompt_manager)
        
    async def execute_deep_search(
        self, 
        query: str, 
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """执行完整的深度搜索流程"""
        
        # 生成跟踪ID
        trace_id = str(uuid.uuid4())
        
        # 开始Langfuse跟踪
        if MONITORING_AVAILABLE:
            monitor.start_trace(
                trace_id=trace_id,
                name="deep_search_workflow",
                input_data={"query": query, "report_type": report_type},
                metadata={"coordinator": self.name}
            )
        
        logger.info(f"[{self.name}] 开始深度搜索流程 (trace_id: {trace_id})")
        
        try:
            # 0. 获取时间上下文
            time_context = time_tool.parse_date_query(query)
            logger.info(f"[{self.name}] 时间上下文: {time_context['time_context']}")
            
            # 1. 任务分解
            logger.info(f"[{self.name}] 步骤1: 任务分解")
            decomposition = await self.task_decomposer.decompose_query(query, time_context)
            
            if not decomposition.get("subtasks"):
                logger.warning(f"[{self.name}] 任务分解失败，使用默认搜索")
                decomposition = {
                    "subtasks": [{
                        "id": "default_search",
                        "type": "search",
                        "title": "默认搜索",
                        "search_queries": [query],
                        "priority": "high",
                        "expected_results": 10
                    }],
                    "strategy": "fallback"
                }
            
            logger.info(f"[{self.name}] 任务分解完成，生成 {len(decomposition['subtasks'])} 个子任务")
            
            # 2. 深度搜索
            logger.info(f"[{self.name}] 步骤2: 深度搜索")
            search_results = await self.deep_searcher.execute_deep_search(
                query, decomposition, time_context
            )
            
            logger.info(f"[{self.name}] 深度搜索完成，获得 {search_results.get('content_count', 0)} 个内容项")
            
            # 3. 内容评估和过滤
            logger.info(f"[{self.name}] 步骤3: 内容相关性评估")
            if search_results.get("all_content"):
                evaluated_content = await self.content_evaluator.evaluate_content_relevance(
                    query, search_results["all_content"], time_context
                )
                search_results["all_content"] = evaluated_content
                search_results["content_count"] = len(evaluated_content)
                logger.info(f"[{self.name}] 评估后保留 {len(evaluated_content)} 个相关内容项")
            else:
                logger.warning(f"[{self.name}] 没有内容需要评估")
            
            # 4. 生成报告
            logger.info(f"[{self.name}] 步骤4: 生成报告")
            report = await self.report_generator.generate_report(
                query, search_results, report_type, time_context
            )
            
            # 5. 保存报告
            report_path = await self._save_report(query, report)
            
            logger.info(f"[{self.name}] 深度搜索流程完成")
            
            result = {
                "status": "success",
                "query": query,
                "time_context": time_context,
                "decomposition": decomposition,
                "search_results": search_results,
                "report": report,
                "report_path": report_path,
                "statistics": {
                    "subtasks_count": len(decomposition.get("subtasks", [])),
                    "total_content_items": search_results.get("content_count", 0),
                    "report_word_count": len(report.get("report", {}).get("content", "")),
                    "execution_time": datetime.now().isoformat()
                }
            }
            
            # 结束Langfuse跟踪
            if MONITORING_AVAILABLE:
                monitor.end_trace(
                    trace_id=trace_id,
                    output_data=result,
                    metadata={"status": "success"}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] 深度搜索流程失败: {e}")
            
            error_result = {
                "status": "error",
                "query": query,
                "error": str(e),
                "time_context": time_tool.parse_date_query(query)
            }
            
            # 结束Langfuse跟踪（错误情况）
            if MONITORING_AVAILABLE:
                monitor.end_trace(
                    trace_id=trace_id,
                    output_data=error_result,
                    metadata={"status": "error", "error": str(e)}
                )
            
            return error_result
    
    async def _save_report(self, query: str, report_data: Dict[str, Any]) -> str:
        """保存报告到文件"""
        try:
            import os
            from datetime import datetime
            
            # 创建结果目录
            results_dir = "results"
            os.makedirs(results_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_'))[:50]
            filename = f"deep_search_report_{safe_query}_{timestamp}.txt"
            filepath = os.path.join(results_dir, filename)
            
            # 准备报告内容
            report = report_data.get("report", {})
            content = f"""# 深度搜索报告

## 查询信息
- 原始查询: {query}
- 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 报告类型: {report.get('type', '未知')}

## 报告内容

{report.get('content', '无内容')}

## 元数据
- 字数统计: {report.get('metadata', {}).get('word_count', 0)}
- 内容来源: {report.get('metadata', {}).get('content_sources', 0)}
- 生成状态: {report_data.get('status', '未知')}
"""
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"[{self.name}] 报告已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"[{self.name}] 保存报告失败: {e}")
            return ""
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        current_time = time_tool.get_current_time()
        
        return {
            "coordinator": {
                "name": self.name,
                "status": "active",
                "agents": [
                    "task_decomposer",
                    "deep_searcher", 
                    "content_evaluator",
                    "report_generator"
                ]
            },
            "time_context": current_time,
            "capabilities": [
                "任务分解",
                "深度搜索",
                "内容评估",
                "时间感知",
                "报告生成"
            ]
        }