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

class ReportGenerator:
    """TODO: Add docstring."""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
        query = data.get("query", "")
        search_results = data.get("search_results", [])
        synthesis_results = data.get("synthesis_results", {})
        report_type = data.get("report_type", "general")

        # synthesis_resultssearch_data
        if isinstance(synthesis_results, str):
            # 
            search_data = {"all_content": [{"content": synthesis_results, "source": "synthesis"}]}
        elif isinstance(synthesis_results, dict) and synthesis_results:
            # report_contentdetailed_analysis
            content = synthesis_results.get("report_content") or synthesis_results.get("detailed_analysis", "")
            if content:
                search_data = {"all_content": [{"content": content, "source": "synthesis", **synthesis_results}]}
            elif "all_content" in synthesis_results:
                # 
                search_data = synthesis_results
            else:
                # 
                search_data = {"all_content": search_results}
        else:
            # 
            search_data = {"all_content": search_results}

        result = await self.generate_report(query, search_data, report_type)
        return {
            "agent": self.name,
            "result": result,
            "status": "success" if result.get("report") else "failed"
        }
        
    async def generate_report(
        self, 
        query: str, 
        search_results: Dict[str, Any],
        report_type: str = "comprehensive",
        time_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        
        logger.info(f"[{self.name}]  {report_type} ")
        
        # 
        if not time_context:
            time_context = time_tool.parse_date_query(query)
        
        try:
            # 
            content_items = search_results.get("all_content", [])
            
            if not content_items:
                logger.warning(f"[{self.name}] ")
                return self._generate_empty_report(query, report_type)
            
            # 
            report_template = self._get_report_template(report_type, time_context)
            
            # 
            report_prompt = self._build_report_prompt(
                query, content_items, report_template, time_context
            )
            
            # LLM
            # 
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                report_prompt,
                ""
            )
            
            # 
            report = self._parse_report_response(response, report_type)
            
            # 
            report["metadata"] = {
                "query": query,
                "report_type": report_type,
                "generation_time": datetime.now().isoformat(),
                "content_sources": len(content_items),
                "time_context": time_context,
                "word_count": len(report.get("content", ""))
            }
            
            logger.info(f"[{self.name}] : {report['metadata']['word_count']}")
            
            return {
                "report": report,
                "status": "success",
                "sources_used": len(content_items)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return {
                "report": self._generate_error_report(query, str(e)),
                "status": "error",
                "error": str(e)
            }
    
    def _get_report_template(self, report_type: str, time_context: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        
        # 
        if "" in report_type or "daily" in report_type.lower():
            template_name = "daily"
        elif "" in report_type or "analysis" in report_type.lower():
            template_name = "analysis"
        elif "" in report_type or "research" in report_type.lower():
            template_name = "research"
        else:
            template_name = "general"
        
        # 
        if time_context.get("extracted_dates") and template_name == "general":
            template_name = "daily"
        
        return self.prompt_manager.get_prompt(
            f"agents/report_generator/{template_name}_system",
            default=self._get_default_template(template_name)
        )
    
    def _get_default_template(self, template_name: str) -> str:
        """TODO: Add docstring."""
        templates = {
            "daily": """
# {title}

##  
- : {report_date}
- : {time_range}

##  

{main_events}

##  

{detailed_analysis}

##  

{important_links}

##  

{summary}
            """,
            "analysis": """
# {title}

##  
{analysis_target}

##  
{key_findings}

##  
{detailed_analysis}

##  
{insights_recommendations}

##  
{references}
            """,
            "research": """
# {title}

##  
{research_background}

##  
{methodology}

##  
{research_results}

##  
{result_analysis}

##  
{conclusions}

##  
{references}
            """,
            "general": """
# {title}

##  
{overview}

##  
{detailed_content}

##  
{key_points}

##  
{related_resources}

##  
{summary}
            """
        }
        
        return templates.get(template_name, templates["general"])
    
    def _build_report_prompt(
        self, 
        query: str, 
        content_items: List[Dict[str, Any]], 
        template: str,
        time_context: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""
        
        # 
        system_prompt = self.prompt_manager.get_prompt(
            "agents/report_generator/general_system",
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
- 
- 
- """
        )
        
        # 
        content_summary = self._prepare_content_summary(content_items)
        
        # 
        time_info = time_context.get("time_context", "")
        extracted_dates = time_context.get("extracted_dates", [])
        current_time = time_context.get("current_time", {})
        
        prompt = f"""{system_prompt}

## 
: {query}

## 
{time_info}
: {current_time.get('current_datetime', '')}
: {[d['formatted'] for d in extracted_dates] if extracted_dates else ''}

## 
 {len(content_items)} :

{content_summary}

## 
:

{template}

## 
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 2000-4000

: 
"""
        return prompt
    
    def _prepare_content_summary(self, content_items: List[Dict[str, Any]]) -> str:
        """TODO: Add docstring."""
        summaries = []
        
        for i, item in enumerate(content_items[:20]):  # 20
            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")[:500]  # 
            extracted_time = item.get("extracted_time", "")
            
            summary = f"""
 {i+1}:
: {title}
: {extracted_time}
URL: {url}
: {content}...
---
"""
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def _parse_report_response(self, response: str, report_type: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            # 
            title_match = response.split('\n')[0] if response else ""
            title = title_match.replace('#', '').strip() if title_match.startswith('#') else f"{report_type}"
            
            return {
                "title": title,
                "content": response,
                "type": report_type,
                "sections": self._extract_sections(response)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return {
                "title": f"{report_type}",
                "content": response,
                "type": report_type,
                "sections": []
            }
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """TODO: Add docstring."""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('##'):
                # 
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content).strip()
                    })
                
                # 
                current_section = line.replace('##', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # 
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content).strip()
            })
        
        return sections
    
    def _generate_empty_report(self, query: str, report_type: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "report": {
                "title": f"'{query}'{report_type}",
                "content": f"'{query}'",
                "type": report_type,
                "sections": []
            },
            "status": "empty",
            "sources_used": 0
        }
    
    def _generate_error_report(self, query: str, error: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "title": f"",
            "content": f"'{query}': {error}",
            "type": "error",
            "sections": [],
            "metadata": {
                "generation_time": datetime.now().isoformat(),
                "error": error
            }
        }