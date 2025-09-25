"""
任务分解智能体 - 将复杂查询分解为可搜索的子任务
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..llm.manager import LLMManager
from ..llm.prompts import PromptManager
from ..tools.time_tool import time_tool

class TaskDecomposer:
    """任务分解智能体"""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "任务分解智能体"
        
    async def decompose_query(
        self, 
        query: str, 
        time_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """分解查询为子任务"""
        
        logger.info(f"[{self.name}] 开始分解查询: {query}")
        
        # 获取时间上下文
        if not time_context:
            time_context = time_tool.parse_date_query(query)
        
        try:
            # 构建分解提示
            decomposition_prompt = self._build_decomposition_prompt(query, time_context)
            
            # 调用LLM进行任务分解
            # 使用默认客户端进行简单聊天
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                decomposition_prompt,
                "你是一个专业的任务分解专家，请按照要求分解用户查询。"
            )
            
            # 解析分解结果
            decomposition = self._parse_decomposition_response(response)
            
            # 添加时间上下文到每个子任务
            if decomposition.get("subtasks"):
                for subtask in decomposition["subtasks"]:
                    subtask["time_context"] = time_context
                    # 为搜索查询添加时间限定
                    if time_context.get("extracted_dates"):
                        time_str = time_tool.format_time_for_search(time_context)
                        if time_str:
                            subtask["search_queries"] = [
                                f"{q} {time_str}" for q in subtask.get("search_queries", [])
                            ]
            
            logger.info(f"[{self.name}] 任务分解完成，生成 {len(decomposition.get('subtasks', []))} 个子任务")
            return decomposition
            
        except Exception as e:
            logger.error(f"[{self.name}] 任务分解失败: {e}")
            return {
                "subtasks": [],
                "strategy": "fallback",
                "priority": "medium",
                "estimated_time": 300,
                "error": str(e)
            }
    
    def _build_decomposition_prompt(self, query: str, time_context: Dict[str, Any]) -> str:
        """构建任务分解提示"""
        
        # 获取系统提示
        system_prompt = self.prompt_manager.get_prompt(
            "agents\\task_decomposer\\system",
            default="""你是一个专业的任务分解专家，负责将复杂查询分解为可搜索的子任务。

## 核心职责
1. 分析用户查询的意图和需求
2. 识别查询中的关键信息（主题、时间、范围等）
3. 将复杂查询分解为3-5个具体的搜索子任务
4. 为每个子任务设计合适的搜索关键词

## 分解原则
- 每个子任务应该有明确的搜索目标
- 子任务之间应该互补，覆盖查询的不同方面
- 考虑时间限制和地域限制
- 优先搜索权威来源和最新信息"""
        )
        
        # 时间上下文信息
        time_info = time_context.get("time_context", "")
        extracted_dates = time_context.get("extracted_dates", [])
        
        prompt = f"""{system_prompt}

## 任务分解请求
用户查询: {query}

## 时间上下文
{time_info}
目标日期: {[d['formatted'] for d in extracted_dates] if extracted_dates else '无具体日期'}

## 分解要求
请将用户查询分解为3-5个具体的搜索子任务，每个子任务应该：
1. 有明确的搜索目标
2. 包含具体的搜索关键词
3. 考虑时间限制（如果有）
4. 覆盖查询的不同方面

## 输出格式
请严格按照以下JSON格式输出:
{{
    "subtasks": [
        {{
            "id": "task_1",
            "type": "search",
            "title": "子任务标题",
            "description": "子任务描述",
            "search_queries": ["搜索查询1", "搜索查询2"],
            "keywords": ["关键词1", "关键词2"],
            "priority": "high/medium/low",
            "expected_results": 5
        }}
    ],
    "strategy": "comprehensive/focused/exploratory",
    "priority": "high/medium/low",
    "estimated_time": 预估时间秒数
}}

注意：如果查询涉及具体日期，请确保每个搜索查询都包含相应的时间限定词。
"""
        return prompt
    
    def _parse_decomposition_response(self, response: str) -> Dict[str, Any]:
        """解析分解响应"""
        try:
            import json
            import re
            
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                decomposition = json.loads(json_str)
                
                # 验证必要字段
                if "subtasks" in decomposition and isinstance(decomposition["subtasks"], list):
                    return decomposition
            
            # 如果JSON解析失败，创建默认分解
            logger.warning(f"[{self.name}] JSON解析失败，使用默认分解")
            return self._create_default_decomposition(response)
            
        except Exception as e:
            logger.error(f"[{self.name}] 解析分解响应时出错: {e}")
            return self._create_default_decomposition(response)
    
    def _create_default_decomposition(self, query_or_response: str) -> Dict[str, Any]:
        """创建默认任务分解"""
        return {
            "subtasks": [
                {
                    "id": "default_search",
                    "type": "search",
                    "title": "默认搜索任务",
                    "description": "执行基本搜索",
                    "search_queries": [query_or_response[:100]],
                    "keywords": [],
                    "priority": "medium",
                    "expected_results": 10
                }
            ],
            "strategy": "fallback",
            "priority": "medium",
            "estimated_time": 300
        }