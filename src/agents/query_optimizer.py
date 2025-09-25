"""查询优化智能体"""

import json
from typing import Dict, Any
from loguru import logger

from .base import BaseAgent, AgentConfig
from ..llm import LLMManager, PromptManager


class QueryOptimizerAgent(BaseAgent):
    """查询优化智能体 - 分析用户意图，生成优化搜索策略"""
    
    def __init__(
        self, 
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="查询优化智能体",
            description="分析用户查询意图，生成优化的搜索关键词和策略",
            llm_config_name="query_optimizer",
            temperature=0.3,
            max_tokens=2000
        )
        
        super().__init__(llm_manager, prompt_manager, config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理查询优化"""
        try:
            query = input_data.get("query", "")
            context = input_data.get("context", {})
            
            logger.info(f"开始查询优化: {query}")
            
            # 获取系统提示词
            system_prompt = self.get_prompt("agents/query_optimizer/system")
            
            # 构建用户提示词
            user_prompt = f"""
请分析以下用户查询，并生成优化的搜索策略：

用户查询: {query}

请提供：
1. 查询意图分析
2. 优化后的搜索关键词（多个）
3. 搜索策略建议
4. 预期结果类型

请以JSON格式返回结果。
"""
            
            # 获取LLM响应
            response = await self.get_llm_response(user_prompt, system_prompt)
            
            # 尝试解析JSON响应
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回基本结果
                result = {
                    "intent_analysis": "查询意图分析",
                    "optimized_keywords": [query],
                    "search_strategy": "基础搜索策略",
                    "expected_result_type": "综合信息",
                    "raw_response": response
                }
            
            # 确保包含原始查询
            result["original_query"] = query
            result["optimized_query"] = result.get("optimized_keywords", [query])[0] if result.get("optimized_keywords") else query
            
            logger.info(f"查询优化完成: {result.get('optimized_query', query)}")
            
            return {
                "status": "success",
                "agent": self.name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"查询优化失败: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "result": {
                    "original_query": input_data.get("query", ""),
                    "optimized_query": input_data.get("query", ""),
                    "intent_analysis": "分析失败",
                    "optimized_keywords": [input_data.get("query", "")],
                    "search_strategy": "默认策略",
                    "expected_result_type": "未知"
                }
            }