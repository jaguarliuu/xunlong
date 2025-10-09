"""
 - 
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager


class SectionWriter:
    """"""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = ""

    async def write_section(
        self,
        section: Dict[str, Any],
        available_content: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """"""

        section_id = section.get("id")
        section_title = section.get("title")

        logger.info(f"[{self.name}]  {section_id}: {section_title}")

        try:
            # 
            relevant_content = self._filter_relevant_content(
                section, available_content
            )

            # 
            section_images = []

            # 
            writing_prompt = self._build_writing_prompt(
                section, relevant_content, context
            )

            # LLM
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                writing_prompt,
                ""
            )

            # 
            enhanced_content = response

            # 
            confidence = self._calculate_confidence(
                enhanced_content, section, relevant_content
            )

            # 
            issues = self._identify_issues(enhanced_content, section)

            result = {
                "section_id": section_id,
                "title": section_title,
                "content": enhanced_content,
                "confidence": confidence,
                "sources_used": [c.get("url", "") for c in relevant_content[:5]],
                "word_count": len(enhanced_content),
                "issues": issues,
                "status": "success",
                "images": section_images,
                "image_count": len(section_images),
                "images_inserted": bool(section_images)
            }

            logger.info(
                f"[{self.name}]  {section_id} "
                f": {len(enhanced_content)}, "
                f": {confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"[{self.name}]  {section_id} : {e}")
            return {
                "section_id": section_id,
                "title": section_title,
                "content": "",
                "confidence": 0.0,
                "sources_used": [],
                "word_count": 0,
                "issues": [f": {str(e)}"],
                "status": "error",
                "error": str(e),
                "images": [],
                "image_count": 0,
                "images_inserted": False
            }

    async def rewrite_section(
        self,
        section_result: Dict[str, Any],
        suggestions: List[str],
        additional_content: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """"""

        section_id = section_result.get("section_id")
        logger.info(f"[{self.name}]  {section_id}")

        try:
            # 
            rewrite_prompt = self._build_rewrite_prompt(
                section_result, suggestions, additional_content
            )

            # LLM
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                rewrite_prompt,
                ""
            )

            # 
            section_result["content"] = response
            section_result["word_count"] = len(response)
            section_result["confidence"] = self._calculate_confidence(
                response, {"requirements": section_result.get("title", "")}, []
            )

            logger.info(f"[{self.name}]  {section_id} ")

            return section_result

        except Exception as e:
            logger.error(f"[{self.name}]  {section_id} : {e}")
            section_result["issues"].append(f": {str(e)}")
            return section_result

    def _filter_relevant_content(
        self,
        section: Dict[str, Any],
        available_content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """"""

        section_title = section.get("title", "").lower()
        requirements = section.get("requirements", "").lower()
        suggested_sources = section.get("suggested_sources", [])

        relevant = []

        for content in available_content:
            score = 0

            # 
            title = content.get("title", "").lower()
            if any(word in title for word in section_title.split()):
                score += 2

            # 
            text = content.get("content", "").lower()
            if any(word in text for word in requirements.split()):
                score += 1

            # 
            if title in [s.lower() for s in suggested_sources]:
                score += 3

            if score > 0:
                relevant.append((score, content))

        # 
        relevant.sort(key=lambda x: x[0], reverse=True)

        return [content for score, content in relevant[:10]]

    def _build_writing_prompt(
        self,
        section: Dict[str, Any],
        relevant_content: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """"""

        section_id = section.get("id")
        title = section.get("title")
        requirements = section.get("requirements")
        word_count = section.get("word_count", 500)

        # 
        references = self._format_references(relevant_content)

        # 
        query = context.get("query", "") if context else ""
        report_type = context.get("report_type", "comprehensive") if context else "comprehensive"
        previous_section = context.get("previous_section", "") if context else ""

        prompt = f"""# 

## 
- : {section_id}
- : {title}
- : {word_count} 

## 
{requirements}

## 
{query}

## 
{report_type}

{"## " if previous_section else ""}
{previous_section[:200] + "..." if previous_section else ""}

## 


{references}

## 

1. ****:
   - ""
   - 
   - 
   - 

2. ****:
   - Markdown
   - 
   -  {word_count}  20% 

3. ****:
   - 
   - 
   - 
   - 

4. ****:
   - 
   - 
   - 

## 


- 
- 
- 
- 


"""

        return prompt

    def _collect_section_images(
        self,
        relevant_content: List[Dict[str, Any]],
        section_title: Optional[str] = None,
        max_images: int = 4
    ) -> List[Dict[str, Any]]:
        """"""

        collected: List[Dict[str, Any]] = []
        seen_keys = set()

        for content in relevant_content:
            images = content.get("images") or []
            if not images:
                continue

            for img in images:
                if not isinstance(img, dict):
                    continue

                key = img.get("url") or img.get("local_path")
                if not key or key in seen_keys:
                    continue

                seen_keys.add(key)

                alt_text = img.get("alt") or content.get("title") or section_title or ""
                sanitized = {
                    "url": img.get("url"),
                    "local_path": "",  # 
                    "alt": alt_text,
                    "width": img.get("width"),
                    "height": img.get("height"),
                    "source": content.get("title") or content.get("url"),
                    "source_title": content.get("title", ""),
                    "source_url": content.get("url", ""),
                    "search_query": content.get("search_query"),
                    "original_local_path": img.get("local_path")
                }

                collected.append(sanitized)

                if len(collected) >= max_images:
                    return collected

        return collected

    def _format_references(self, content_list: List[Dict[str, Any]]) -> str:
        """"""

        if not content_list:
            return ""

        formatted = []
        for i, content in enumerate(content_list[:8], 1):
            title = content.get("title", "")
            url = content.get("url", "")
            text = content.get("content", "")[:500]

            formatted.append(f"""
###  {i}: {title}
**URL**: {url}
****: {text}...
""")

        return "\n".join(formatted)

    def _calculate_confidence(
        self,
        content: str,
        section: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> float:
        """"""

        confidence = 0.5  # 

        # 
        word_count = len(content)
        target_count = section.get("word_count", 500)

        if 0.8 * target_count <= word_count <= 1.2 * target_count:
            confidence += 0.2
        elif 0.6 * target_count <= word_count <= 1.4 * target_count:
            confidence += 0.1

        # Markdown
        if "#" in content or "**" in content or "-" in content:
            confidence += 0.1

        # 
        if sources:
            confidence += min(0.2, len(sources) * 0.05)

        return min(1.0, confidence)

    def _identify_issues(
        self,
        content: str,
        section: Dict[str, Any]
    ) -> List[str]:
        """"""

        issues = []

        # 
        word_count = len(content)
        target_count = section.get("word_count", 500)

        if word_count < 0.6 * target_count:
            issues.append(f" ({word_count}  <  {target_count} )")

        if word_count > 1.4 * target_count:
            issues.append(f" ({word_count}  >  {target_count} )")

        # 
        if content.count("") < 3:
            issues.append("")

        # 
        if not any(marker in content for marker in ["#", "**", "-", ""]):
            issues.append("")

        return issues

    def _build_rewrite_prompt(
        self,
        section_result: Dict[str, Any],
        suggestions: List[str],
        additional_content: Optional[List[Dict[str, Any]]]
    ) -> str:
        """"""

        original_content = section_result.get("content", "")
        section_title = section_result.get("title", "")

        additional_refs = ""
        if additional_content:
            additional_refs = self._format_references(additional_content)

        prompt = f"""# 

## 
### {section_title}
{original_content}

## 
{chr(10).join(f"- {s}" for s in suggestions)}

{"## " if additional_refs else ""}
{additional_refs}

## 



1. ****
2. ****
3. ****
4. ****


"""

        return prompt
