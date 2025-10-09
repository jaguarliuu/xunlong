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

    async def analyze_subtask(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        subtask_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        NEW METHOD: Analyze search results for a single subtask.
        This provides more focused and detailed analysis than analyzing all results at once.
        """
        try:
            logger.info(f"[{self.name}]  '{query}'  {len(search_results)} ")

            if not search_results:
                return {
                    "status": "warning",
                    "agent": self.name,
                    "result": {
                        "analysis_summary": f" '{query}' ",
                        "key_insights": [],
                        "quality_score": 0.0,
                        "content_themes": [],
                        "most_relevant_results": []
                    }
                }

            # Prepare subtask-specific analysis prompt
            system_prompt = f"""
: {self.name}

:

1.
2.
3.
4.
5.

JSON
"""

            # Summarize search results for analysis
            results_summary = []
            for i, result in enumerate(search_results):
                content = result.get("content", "") or result.get("snippet", "")
                results_summary.append({
                    "index": i + 1,
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content_preview": content[:400] + "..." if len(content) > 400 else content,
                    "content_length": len(content),
                    "has_images": result.get("has_images", False),
                    "image_count": result.get("image_count", 0)
                })

            user_prompt = f"""
#

****: {query}
****: {subtask_context.get('title', query)}
****: {subtask_context.get('description', '')}

#

{json.dumps(results_summary, ensure_ascii=False, indent=2)}

#

JSON
{{
  "analysis_summary": "",
  "key_insights": ["", "", ""],
  "quality_score": 0.0,
  "content_themes": ["", ""],
  "most_relevant_results": [1, 2, 3],
  "recommendations": ""
}}
"""

            # Get LLM analysis
            response = await self.get_llm_response(user_prompt, system_prompt)

            # Parse JSON response
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                logger.warning(f"[{self.name}] JSON JSON")
                result = {
                    "analysis_summary": response[:500],
                    "key_insights": [""],
                    "quality_score": 0.7,
                    "content_themes": [""],
                    "most_relevant_results": list(range(1, min(4, len(search_results) + 1))),
                    "recommendations": ""
                }

            # Add metadata
            result["subtask_id"] = subtask_context.get("id", "")
            result["subtask_title"] = subtask_context.get("title", query)
            result["total_results"] = len(search_results)
            result["analyzed_at"] = "2025-09-25"

            logger.info(f"[{self.name}]  '{query}'  : {result.get('quality_score', 0.0):.2f}")

            return {
                "status": "success",
                "agent": self.name,
                "result": result
            }

        except Exception as e:
            logger.error(f"[{self.name}]  '{query}' : {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "result": {
                    "analysis_summary": f": {e}",
                    "key_insights": [],
                    "quality_score": 0.0,
                    "content_themes": [],
                    "most_relevant_results": [],
                    "subtask_id": subtask_context.get("id", ""),
                    "subtask_title": subtask_context.get("title", query),
                    "total_results": len(search_results)
                }
            }