""""""

import json
from typing import Dict, Any, List
from loguru import logger

from .base import BaseAgent, AgentConfig
from ..llm import LLMManager, PromptManager


class ContentSynthesizerAgent(BaseAgent):
    """ - """
    
    def __init__(
        self, 
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="",
            description="",
            llm_config_name="content_synthesizer",
            temperature=0.7,
            max_tokens=6000
        )
        
        super().__init__(llm_manager, prompt_manager, config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """"""
        try:
            query = input_data.get("query", "")
            search_results = input_data.get("search_results", [])
            analysis_results = input_data.get("analysis_results", {})
            
            logger.info(f": {query}")
            
            # 
            system_prompt = self.get_prompt("agents/content_synthesizer/system")
            
            # 
            synthesis_data = {
                "query": query,
                "search_results_count": len(search_results),
                "key_insights": analysis_results.get("result", {}).get("key_insights", []),
                "content_themes": analysis_results.get("result", {}).get("content_themes", []),
                "top_results": []
            }
            
            # 3
            for i, result in enumerate(search_results[:3]):
                synthesis_data["top_results"].append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content_summary": result.get("content", "")[:500] + "..." if result.get("content") else ""
                })
            
            # 
            user_prompt = f"""
"{query}"

:
{json.dumps(synthesis_data, ensure_ascii=False, indent=2)}


1. 
2. 
3. 
4. 
5. 

JSONreport_content
"""
            
            # LLM
            response = await self.get_llm_response(user_prompt, system_prompt)
            
            # JSON
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # JSON
                result = {
                    "report_content": response,
                    "executive_summary": "",
                    "main_findings": [""],
                    "detailed_analysis": response,
                    "conclusions": [""],
                    "sources": [r.get("url", "") for r in search_results[:3]]
                }
            
            # 
            if "report_content" not in result:
                result["report_content"] = result.get("detailed_analysis", response)
            
            # 
            result["query"] = query
            result["synthesis_timestamp"] = "2025-09-25"  # 
            result["sources_count"] = len(search_results)
            result["analysis_quality"] = "good" if analysis_results.get("status") == "success" else "limited"
            
            logger.info(f":  {len(result.get('report_content', ''))} ")
            
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
                    "report_content": f"'{input_data.get('query', '')}': {e}",
                    "executive_summary": "",
                    "main_findings": [],
                    "detailed_analysis": "",
                    "conclusions": [""],
                    "sources": [],
                    "query": input_data.get("query", ""),
                    "sources_count": 0,
                    "analysis_quality": "failed"
                }
            }