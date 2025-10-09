"""TODO: Add docstring."""

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
        """TODO: Add docstring."""
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

    async def synthesize_subtask(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        analysis_results: Dict[str, Any],
        subtask_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        NEW METHOD: Synthesize content for a single subtask.
        This creates a refined, well-organized summary specific to this subtask.
        """
        try:
            logger.info(f"[{self.name}]  '{query}'  {len(search_results)} ")

            if not search_results:
                return {
                    "status": "warning",
                    "agent": self.name,
                    "result": {
                        "synthesized_content": f" '{query}' ",
                        "key_points": [],
                        "summary": "",
                        "sources": []
                    }
                }

            # Prepare synthesis prompt
            system_prompt = f"""
: {self.name}

:

1.
2.
3.
4.
5.

Markdown
"""

            # Extract key information from analysis
            analysis_data = analysis_results.get("result", {})
            key_insights = analysis_data.get("key_insights", [])
            content_themes = analysis_data.get("content_themes", [])
            quality_score = analysis_data.get("quality_score", 0.5)

            # Prepare content snippets from search results
            content_snippets = []
            sources = []
            for i, result in enumerate(search_results[:5]):  # Top 5 results
                content = result.get("content", "") or result.get("snippet", "")
                if content:
                    content_snippets.append({
                        "source": result.get("title", f" {i+1}"),
                        "url": result.get("url", ""),
                        "content": content[:800] + "..." if len(content) > 800 else content
                    })
                    sources.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", "")
                    })

            user_prompt = f"""
#

****: {query}
****: {subtask_context.get('title', query)}
****: {subtask_context.get('description', '')}

#

**: {', '.join(key_insights) if key_insights else ''}
**: {', '.join(content_themes) if content_themes else ''}
**: {quality_score:.2f}

#

{json.dumps(content_snippets, ensure_ascii=False, indent=2)}

#

Markdown

1.
2. 3-5
3. :
   -
   -
   - URL
4. 800-1500

JSON
{{
  "synthesized_content": "Markdown",
  "key_points": ["", "", ""],
  "summary": "2-3",
  "sources": [{{"title": "", "url": ""}}],
  "confidence": 0.85
}}
"""

            # Get LLM synthesis
            response = await self.get_llm_response(user_prompt, system_prompt)

            # Parse JSON response
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                logger.warning(f"[{self.name}] JSON Markdown")
                # If JSON parsing fails, treat entire response as synthesized content
                result = {
                    "synthesized_content": response,
                    "key_points": key_insights[:3] if key_insights else [""],
                    "summary": response[:200] + "..." if len(response) > 200 else response,
                    "sources": sources[:3],
                    "confidence": 0.7
                }

            # Add metadata
            result["subtask_id"] = subtask_context.get("id", "")
            result["subtask_title"] = subtask_context.get("title", query)
            result["sources_count"] = len(sources)
            result["synthesized_at"] = "2025-09-25"
            result["word_count"] = len(result.get("synthesized_content", ""))

            # Ensure sources field exists
            if "sources" not in result:
                result["sources"] = sources[:5]

            logger.info(f"[{self.name}]  '{query}'  {result.get('word_count', 0)} ")

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
                    "synthesized_content": f" '{query}' : {e}",
                    "key_points": [],
                    "summary": "",
                    "sources": [],
                    "subtask_id": subtask_context.get("id", ""),
                    "subtask_title": subtask_context.get("title", query),
                    "sources_count": 0,
                    "word_count": 0,
                    "confidence": 0.0
                }
            }