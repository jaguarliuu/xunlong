"""
PPT - PPT
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager
from ..base import BaseAgent, AgentConfig


class SlideContentGenerator(BaseAgent):
    """PPT - """

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="PPT",
            description="PPT",
            llm_config_name="slide_content_generator",
            temperature=0.7,
            max_tokens=2000
        )
        super().__init__(llm_manager, prompt_manager, config)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent"""
        return await self.generate_slide_content(
            slide_outline=input_data.get("slide_outline", {}),
            style=input_data.get("style", "business"),
            available_content=input_data.get("available_content", []),
            context=input_data.get("context")
        )

    async def generate_slide_content(
        self,
        slide_outline: Dict[str, Any],
        style: str,
        available_content: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        PPT

        Args:
            slide_outline: 
            style: PPT
            available_content: 
            context: 

        Returns:
            {
                "slide_number": 1,
                "type": "cover",
                "title": "",
                "subtitle": "",
                "content": {
                    "points": ["1", "2"],
                    "details": {"1": ""},
                    "visuals": [{"type": "image/chart", "description": "..."}]
                }
            }
        """
        try:
            slide_number = slide_outline.get("slide_number")
            slide_type = slide_outline.get("type", "content")

            logger.info(f"[{self.name}]  {slide_number}  (: {slide_type})")

            # 
            if slide_type == "cover":
                result = await self._generate_cover_slide(slide_outline, style)
            elif slide_type == "conclusion":
                result = await self._generate_conclusion_slide(slide_outline, style, context)
            else:  # content / section
                result = await self._generate_content_slide(
                    slide_outline, style, available_content, context
                )

            return result

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return self._get_fallback_slide(slide_outline)

    async def _generate_cover_slide(
        self,
        slide_outline: Dict[str, Any],
        style: str
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "slide_number": slide_outline.get("slide_number", 1),
            "type": "cover",
            "title": slide_outline.get("title", ""),
            "subtitle": "",
            "content": {
                "points": [],
                "details": {},
                "visuals": []
            }
        }

    async def _generate_conclusion_slide(
        self,
        slide_outline: Dict[str, Any],
        style: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        system_prompt = f"""PPT{style}
PPT"""

        user_prompt = f"""

{slide_outline.get('title', '')}
{len(slide_outline.get('key_points', []))}

2-4

JSON
{{
  "points": ["1", "2", "3"]
}}
"""

        response = await self.get_llm_response(user_prompt, system_prompt)

        # 
        import json
        import re
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group(0))
                points = data.get("points", [""])
            else:
                points = [""]
        except:
            points = [""]

        return {
            "slide_number": slide_outline.get("slide_number"),
            "type": "conclusion",
            "title": slide_outline.get("title", ""),
            "subtitle": "",
            "content": {
                "points": points,
                "details": {},
                "visuals": []
            }
        }

    async def _generate_content_slide(
        self,
        slide_outline: Dict[str, Any],
        style: str,
        available_content: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        title = slide_outline.get("title", "")
        key_points = slide_outline.get("key_points", [])
        content_density = slide_outline.get("content_density", "medium")

        # 
        density_guides = {
            "minimal": "1-2",
            "medium": "3-5",
            "detailed": "3-5"
        }

        system_prompt = f"""PPT{style}
{density_guides.get(content_density, density_guides['medium'])}"""

        # 
        relevant_content = self._extract_relevant_content(title, available_content)

        user_prompt = f"""PPT

{title}
{style}
{content_density}


{relevant_content}



JSON
{{
  "points": ["1", "2", "3"],
  "details": {{"1": "content_densitydetailed"}},
  "visuals": [{{"type": "chart/image", "description": ""}}]
}}


- pointscontent_densityminimal: 1-2, medium: 3-5, detailed: 3-5
- minimaldetails
- visuals
"""

        response = await self.get_llm_response(user_prompt, system_prompt)

        # 
        import json
        import re
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = {"points": key_points, "details": {}, "visuals": []}
        except Exception as e:
            logger.warning(f": {e}, ")
            data = {"points": key_points, "details": {}, "visuals": []}

        return {
            "slide_number": slide_outline.get("slide_number"),
            "type": slide_outline.get("type", "content"),
            "title": title,
            "subtitle": "",
            "content": {
                "points": data.get("points", key_points),
                "details": data.get("details", {}),
                "visuals": data.get("visuals", [])
            }
        }

    def _extract_relevant_content(
        self,
        title: str,
        available_content: List[Dict[str, Any]],
        max_length: int = 500
    ) -> str:
        """TODO: Add docstring."""

        relevant_texts = []
        title_lower = title.lower()

        for item in available_content[:10]:  # 10
            content = item.get("full_content", item.get("snippet", ""))
            # 
            if any(word in content.lower() for word in title_lower.split() if len(word) > 2):
                relevant_texts.append(content[:300])

        combined = "\n\n".join(relevant_texts)
        return combined[:max_length] if combined else ""

    def _get_fallback_slide(self, slide_outline: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "slide_number": slide_outline.get("slide_number"),
            "type": slide_outline.get("type", "content"),
            "title": slide_outline.get("title", ""),
            "subtitle": "",
            "content": {
                "points": slide_outline.get("key_points", ["..."]),
                "details": {},
                "visuals": []
            }
        }
