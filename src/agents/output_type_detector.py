"""
 - //PPT
"""
import re
from typing import Dict, Any, Optional
from loguru import logger

from ..llm.manager import LLMManager
from ..llm.prompts import PromptManager


class OutputTypeDetector:
    """TODO: Add docstring."""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""

    async def detect_output_type(self, query: str) -> Dict[str, Any]:
        """TODO: Add docstring."""

        logger.info(f"[{self.name}] ")

        # 
        rule_based = self._rule_based_detection(query)
        if rule_based["confidence"] > 0.8:
            logger.info(
                f"[{self.name}] : {rule_based['output_type']} "
                f"(: {rule_based['confidence']:.2f})"
            )
            return rule_based

        # LLM
        logger.info(f"[{self.name}] LLM")
        llm_result = await self._llm_based_detection(query)

        return llm_result

    def _rule_based_detection(self, query: str) -> Dict[str, Any]:
        """TODO: Add docstring."""

        query_lower = query.lower()

        # 
        fiction_keywords = [
            "", "", "", "", "", "",
            "fiction", "story", "novel", "narrative",
            "", "", "", "", ""
        ]

        # 
        report_keywords = [
            "", "", "", "", "",
            "report", "analysis", "summary", "review",
            "", "", "", ""
        ]

        # PPT
        ppt_keywords = [
            "ppt", "", "", "slide", "presentation",
            "", ""
        ]

        # 
        fiction_score = sum(1 for kw in fiction_keywords if kw in query_lower)
        report_score = sum(1 for kw in report_keywords if kw in query_lower)
        ppt_score = sum(1 for kw in ppt_keywords if kw in query_lower)

        # 
        # 1. "XX" 
        if re.search(r'.*?|.*?|.*?', query):
            fiction_score += 5

        # 2. "XX" 
        if re.search(r'\d+.*?|.*?', query):
            report_score += 5

        # 3. "PPT" 
        if re.search(r'.*?ppt|.*?', query_lower):
            ppt_score += 5

        # 
        max_score = max(fiction_score, report_score, ppt_score)

        if max_score == 0:
            # 
            return {
                "output_type": "report",
                "confidence": 0.5,
                "reason": "",
                "detection_method": "rule_based"
            }

        # 
        total_score = fiction_score + report_score + ppt_score
        confidence = max_score / total_score if total_score > 0 else 0.5

        if fiction_score == max_score:
            output_type = "fiction"
            reason = f" (: {fiction_score})"
        elif ppt_score == max_score:
            output_type = "ppt"
            reason = f"PPT (: {ppt_score})"
        else:
            output_type = "report"
            reason = f" (: {report_score})"

        return {
            "output_type": output_type,
            "confidence": min(confidence, 0.95),  # 0.95
            "reason": reason,
            "detection_method": "rule_based",
            "scores": {
                "fiction": fiction_score,
                "report": report_score,
                "ppt": ppt_score
            }
        }

    async def _llm_based_detection(self, query: str) -> Dict[str, Any]:
        """LLM"""

        prompt = f"""# 



## 
{query}

## 

1. **report** ()
   - 
   - 
   - 
     - "AI"
     - ""
     - ""

2. **fiction** (/)
   - 
   - 
   - 
     - ""
     - ""
     - ""

3. **ppt** ()
   - 
   - PPT
   - 
     - "PPT"
     - ""

##

- ****
- ****
- ****

## 

JSON

```json
{{
  "output_type": "report" | "fiction" | "ppt",
  "confidence": 0.95,
  "reason": ""
}}
```


- output_type  "report""fiction""ppt" 
- confidence 0.0-1.0
- reason 


"""

        try:
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                prompt,
                ""
            )

            # 
            import json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())

                # 
                if "output_type" in result and result["output_type"] in ["report", "fiction", "ppt"]:
                    result["detection_method"] = "llm_based"
                    logger.info(
                        f"[{self.name}] LLM: {result['output_type']} "
                        f"(: {result.get('confidence', 0.8):.2f})"
                    )
                    return result

            # 
            logger.warning(f"[{self.name}] LLM")
            return {
                "output_type": "report",
                "confidence": 0.6,
                "reason": "LLM",
                "detection_method": "fallback"
            }

        except Exception as e:
            logger.error(f"[{self.name}] LLM: {e}")
            return {
                "output_type": "report",
                "confidence": 0.5,
                "reason": f": {str(e)}",
                "detection_method": "error_fallback"
            }

    def extract_fiction_requirements(self, query: str) -> Dict[str, Any]:
        """Extract fiction-specific requirements from the query."""

        requirements = {
            "genre": None,      # 
            "length": None,     # 
            "theme": None,      # 
            "style": None,      # 
            "constraints": []   # 
        }

        query_lower = query.lower()

        # 
        genre_patterns = {
            "": ["", "", "", "mystery", "detective"],
            "": ["", "sci-fi", ""],
            "": ["", "", "fantasy"],
            "": ["", "", "romance"],
            "": ["", "", "horror"],
            "": ["", "", ""]
        }

        for genre, keywords in genre_patterns.items():
            if any(kw in query_lower for kw in keywords):
                requirements["genre"] = genre
                break

        # 
        if "" in query or "short" in query_lower:
            requirements["length"] = "short"  # 5000
        elif "" in query or "medium" in query_lower:
            requirements["length"] = "medium"  # 5000-30000
        elif "" in query or "long" in query_lower:
            requirements["length"] = "long"  # 30000
        else:
            requirements["length"] = "short"  # 

        # 
        special_patterns = [
            ("", ""),
            ("", ""),
            ("", ""),
            ("", ""),
            ("time loop", ""),
            ("", ""),
            ("", "")
        ]

        for pattern, constraint in special_patterns:
            if pattern in query_lower:
                requirements["constraints"].append(constraint)

        return requirements
