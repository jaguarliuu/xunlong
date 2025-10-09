"""TODO: Add docstring."""

import json
from typing import Dict, Any, List
from loguru import logger

from .base import BaseAgent, AgentConfig
from ..llm import LLMManager, PromptManager


class SearchAnalyzerAgent(BaseAgent):
    """ - """
    
    def __init__(
        self, 
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="",
            description="",
            llm_config_name="search_analyzer",
            temperature=0.5,
            max_tokens=4000
        )
        
        super().__init__(llm_manager, prompt_manager, config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            query = input_data.get("query", "")
            search_results = input_data.get("search_results", [])
            
            logger.info(f": {len(search_results)} ")
            
            if not search_results:
                return {
                    "status": "warning",
                    "agent": self.name,
                    "result": {
                        "analysis_summary": "",
                        "key_insights": [],
                        "relevance_scores": [],
                        "content_themes": [],
                        "recommendations": [""]
                    }
                }
            
            # 
            system_prompt = self.get_prompt("agents/search_analyzer/system")
            
            # 
            results_summary = []
            for i, result in enumerate(search_results[:5]):  # 5
                summary = {
                    "index": i + 1,
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content_preview": result.get("content", "")[:300] + "..." if result.get("content") else ""
                }
                results_summary.append(summary)
            
            # 
            user_prompt = f"""
"{query}"

:
{json.dumps(results_summary, ensure_ascii=False, indent=2)}


1. 
2. 
3. 1-10
4. 
5. 

JSON
"""
            
            # LLM
            response = await self.get_llm_response(user_prompt, system_prompt)
            
            # JSON
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # JSON
                result = {
                    "analysis_summary": "",
                    "key_insights": [""],
                    "relevance_scores": [8] * len(search_results),
                    "content_themes": [""],
                    "recommendations": [""],
                    "raw_response": response
                }
            
            # 
            result["total_results"] = len(search_results)
            result["analyzed_results"] = min(len(search_results), 5)
            
            logger.info(f": {result.get('analysis_summary', '')}")
            
            return {
                "status": "success",
                "agent": self.name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f": {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "result": {
                    "analysis_summary": "",
                    "key_insights": [],
                    "relevance_scores": [],
                    "content_themes": [],
                    "recommendations": [""],
                    "total_results": len(input_data.get("search_results", [])),
                    "analyzed_results": 0
                }
            }