"""DeepSearch智能体系统 - 深度搜索和智能分析"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .llm import LLMManager, PromptManager
from .agents.coordinator import DeepSearchCoordinator, DeepSearchConfig


class DeepSearchAgent:
    """DeepSearch智能体系统 - 提供深度搜索和智能分析服务"""
    
    def __init__(
        self,
        config: Optional[DeepSearchConfig] = None,
        llm_manager: Optional[LLMManager] = None,
        prompt_manager: Optional[PromptManager] = None
    ):
        """初始化DeepSearch智能体系统"""
        self.config = config or DeepSearchConfig()
        self.llm_manager = llm_manager or LLMManager()
        self.prompt_manager = prompt_manager or PromptManager()
        
        # 初始化协调器
        self.coordinator = DeepSearchCoordinator(
            config=self.config,
            llm_manager=self.llm_manager,
            prompt_manager=self.prompt_manager
        )
        
        logger.info("DeepSearch智能体系统初始化完成")
    
    async def search(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行深度搜索"""
        logger.info(f"开始深度搜索: {query}")
        
        try:
            # 使用协调器处理查询
            result = await self.coordinator.process_query(query, context)
            
            logger.info(f"深度搜索完成: {result.get('status')}")
            
            return result
            
        except Exception as e:
            logger.error(f"深度搜索失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "result": {}
            }
    
    async def quick_answer(self, query: str) -> str:
        """快速回答"""
        return await self.coordinator.quick_answer(query)
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "system": "DeepSearch智能体系统",
            "version": "2.0",
            "status": "active",
            "coordinator": self.coordinator.get_agent_status(),
            "llm_manager": {
                "available_configs": len(self.llm_manager.configs),
                "available_providers": len(self.llm_manager.get_available_providers())
            },
            "prompt_manager": {
                "loaded_prompts": len(self.prompt_manager.prompts_cache) if self.prompt_manager else 0
            }
        }
    
    async def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """分析查询复杂度"""
        try:
            # 使用任务分解智能体分析查询
            task_decomposer = self.coordinator.agents["task_decomposer"]
            result = await task_decomposer.process({
                "query": query,
                "context": {}
            })
            
            if result.get("status") == "success":
                analysis = result.get("result", {}).get("query_analysis", {})
                return {
                    "status": "success",
                    "complexity": analysis.get("complexity", "unknown"),
                    "intent": analysis.get("intent", "unknown"),
                    "time_sensitive": analysis.get("time_sensitive", False),
                    "domain": analysis.get("domain", "unknown"),
                    "expected_output": analysis.get("expected_output", "unknown")
                }
            else:
                return {
                    "status": "error",
                    "error": "查询分析失败"
                }
                
        except Exception as e:
            logger.error(f"查询复杂度分析失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def generate_report_only(
        self, 
        query: str, 
        search_results: list, 
        report_type: str = "general"
    ) -> Dict[str, Any]:
        """仅生成报告（基于已有搜索结果）"""
        try:
            report_generator = self.coordinator.agents["report_generator"]
            
            report_input = {
                "query": query,
                "task_analysis": {"query_analysis": {"expected_output": report_type}},
                "search_results": search_results,
                "analysis_results": {},
                "synthesis_results": {}
            }
            
            result = await report_generator.process(report_input)
            
            return result
            
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }