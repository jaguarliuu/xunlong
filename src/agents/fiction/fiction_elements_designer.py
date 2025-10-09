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


class FictionElementsDesigner:
    """TODO: Add docstring."""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""

    async def design_elements(
        self,
        query: str,
        requirements: Dict[str, Any],
        search_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        logger.info(f"[{self.name}] ")

        try:
            # 
            design_prompt = self._build_design_prompt(query, requirements, search_results)

            # LLM
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                design_prompt,
                ""
            )

            # 
            elements = self._parse_elements_response(response)

            # 
            elements = self._validate_and_optimize(elements, requirements)

            logger.info(f"[{self.name}] ")

            return {
                "elements": elements,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return {
                "elements": self._get_fallback_elements(requirements),
                "status": "error",
                "error": str(e)
            }

    def _build_design_prompt(
        self,
        query: str,
        requirements: Dict[str, Any],
        search_results: Optional[List[Dict[str, Any]]]
    ) -> str:
        """TODO: Add docstring."""

        genre = requirements.get("genre", "")
        length = requirements.get("length", "short")
        constraints = requirements.get("constraints", [])

        # 
        references = ""
        if search_results:
            references = self._format_references(search_results[:5])

        prompt = f"""# 

## 
: {query}

## 
- ****: {genre}
- ****: {length} ({self._get_length_desc(length)})
- ****: {', '.join(constraints) if constraints else ''}

## 
{references if references else ""}

## 

****

### 

1. ** (Time)**
   - /
   - 
   - 

2. ** (Place)**
   - 
   - 
   - 

3. ** (Characters)**
   - 
   - 3-5
   - 

4. ** (Plot)**
   - 
   - 
   - /

5. ** (Environment)**
   - 
   - 
   - 

6. ** (Theme)**
   - 
   - 
   - 

## 

{self._get_genre_specific_requirements(genre, constraints)}

## 

JSON

```json
{{
  "time": {{
    "period": "/",
    "duration": "",
    "key_moments": ["1", "2"]
  }},
  "place": {{
    "main_location": "",
    "description": "",
    "layout": "",
    "significance": ""
  }},
  "characters": [
    {{
      "role": "protagonist",
      "name": "",
      "age": ,
      "occupation": "",
      "personality": "",
      "motivation": "",
      "secret": ""
    }},
    {{
      "role": "antagonist/supporting",
      "name": "",
      ...
    }}
  ],
  "plot": {{
    "core_conflict": "",
    "inciting_incident": "",
    "turning_points": ["1", "2", "3"],
    "climax": "",
    "resolution": ""
  }},
  "environment": {{
    "social": "",
    "natural": "",
    "atmosphere": ""
  }},
  "theme": {{
    "core_theme": "",
    "message": "",
    "tone": ""
  }}
}}
```

## 

1. ****: 
2. ****: 
3. ****: 
4. ****: 


"""

        return prompt

    def _get_genre_specific_requirements(self, genre: str, constraints: List[str]) -> str:
        """TODO: Add docstring."""

        requirements_map = {
            "": """
### 

- ****: /3
- ****:
- ****:
- ****:
- ****:
- ****:
- ****:
- ****:
""",
            "": """
### 

- ****: 
- ****: 
- ****: 
- ****: 
""",
            "": """
### 

- ****: 
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

    def _get_length_desc(self, length: str) -> str:
        """TODO: Add docstring."""
        length_map = {
            "short": "50002-3",
            "medium": "5000-30000",
            "long": "30000"
        }
        return length_map.get(length, "")

    def _format_references(self, search_results: List[Dict[str, Any]]) -> str:
        """TODO: Add docstring."""

        formatted = []
        for i, result in enumerate(search_results, 1):
            title = result.get("title", "")
            content = result.get("content", "")[:300]
            formatted.append(f"###  {i}: {title}\n{content}...\n")

        return "\n".join(formatted)

    def _parse_elements_response(self, response: str) -> Dict[str, Any]:
        """TODO: Add docstring."""

        try:
            # JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                elements = json.loads(json_match.group())

                # 
                required_keys = ["time", "place", "characters", "plot", "environment", "theme"]
                if all(key in elements for key in required_keys):
                    return elements

            logger.warning(f"[{self.name}] JSON")
            return self._get_default_elements()

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return self._get_default_elements()

    def _validate_and_optimize(
        self,
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""

        # 
        if not elements.get("characters") or len(elements["characters"]) == 0:
            elements["characters"] = [
                {
                    "role": "protagonist",
                    "name": "",
                    "age": 30,
                    "occupation": "",
                    "personality": "",
                    "motivation": "",
                    "secret": ""
                }
            ]

        # 2
        if len(elements["characters"]) < 3:
            logger.info(f"[{self.name}] ")
            # TODO: 

        return elements

    def _get_default_elements(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "time": {
                "period": "",
                "duration": "24",
                "key_moments": ["", "", ""]
            },
            "place": {
                "main_location": "",
                "description": "",
                "layout": "10",
                "significance": ""
            },
            "characters": [
                {
                    "role": "protagonist",
                    "name": "",
                    "age": 35,
                    "occupation": "",
                    "personality": "",
                    "motivation": "",
                    "secret": ""
                }
            ],
            "plot": {
                "core_conflict": "",
                "inciting_incident": "",
                "turning_points": ["", "", ""],
                "climax": "",
                "resolution": ""
            },
            "environment": {
                "social": "",
                "natural": "",
                "atmosphere": ""
            },
            "theme": {
                "core_theme": "",
                "message": "",
                "tone": ""
            }
        }

    def _get_fallback_elements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return self._get_default_elements()
