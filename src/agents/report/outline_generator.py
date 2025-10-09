"""
 - 
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
import json
import re

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager


class OutlineGenerator:
    """TODO: Add docstring."""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""

    async def generate_outline(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        synthesis_results: Optional[Dict[str, Any]] = None,
        report_type: str = "comprehensive",
        refined_subtasks: Optional[List[Dict[str, Any]]] = None  # NEW
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        logger.info(f"[{self.name}]  (: {report_type})")

        # NEW: Log if using refined subtasks
        if refined_subtasks:
            logger.info(f"[{self.name}]  {len(refined_subtasks)} ")

        try:
            # 
            outline_prompt = self._build_outline_prompt(
                query, search_results, synthesis_results, report_type
            )

            # LLM
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                outline_prompt,
                ""
            )

            # 
            outline = self._parse_outline_response(response)

            # 
            outline = self._validate_and_optimize_outline(outline, report_type)

            logger.info(f"[{self.name}]  {len(outline['sections'])} ")

            return {
                "outline": outline,
                "total_sections": len(outline["sections"]),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return {
                "outline": self._get_fallback_outline(report_type),
                "total_sections": 0,
                "status": "error",
                "error": str(e)
            }

    def _build_outline_prompt(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        synthesis_results: Optional[Dict[str, Any]],
        report_type: str
    ) -> str:
        """TODO: Add docstring."""

        # 
        results_summary = self._summarize_search_results(search_results[:10])

        # 
        synthesis_summary = ""
        if synthesis_results:
            if isinstance(synthesis_results, dict):
                synthesis_summary = synthesis_results.get("report_content", "")[:500]
            elif isinstance(synthesis_results, str):
                synthesis_summary = synthesis_results[:500]

        prompt = f"""# 

## 
{query}

## 
{report_type}

## 
###  ({len(search_results)} )
{results_summary}

### 
{synthesis_summary}

## 



1. ****: 
2. ****: 3-6 section
3. ****:
   - id: 1
   - title: 
   - requirements: 
   - suggested_sources: 
   - word_count: 
   - importance: 0.0-1.0

## 

- **comprehensive** (): 
  - :         
  - :  500-800 

- **daily** (): 
  - :       
  - :  300-500 

- **analysis** (): 
  - :       
  - :  400-600 

- **research** (): 
  - :           
  - :  600-1000 

## 

JSON:

```json
{{
  "title": "",
  "sections": [
    {{
      "id": 1,
      "title": "",
      "requirements": "",
      "suggested_sources": ["1", "2"],
      "word_count": 500,
      "importance": 0.9
    }}
  ]
}}
```

:
- 
- requirements 
- 
- 
"""

        return prompt

    def _summarize_search_results(self, results: List[Dict[str, Any]]) -> str:
        """TODO: Add docstring."""
        if not results:
            return ""

        summaries = []
        for i, result in enumerate(results[:10], 1):
            title = result.get("title", "")
            url = result.get("url", "")
            content_preview = result.get("content", "")[:100]

            summaries.append(f"{i}. {title}\n   : {url}\n   : {content_preview}...")

        return "\n\n".join(summaries)

    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            # JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                outline = json.loads(json_str)

                # 
                if "title" in outline and "sections" in outline:
                    return outline

            logger.warning(f"[{self.name}] JSON")
            return self._get_fallback_outline("comprehensive")

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return self._get_fallback_outline("comprehensive")

    def _validate_and_optimize_outline(
        self,
        outline: Dict[str, Any],
        report_type: str
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        sections = outline.get("sections", [])

        # 
        if len(sections) < 3:
            logger.warning(f"[{self.name}]  ({len(sections)})")
            sections = self._add_missing_sections(sections, report_type)

        if len(sections) > 6:
            logger.warning(f"[{self.name}]  ({len(sections)})6")
            sections = sections[:6]

        # 
        for i, section in enumerate(sections):
            # id
            if "id" not in section:
                section["id"] = i + 1

            # 
            if "title" not in section or not section["title"]:
                section["title"] = f"{i+1}"

            # 
            if "requirements" not in section or not section["requirements"]:
                section["requirements"] = f"{outline.get('title', '')}{section['title']}"

            # 
            if "word_count" not in section:
                section["word_count"] = 500

            # 
            if "importance" not in section:
                section["importance"] = 1.0 / len(sections)

            # 
            if "suggested_sources" not in section:
                section["suggested_sources"] = []

        outline["sections"] = sections

        return outline

    def _add_missing_sections(
        self,
        sections: List[Dict[str, Any]],
        report_type: str
    ) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""

        default_sections = {
            "comprehensive": ["", "", "", "", ""],
            "daily": ["", "", "", ""],
            "analysis": ["", "", "", ""],
            "research": ["", "", "", "", "", ""]
        }

        template = default_sections.get(report_type, default_sections["comprehensive"])

        # 
        if not sections:
            return [
                {
                    "id": i + 1,
                    "title": title,
                    "requirements": f"{title}",
                    "word_count": 500,
                    "importance": 1.0 / len(template),
                    "suggested_sources": []
                }
                for i, title in enumerate(template)
            ]

        return sections

    def _get_fallback_outline(self, report_type: str) -> Dict[str, Any]:
        """TODO: Add docstring."""

        default_outlines = {
            "comprehensive": {
                "title": "",
                "sections": [
                    {
                        "id": 1,
                        "title": "",
                        "requirements": "",
                        "word_count": 300,
                        "importance": 0.15,
                        "suggested_sources": []
                    },
                    {
                        "id": 2,
                        "title": "",
                        "requirements": "",
                        "word_count": 800,
                        "importance": 0.35,
                        "suggested_sources": []
                    },
                    {
                        "id": 3,
                        "title": "",
                        "requirements": "",
                        "word_count": 700,
                        "importance": 0.30,
                        "suggested_sources": []
                    },
                    {
                        "id": 4,
                        "title": "",
                        "requirements": "",
                        "word_count": 300,
                        "importance": 0.20,
                        "suggested_sources": []
                    }
                ]
            },
            "daily": {
                "title": "AI",
                "sections": [
                    {
                        "id": 1,
                        "title": "",
                        "requirements": "",
                        "word_count": 300,
                        "importance": 0.25,
                        "suggested_sources": []
                    },
                    {
                        "id": 2,
                        "title": "",
                        "requirements": "2-3",
                        "word_count": 500,
                        "importance": 0.50,
                        "suggested_sources": []
                    },
                    {
                        "id": 3,
                        "title": "",
                        "requirements": "",
                        "word_count": 200,
                        "importance": 0.25,
                        "suggested_sources": []
                    }
                ]
            }
        }

        return default_outlines.get(report_type, default_outlines["comprehensive"])
