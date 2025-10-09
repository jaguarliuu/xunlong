"""
 - 
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
    """TODO: Add docstring."""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
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
        """TODO: Add docstring."""
        
        logger.info(f"[{self.name}]  {len(content_items)} ")
        
        # 
        if not time_context:
            time_context = time_tool.parse_date_query(query)
        
        # 
        evaluation_tasks = []
        for i, item in enumerate(content_items):
            task = self._evaluate_single_item(query, item, time_context, i)
            evaluation_tasks.append(task)
        
        evaluations = await asyncio.gather(*evaluation_tasks, return_exceptions=True)
        
        # 
        relevant_items = []
        for i, evaluation in enumerate(evaluations):
            if isinstance(evaluation, Exception):
                logger.error(f"[{self.name}]  {i} : {evaluation}")
                continue
                
            if evaluation and evaluation.get("is_relevant", False):
                item = content_items[i].copy()
                item["evaluation"] = evaluation
                relevant_items.append(item)
                logger.info(f"[{self.name}]  {i} : {evaluation.get('relevance_score', 0)}")
            else:
                logger.info(f"[{self.name}]  {i}  - ")
        
        logger.info(f"[{self.name}]  {len(relevant_items)}/{len(content_items)} ")
        return relevant_items
    
    async def _evaluate_single_item(
        self, 
        query: str, 
        item: Dict[str, Any], 
        time_context: Dict[str, Any],
        index: int
    ) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        
        try:
            # 
            evaluation_prompt = self._build_evaluation_prompt(query, item, time_context)
            
            # LLM
            # 
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                evaluation_prompt,
                ""
            )
            
            # 
            evaluation = self._parse_evaluation_response(response)
            return evaluation
            
        except Exception as e:
            logger.error(f"[{self.name}]  {index} : {e}")
            return None
    
    def _build_evaluation_prompt(
        self, 
        query: str, 
        item: Dict[str, Any], 
        time_context: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""
        
        # 
        system_prompt = self.prompt_manager.get_prompt(
            "agents/content_evaluator/system",
            default="""

## 
1. 
2. 
3. 
4. 

## 
- 
- 
- 
- """
        )
        
        # 
        title = item.get("title", "")
        content = item.get("content", "")[:1000]  # 
        url = item.get("url", "")
        
        # 
        extracted_dates = time_context.get("extracted_dates", [])
        current_time = time_context.get("current_time", {})
        
        prompt = f"""{system_prompt}

## 


## 
{query}

## 
: {current_time.get('current_datetime', '')}
: {[d['formatted'] for d in extracted_dates] if extracted_dates else ''}

## 
: {title}
URL: {url}
: {content}

## 
1.  (0-10): 
2.  (0-10): 
3.  (0-10): 

## 
JSON:
{{
    "is_relevant": true/false,
    "relevance_score": (0-30),
    "topic_score": (0-10),
    "time_score": (0-10),
    "quality_score": (0-10),
    "reason": "",
    "extracted_time": ""
}}

: 
"""
        return prompt
    
    def _parse_evaluation_response(self, response: str) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        try:
            import json
            
            # JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                evaluation = json.loads(json_str)
                
                # 
                required_fields = ["is_relevant", "relevance_score", "topic_score", "time_score", "quality_score"]
                if all(field in evaluation for field in required_fields):
                    return evaluation
            
            # JSON
            logger.warning(f"[{self.name}] JSON")
            return self._fallback_parse(response)
            
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return None
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        # 
        is_relevant = "" in response and "" not in response
        
        # 
        score_match = re.search(r'(\d+)', response)
        score = int(score_match.group(1)) if score_match else (20 if is_relevant else 5)
        
        return {
            "is_relevant": is_relevant,
            "relevance_score": score,
            "topic_score": score // 3,
            "time_score": score // 3,
            "quality_score": score // 3,
            "reason": "",
            "extracted_time": ""
        }
    
    async def filter_by_time_relevance(
        self, 
        content_items: List[Dict[str, Any]], 
        target_dates: List[str],
        tolerance_days: int = 2
    ) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        
        if not target_dates:
            return content_items
        
        filtered_items = []
        
        for item in content_items:
            # 
            extracted_time = self._extract_time_from_content(item)
            
            if extracted_time:
                # 
                is_time_relevant = any(
                    time_tool.is_date_relevant(extracted_time, target_date, tolerance_days)
                    for target_date in target_dates
                )
                
                if is_time_relevant:
                    item["extracted_time"] = extracted_time
                    filtered_items.append(item)
                else:
                    logger.info(f"[{self.name}] : {extracted_time} vs {target_dates}")
            else:
                # 
                item["extracted_time"] = ""
                filtered_items.append(item)
        
        return filtered_items
    
    def _extract_time_from_content(self, item: Dict[str, Any]) -> Optional[str]:
        """TODO: Add docstring."""
        text = f"{item.get('title', '')} {item.get('content', '')}"
        
        # 
        patterns = [
            r'(\d{4})(\d{1,2})(\d{1,2})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{1,2})(\d{1,2})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                match = matches[0]
                if len(match) == 3:  # 
                    year, month, day = match
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif len(match) == 2:  # 
                    month, day = match
                    current_year = datetime.now().year
                    return f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None