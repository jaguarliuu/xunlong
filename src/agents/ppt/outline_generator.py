"""
PPT - PPT
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager
from ..base import BaseAgent, AgentConfig


class PPTOutlineGenerator(BaseAgent):
    """PPT - PPT"""

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="PPT",
            description="PPT",
            llm_config_name="outline_generator",
            temperature=0.7,
            max_tokens=3000
        )
        super().__init__(llm_manager, prompt_manager, config)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent"""
        return await self.generate_outline(
            topic=input_data.get("topic", ""),
            style=input_data.get("style", "business"),
            slides=input_data.get("slides", 10),
            search_results=input_data.get("search_results", []),
            depth=input_data.get("depth", "medium")
        )

    async def generate_outline(
        self,
        topic: str,
        style: str,
        slides: int,
        search_results: List[Dict[str, Any]],
        depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        PPT

        Args:
            topic: PPT
            style: PPT (ted/business/academic/creative/simple)
            slides: 
            search_results: 
            depth: 

        Returns:
            {
                "status": "success/error",
                "outline": {
                    "title": "PPT",
                    "subtitle": "",
                    "slides": [
                        {
                            "slide_number": 1,
                            "type": "cover/content/section/conclusion",
                            "title": "",
                            "key_points": ["1", "2"],
                            "content_density": "minimal/medium/detailed"
                        }
                    ]
                }
            }
        """
        try:
            logger.info(f"[{self.name}] PPT (: {topic}, : {style}, : {slides})")

            # 
            system_prompt = self._get_system_prompt(style)
            user_prompt = self._build_user_prompt(topic, style, slides, search_results, depth)

            # LLM
            response = await self.get_llm_response(user_prompt, system_prompt)

            # 
            outline = self._parse_outline(response, topic, slides)

            logger.info(f"[{self.name}]  {len(outline['slides'])} ")

            return {
                "status": "success",
                "outline": outline
            }

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _get_system_prompt(self, style: str) -> str:
        """TODO: Add docstring."""

        style_guides = {
            "red": """
REDPPT
RED
- 
- 
- 
- 
""",
            "business": """
PPT

- 
- 
- 
- 
""",
            "academic": """
PPT

- 
- 
- 
- 
""",
            "creative": """
PPT

- 
- 
- 
- 
""",
            "simple": """
PPT

- 
- 
- 
- 
"""
        }

        base_prompt = style_guides.get(style, style_guides["business"])

        return base_prompt + """

1. 
2. PPT
3. 
4. 

JSON
{
  "title": "PPT",
  "subtitle": "",
  "slides": [
    {
      "slide_number": 1,
      "type": "cover/content/section/conclusion",
      "title": "",
      "key_points": ["1", "2", "3"],
      "content_density": "minimal/medium/detailed"
    }
  ]
}


- slide_number1
- typecover(), content(), section(), conclusion()
- content_density
  * red/simple: minimal (1-2)
  * business/creative: medium (+3-5)
  * academic: detailed (++)
"""

    def _build_user_prompt(
        self,
        topic: str,
        style: str,
        slides: int,
        search_results: List[Dict[str, Any]],
        depth: str
    ) -> str:
        """TODO: Add docstring."""

        prompt = f"""PPT

{topic}
{style}
{slides}
{depth}


"""

        # 
        for i, result in enumerate(search_results[:5], 1):  # 5
            title = result.get("title", "")
            snippet = result.get("snippet", result.get("full_content", ""))[:200]
            prompt += f"\n{i}. {title}\n   {snippet}...\n"

        prompt += f"""

{style}
1.  (type: cover)
2.  (type: conclusion)
3. 
4. {style}
5. {slides}2

JSON"""

        return prompt

    def _parse_outline(self, response: str, topic: str, target_slides: int) -> Dict[str, Any]:
        """LLM"""
        import json
        import re

        try:
            # JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                outline = json.loads(json_match.group(0))
            else:
                raise ValueError("JSON")

            # 
            if "title" not in outline:
                outline["title"] = topic

            if "slides" not in outline or not outline["slides"]:
                raise ValueError("slides")

            # slide_number
            for i, slide in enumerate(outline["slides"], 1):
                slide["slide_number"] = i

            return outline

        except Exception as e:
            logger.error(f": {e}, ")
            # 
            return self._get_default_outline(topic, target_slides)

    def _get_default_outline(self, topic: str, slides: int) -> Dict[str, Any]:
        """TODO: Add docstring."""
        default_slides = [
            {
                "slide_number": 1,
                "type": "cover",
                "title": topic,
                "key_points": [],
                "content_density": "minimal"
            }
        ]

        # 
        for i in range(2, slides):
            default_slides.append({
                "slide_number": i,
                "type": "content",
                "title": f"{i-1}",
                "key_points": ["1", "2", "3"],
                "content_density": "medium"
            })

        # 
        default_slides.append({
            "slide_number": slides,
            "type": "conclusion",
            "title": "",
            "key_points": [""],
            "content_density": "medium"
        })

        return {
            "title": topic,
            "subtitle": "",
            "slides": default_slides
        }
