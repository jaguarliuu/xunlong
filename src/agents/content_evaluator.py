"""
内容评估智能体 - 评估搜索内容与查询主题和时间的相关性
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from loguru import logger

from ..llm.manager import LLMManager
from ..llm.prompts import PromptManager
from ..tools.time_tool import time_tool

class ContentEvaluator:
    """内容评估智能体"""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "内容评估智能体"
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理内容评估请求"""
        content_items = data.get("content_items", [])
        query = data.get("query", "")
        time_context = data.get("time_context", {})
        
        result = await self.evaluate_content(content_items, query, time_context)
        return {
            "agent": self.name,
            "result": result,
            "status": "success" if result.get("relevant_content") else "failed"
        }
        
    async def evaluate_content_relevance(
        self, 
        query: str, 
        content_items: List[Dict[str, Any]],
        time_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """评估内容相关性并过滤"""
        
        logger.info(f"[{self.name}] 开始评估 {len(content_items)} 个内容项的相关性")
        
        # 获取时间上下文
        if not time_context:
            time_context = time_tool.parse_date_query(query)
        
        # 并行评估所有内容项
        evaluation_tasks = []
        for i, item in enumerate(content_items):
            task = self._evaluate_single_item(query, item, time_context, i)
            evaluation_tasks.append(task)
        
        evaluations = await asyncio.gather(*evaluation_tasks, return_exceptions=True)
        
        # 过滤相关内容
        relevant_items = []
        for i, evaluation in enumerate(evaluations):
            if isinstance(evaluation, Exception):
                logger.error(f"[{self.name}] 评估第 {i} 个内容项时出错: {evaluation}")
                continue
                
            if evaluation and evaluation.get("is_relevant", False):
                item = content_items[i].copy()
                item["evaluation"] = evaluation
                relevant_items.append(item)
                logger.info(f"[{self.name}] 内容项 {i} 相关性评分: {evaluation.get('relevance_score', 0)}")
            else:
                logger.info(f"[{self.name}] 内容项 {i} 被过滤 - 相关性不足")
        
        logger.info(f"[{self.name}] 评估完成，保留 {len(relevant_items)}/{len(content_items)} 个相关内容项")
        return relevant_items
    
    async def _evaluate_single_item(
        self, 
        query: str, 
        item: Dict[str, Any], 
        time_context: Dict[str, Any],
        index: int
    ) -> Optional[Dict[str, Any]]:
        """评估单个内容项"""
        
        try:
            # 构建评估提示
            evaluation_prompt = self._build_evaluation_prompt(query, item, time_context)
            
            # 调用LLM进行评估
            # 使用默认客户端进行简单聊天
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                evaluation_prompt,
                "你是一个专业的内容相关性评估专家。"
            )
            
            # 解析评估结果
            evaluation = self._parse_evaluation_response(response)
            return evaluation
            
        except Exception as e:
            logger.error(f"[{self.name}] 评估内容项 {index} 时出错: {e}")
            return None
    
    def _build_evaluation_prompt(
        self, 
        query: str, 
        item: Dict[str, Any], 
        time_context: Dict[str, Any]
    ) -> str:
        """构建评估提示"""
        
        # 获取系统提示模板
        system_prompt = self.prompt_manager.get_prompt(
            "agents\\content_evaluator\\system",
            default="""你是一个专业的内容相关性评估专家，负责评估搜索获取的内容是否与用户查询相关。

## 核心职责
1. 评估内容与查询主题的匹配度
2. 严格检查时间相关性，确保内容时间与查询要求一致
3. 评估内容的质量和信息价值
4. 过滤不相关或过时的内容

## 评估标准
- 主题相关性：内容是否与查询主题匹配
- 时间相关性：内容时间是否与查询时间要求一致
- 内容质量：内容是否有价值和信息量
- 来源可靠性：内容来源是否权威可信"""
        )
        
        # 提取内容信息
        title = item.get("title", "无标题")
        content = item.get("content", "")[:1000]  # 限制内容长度
        url = item.get("url", "")
        
        # 提取时间信息
        extracted_dates = time_context.get("extracted_dates", [])
        current_time = time_context.get("current_time", {})
        
        prompt = f"""{system_prompt}

## 评估任务
请评估以下内容是否与用户查询相关，特别注意时间匹配度。

## 用户查询
{query}

## 时间上下文
当前时间: {current_time.get('current_datetime', '未知')}
查询中的目标日期: {[d['formatted'] for d in extracted_dates] if extracted_dates else '无具体日期'}

## 待评估内容
标题: {title}
URL: {url}
内容摘要: {content}

## 评估标准
1. 主题相关性 (0-10分): 内容是否与查询主题匹配
2. 时间相关性 (0-10分): 内容时间是否与查询时间要求匹配
3. 内容质量 (0-10分): 内容是否有价值和信息量

## 输出格式
请严格按照以下JSON格式输出评估结果:
{{
    "is_relevant": true/false,
    "relevance_score": 总分(0-30),
    "topic_score": 主题相关性分数(0-10),
    "time_score": 时间相关性分数(0-10),
    "quality_score": 内容质量分数(0-10),
    "reason": "评估理由",
    "extracted_time": "从内容中提取的时间信息"
}}

注意: 如果查询指定了具体日期，时间相关性必须严格匹配，否则应该被过滤。
"""
        return prompt
    
    def _parse_evaluation_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析评估响应"""
        try:
            import json
            
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                evaluation = json.loads(json_str)
                
                # 验证必要字段
                required_fields = ["is_relevant", "relevance_score", "topic_score", "time_score", "quality_score"]
                if all(field in evaluation for field in required_fields):
                    return evaluation
            
            # 如果JSON解析失败，尝试简单的文本解析
            logger.warning(f"[{self.name}] JSON解析失败，尝试文本解析")
            return self._fallback_parse(response)
            
        except Exception as e:
            logger.error(f"[{self.name}] 解析评估响应时出错: {e}")
            return None
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """备用解析方法"""
        # 简单的关键词匹配
        is_relevant = "相关" in response and "不相关" not in response
        
        # 尝试提取分数
        score_match = re.search(r'(\d+)', response)
        score = int(score_match.group(1)) if score_match else (20 if is_relevant else 5)
        
        return {
            "is_relevant": is_relevant,
            "relevance_score": score,
            "topic_score": score // 3,
            "time_score": score // 3,
            "quality_score": score // 3,
            "reason": "备用解析结果",
            "extracted_time": "未提取"
        }
    
    async def filter_by_time_relevance(
        self, 
        content_items: List[Dict[str, Any]], 
        target_dates: List[str],
        tolerance_days: int = 2
    ) -> List[Dict[str, Any]]:
        """基于时间相关性过滤内容"""
        
        if not target_dates:
            return content_items
        
        filtered_items = []
        
        for item in content_items:
            # 尝试从内容中提取时间信息
            extracted_time = self._extract_time_from_content(item)
            
            if extracted_time:
                # 检查时间相关性
                is_time_relevant = any(
                    time_tool.is_date_relevant(extracted_time, target_date, tolerance_days)
                    for target_date in target_dates
                )
                
                if is_time_relevant:
                    item["extracted_time"] = extracted_time
                    filtered_items.append(item)
                else:
                    logger.info(f"[{self.name}] 过滤时间不匹配的内容: {extracted_time} vs {target_dates}")
            else:
                # 如果无法提取时间，保留内容但标记
                item["extracted_time"] = "未知"
                filtered_items.append(item)
        
        return filtered_items
    
    def _extract_time_from_content(self, item: Dict[str, Any]) -> Optional[str]:
        """从内容中提取时间信息"""
        text = f"{item.get('title', '')} {item.get('content', '')}"
        
        # 时间模式匹配
        patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{1,2})月(\d{1,2})日',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                match = matches[0]
                if len(match) == 3:  # 完整日期
                    year, month, day = match
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif len(match) == 2:  # 月日，使用当前年份
                    month, day = match
                    current_year = datetime.now().year
                    return f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None