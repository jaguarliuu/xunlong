"""
 - 
"""
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
import json
import re

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager


class FictionOutlineGenerator:
    """TODO: Add docstring."""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""

    async def generate_outline(
        self,
        query: str,
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        logger.info(f"[{self.name}] ")

        try:
            # 
            outline_prompt = self._build_outline_prompt(query, elements, requirements)

            # LLM
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                outline_prompt,
                ""
            )

            # 
            outline = self._parse_outline_response(response)

            # 
            outline = self._validate_and_optimize(outline, elements, requirements)

            logger.info(f"[{self.name}]  {len(outline['chapters'])} ")

            return {
                "outline": outline,
                "total_chapters": len(outline["chapters"]),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return {
                "outline": self._get_fallback_outline(elements, requirements),
                "total_chapters": 0,
                "status": "error",
                "error": str(e)
            }

    def _build_outline_prompt(
        self,
        query: str,
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""

        genre = requirements.get("genre", "")
        length = requirements.get("length", "short")
        constraints = requirements.get("constraints", [])

        # 
        elements_summary = self._format_elements(elements)

        # 
        chapter_count = self._get_chapter_count(length)

        prompt = f"""# 

## 
{query}

## 
- ****: {genre}
- ****: {length} ( {chapter_count} )
- ****: {', '.join(constraints) if constraints else ''}

## 

{elements_summary}

## 



### 


1. ****: 1
2. ****: 
3. ****: 
4. ****: 1-2
5. ****: 
6. ****: /
7. ****: 

### 

- **** (1): 
- **** (): 
- **** (2): 
- **** (1): 

## 

{self._get_genre_outline_requirements(genre, constraints)}

## 

JSON

```json
{{
  "title": "",
  "synopsis": "",
  "chapters": [
    {{
      "id": 1,
      "title": "",
      "writing_points": "",
      "key_scenes": ["1", "2"],
      "characters_involved": ["A", "B"],
      "suspense": "",
      "word_count": 1000
    }}
  ]
}}
```


"""

        return prompt

    def _get_genre_outline_requirements(self, genre: str, constraints: List[str]) -> str:
        """TODO: Add docstring."""

        requirements_map = {
            "": """
### 

- ****: 1-2
- ****: 
- ****: 
- ****: 


- 1: 
- 2: 
- : 
- 2: 
- 1: 
""",
            "": """
### 

- ****: 
- ****: 
- ****: 
""",
            "": """
### 

- ****: 
- ****: 
- ****: 
"""
        }

        return requirements_map.get(genre, "")

    def _get_chapter_count(self, length: str) -> int:
        """TODO: Add docstring."""
        length_map = {
            "short": 5,      #  5
            "medium": 12,    #  12
            "long": 30       #  30
        }
        return length_map.get(length, 5)

    def _format_elements(self, elements: Dict[str, Any]) -> str:
        """TODO: Add docstring."""

        formatted = []

        # 
        time_info = elements.get("time", {})
        formatted.append(f"****: {time_info.get('period', '')}")

        # 
        place_info = elements.get("place", {})
        formatted.append(f"****: {place_info.get('main_location', '')}")
        formatted.append(f"  : {place_info.get('description', '')}")

        # 
        characters = elements.get("characters", [])
        formatted.append(f"\n**** ({len(characters)} ):")
        for char in characters[:6]:  # 6
            name = char.get("name", "")
            role = char.get("role", "")
            occupation = char.get("occupation", "")
            formatted.append(f"  - {name} ({role}): {occupation}")

        # 
        plot = elements.get("plot", {})
        formatted.append(f"\n****: {plot.get('core_conflict', '')}")

        # 
        theme = elements.get("theme", {})
        formatted.append(f"****: {theme.get('core_theme', '')}")

        return "\n".join(formatted)

    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """TODO: Add docstring."""

        try:
            # JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                outline = json.loads(json_match.group())

                # 
                if "chapters" in outline and isinstance(outline["chapters"], list):
                    return outline

            logger.warning(f"[{self.name}] JSON")
            return self._get_default_outline()

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return self._get_default_outline()

    def _validate_and_optimize(
        self,
        outline: Dict[str, Any],
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        chapters = outline.get("chapters", [])

        # 
        target_count = self._get_chapter_count(requirements.get("length", "short"))

        if len(chapters) < target_count - 2:
            logger.warning(f"[{self.name}]  ({len(chapters)} < {target_count})")
            # TODO: 

        # 
        for i, chapter in enumerate(chapters):
            if "id" not in chapter:
                chapter["id"] = i + 1
            if "word_count" not in chapter:
                chapter["word_count"] = 800

        outline["chapters"] = chapters

        return outline

    def _get_default_outline(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "title": "",
            "synopsis": "",
            "chapters": [
                {
                    "id": 1,
                    "title": "",
                    "writing_points": "",
                    "key_scenes": ["", ""],
                    "characters_involved": [""],
                    "suspense": "",
                    "word_count": 1000
                },
                {
                    "id": 2,
                    "title": "",
                    "writing_points": "",
                    "key_scenes": ["", ""],
                    "characters_involved": ["", "", ""],
                    "suspense": "",
                    "word_count": 1000
                }
            ]
        }

    def _get_fallback_outline(
        self,
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return self._get_default_outline()
