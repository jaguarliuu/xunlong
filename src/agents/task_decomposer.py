"""
 - 
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..llm.manager import LLMManager
from ..llm.prompts import PromptManager
from ..tools.time_tool import time_tool

class TaskDecomposer:
    """TODO: Add docstring."""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
        query = data.get("query", "")
        time_context = data.get("time_context")
        context = data.get("context") or {}
        
        result = await self.decompose_query(query, time_context, context)
        return {
            "agent": self.name,
            "result": result,
            "status": "success" if result.get("subtasks") else "failed"
        }
        
    async def decompose_query(
        self, 
        query: str, 
        time_context: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        
        logger.info(f"[{self.name}] : {query}")
        
        # 
        if not time_context:
            time_context = time_tool.parse_date_query(query)
        else:
            # 
            base_context = time_tool.parse_date_query(query)
            time_context.setdefault("current_time", base_context.get("current_time"))
        
        # 
        time_context = self._enrich_time_context(query, time_context, context)
        
        try:
            # 
            decomposition_prompt = self._build_decomposition_prompt(query, time_context)
            
            # LLM
            # 
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                decomposition_prompt,
                ""
            )
            
            # 
            decomposition = self._parse_decomposition_response(response)

            # 
            if decomposition.get("subtasks"):
                for subtask in decomposition["subtasks"]:
                    subtask["time_context"] = time_context
                    if time_context.get("time_filter"):
                        subtask["time_filter"] = time_context["time_filter"]
                    # 
                    if time_context.get("extracted_dates"):
                        time_str = time_tool.format_time_for_search(time_context)
                        if time_str:
                            subtask["search_queries"] = [
                                f"{q} {time_str}" for q in subtask.get("search_queries", [])
                            ]
            decomposition["time_context"] = time_context
            
            logger.info(f"[{self.name}]  {len(decomposition.get('subtasks', []))} ")
            return decomposition
            
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return {
                "subtasks": [],
                "strategy": "fallback",
                "priority": "medium",
                "estimated_time": 300,
                "error": str(e)
            }

    def _enrich_time_context(
        self,
        query: str,
        time_context: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        context = context or {}
        enriched = dict(time_context or {})
        report_type = (context.get("report_type") or "").lower()
        query_lower = query.lower()

        def ensure_daily_focus():
            now_dt = datetime.now(time_tool.beijing_tz)
            extracted = {
                "year": now_dt.year,
                "month": now_dt.month,
                "day": now_dt.day,
                "formatted": now_dt.strftime("%Y-%m-%d")
            }
            enriched["extracted_dates"] = [extracted]
            enriched["query_contains_date"] = True
            enriched["relative_reference"] = enriched.get("relative_reference") or "today"
            enriched["time_filter"] = "day"
            enriched["time_context"] = (
                f" {extracted['formatted']} "
                f": {enriched['current_time']['current_datetime']}"
            )

        if not enriched.get("extracted_dates"):
            if report_type == "daily" or "" in query_lower:
                ensure_daily_focus()

        # 
        if enriched.get("extracted_dates") and not enriched.get("time_filter"):
            try:
                now_dt = datetime.now(time_tool.beijing_tz)
                first = enriched["extracted_dates"][0]
                target = datetime(
                    first["year"],
                    first["month"],
                    first["day"],
                    tzinfo=time_tool.beijing_tz
                )
                diff_days = abs((now_dt.date() - target.date()).days)
                if diff_days <= 1:
                    enriched["time_filter"] = "day"
                elif diff_days <= 7:
                    enriched["time_filter"] = "week"
                elif diff_days <= 31:
                    enriched["time_filter"] = "month"
            except Exception:
                pass

        return enriched
    
    def _build_decomposition_prompt(self, query: str, time_context: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        
        # 
        system_prompt = self.prompt_manager.get_prompt(
            "agents/task_decomposer/system",
            default="""

## 
1. 
2. 
3. 3-5
4. 

## 
- 
- 
- 
- """
        )
        
        # 
        time_info = time_context.get("time_context", "")
        extracted_dates = time_context.get("extracted_dates", [])
        
        prompt = f"""{system_prompt}

## 
: {query}

## 
{time_info}
: {[d['formatted'] for d in extracted_dates] if extracted_dates else ''}

## 
3-5
1. 
2. 
3. 
4. 

## 
JSON:
{{
    "subtasks": [
        {{
            "id": "task_1",
            "type": "search",
            "title": "",
            "description": "",
            "search_queries": ["1", "2"],
            "keywords": ["1", "2"],
            "priority": "high/medium/low",
            "expected_results": 5
        }}
    ],
    "strategy": "comprehensive/focused/exploratory",
    "priority": "high/medium/low",
    "estimated_time": 
}}


"""
        return prompt

    def _parse_decomposition_response(self, response: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            import json
            import re
            
            # JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                decomposition = json.loads(json_str)
                
                # 
                if "subtasks" in decomposition and isinstance(decomposition["subtasks"], list):
                    return decomposition
            
            # JSON
            logger.warning(f"[{self.name}] JSON")
            return self._create_default_decomposition(response)
            
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return self._create_default_decomposition(response)
    
    def _create_default_decomposition(self, query_or_response: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "subtasks": [
                {
                    "id": "default_search",
                    "type": "search",
                    "title": "",
                    "description": "",
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
