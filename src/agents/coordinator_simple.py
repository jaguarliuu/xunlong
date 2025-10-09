"""
 - 
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

# 
try:
    from ..monitoring.langfuse_monitor import monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("")

class SimpleCoordinator:
    """TODO: Add docstring."""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""
        
        # 
        self.task_decomposer = TaskDecomposer(llm_manager, prompt_manager)
        self.deep_searcher = DeepSearcher(llm_manager, prompt_manager)
        self.report_generator = ReportGenerator(llm_manager, prompt_manager)
        self.content_evaluator = ContentEvaluator(llm_manager, prompt_manager)
        
    async def execute_deep_search(
        self, 
        query: str, 
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        
        # ID
        trace_id = str(uuid.uuid4())
        
        # Langfuse
        if MONITORING_AVAILABLE:
            monitor.start_trace(
                trace_id=trace_id,
                name="deep_search_workflow",
                input_data={"query": query, "report_type": report_type},
                metadata={"coordinator": self.name}
            )
        
        logger.info(f"[{self.name}]  (trace_id: {trace_id})")
        
        try:
            # 0. 
            time_context = time_tool.parse_date_query(query)
            logger.info(f"[{self.name}] : {time_context['time_context']}")
            
            # 1. 
            logger.info(f"[{self.name}] 1: ")
            decomposition = await self.task_decomposer.decompose_query(query, time_context)
            
            if not decomposition.get("subtasks"):
                logger.warning(f"[{self.name}] ")
                decomposition = {
                    "subtasks": [{
                        "id": "default_search",
                        "type": "search",
                        "title": "",
                        "search_queries": [query],
                        "priority": "high",
                        "expected_results": 10
                    }],
                    "strategy": "fallback"
                }
            
            logger.info(f"[{self.name}]  {len(decomposition['subtasks'])} ")
            
            # 2. 
            logger.info(f"[{self.name}] 2: ")
            search_results = await self.deep_searcher.execute_deep_search(
                query, decomposition, time_context
            )
            
            logger.info(f"[{self.name}]  {search_results.get('content_count', 0)} ")
            
            # 3. 
            logger.info(f"[{self.name}] 3: ")
            if search_results.get("all_content"):
                evaluated_content = await self.content_evaluator.evaluate_content_relevance(
                    query, search_results["all_content"], time_context
                )
                search_results["all_content"] = evaluated_content
                search_results["content_count"] = len(evaluated_content)
                logger.info(f"[{self.name}]  {len(evaluated_content)} ")
            else:
                logger.warning(f"[{self.name}] ")
            
            # 4. 
            logger.info(f"[{self.name}] 4: ")
            report = await self.report_generator.generate_report(
                query, search_results, report_type, time_context
            )
            
            # 5. 
            report_path = await self._save_report(query, report)
            
            logger.info(f"[{self.name}] ")
            
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
            
            # Langfuse
            if MONITORING_AVAILABLE:
                monitor.end_trace(
                    trace_id=trace_id,
                    output_data=result,
                    metadata={"status": "success"}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            
            error_result = {
                "status": "error",
                "query": query,
                "error": str(e),
                "time_context": time_tool.parse_date_query(query)
            }
            
            # Langfuse
            if MONITORING_AVAILABLE:
                monitor.end_trace(
                    trace_id=trace_id,
                    output_data=error_result,
                    metadata={"status": "error", "error": str(e)}
                )
            
            return error_result
    
    async def _save_report(self, query: str, report_data: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        try:
            import os
            from datetime import datetime
            
            # 
            results_dir = "results"
            os.makedirs(results_dir, exist_ok=True)
            
            # 
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_'))[:50]
            filename = f"deep_search_report_{safe_query}_{timestamp}.txt"
            filepath = os.path.join(results_dir, filename)
            
            # 
            report = report_data.get("report", {})
            content = f"""# 

## 
- : {query}
- : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- : {report.get('type', '')}

## 

{report.get('content', '')}

## 
- : {report.get('metadata', {}).get('word_count', 0)}
- : {report.get('metadata', {}).get('content_sources', 0)}
- : {report_data.get('status', '')}
"""
            
            # 
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"[{self.name}] : {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return ""
    
    def get_system_status(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
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
                "",
                "",
                "",
                "",
                ""
            ]
        }