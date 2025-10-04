"""
PPT页面内容生成器 - 为每一页PPT生成详细内容
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager
from ..base import BaseAgent, AgentConfig


class SlideContentGenerator(BaseAgent):
    """PPT页面内容生成器 - 根据大纲生成每页详细内容"""

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="PPT内容生成器",
            description="为PPT每一页生成详细内容",
            llm_config_name="slide_content_generator",
            temperature=0.7,
            max_tokens=2000
        )
        super().__init__(llm_manager, prompt_manager, config)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """实现BaseAgent的抽象方法"""
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
        生成单页PPT内容

        Args:
            slide_outline: 页面大纲
            style: PPT风格
            available_content: 可用的资料内容
            context: 上下文（如前一页内容）

        Returns:
            {
                "slide_number": 1,
                "type": "cover",
                "title": "标题",
                "subtitle": "副标题",
                "content": {
                    "points": ["要点1", "要点2"],
                    "details": {"要点1": "详细说明"},
                    "visuals": [{"type": "image/chart", "description": "..."}]
                }
            }
        """
        try:
            slide_number = slide_outline.get("slide_number")
            slide_type = slide_outline.get("type", "content")

            logger.info(f"[{self.name}] 生成第 {slide_number} 页内容 (类型: {slide_type})")

            # 不同类型页面使用不同生成策略
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
            logger.error(f"[{self.name}] 生成页面内容失败: {e}")
            return self._get_fallback_slide(slide_outline)

    async def _generate_cover_slide(
        self,
        slide_outline: Dict[str, Any],
        style: str
    ) -> Dict[str, Any]:
        """生成封面页"""
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
        """生成总结页"""
        system_prompt = f"""你是一位PPT内容撰写专家，擅长{style}风格。
现在需要生成PPT的总结页。"""

        user_prompt = f"""请为以下总结页生成内容：

标题：{slide_outline.get('title', '总结')}
要求的要点数：{len(slide_outline.get('key_points', []))}

请生成2-4个总结要点，每个要点简洁有力。

输出JSON格式：
{{
  "points": ["总结要点1", "总结要点2", "总结要点3"]
}}
"""

        response = await self.get_llm_response(user_prompt, system_prompt)

        # 解析响应
        import json
        import re
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group(0))
                points = data.get("points", ["感谢观看"])
            else:
                points = ["感谢观看"]
        except:
            points = ["感谢观看"]

        return {
            "slide_number": slide_outline.get("slide_number"),
            "type": "conclusion",
            "title": slide_outline.get("title", "总结"),
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
        """生成内容页"""

        title = slide_outline.get("title", "")
        key_points = slide_outline.get("key_points", [])
        content_density = slide_outline.get("content_density", "medium")

        # 根据内容密度调整提示词
        density_guides = {
            "minimal": "只需要1-2个核心关键词或短语，无需详细说明",
            "medium": "需要3-5个要点，每个要点一句话说明",
            "detailed": "需要3-5个要点，每个要点包含详细论述和数据支撑"
        }

        system_prompt = f"""你是一位PPT内容撰写专家，擅长{style}风格。
内容密度要求：{density_guides.get(content_density, density_guides['medium'])}"""

        # 提取相关资料
        relevant_content = self._extract_relevant_content(title, available_content)

        user_prompt = f"""请为以下PPT页面生成内容：

标题：{title}
风格：{style}
内容密度：{content_density}

参考资料：
{relevant_content}

请生成符合要求的页面内容。

输出JSON格式：
{{
  "points": ["要点1", "要点2", "要点3"],
  "details": {{"要点1": "详细说明（仅在content_density为detailed时提供）"}},
  "visuals": [{{"type": "chart/image", "description": "建议的可视化内容"}}]
}}

注意：
- points数量根据content_density调整（minimal: 1-2, medium: 3-5, detailed: 3-5）
- 如果是minimal，details可以为空
- visuals是可选的，建议合适的数据可视化
"""

        response = await self.get_llm_response(user_prompt, system_prompt)

        # 解析响应
        import json
        import re
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = {"points": key_points, "details": {}, "visuals": []}
        except Exception as e:
            logger.warning(f"解析内容失败: {e}, 使用默认内容")
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
        """提取与标题相关的内容"""

        relevant_texts = []
        title_lower = title.lower()

        for item in available_content[:10]:  # 最多检查10个
            content = item.get("full_content", item.get("snippet", ""))
            # 简单的相关性判断：标题关键词在内容中
            if any(word in content.lower() for word in title_lower.split() if len(word) > 2):
                relevant_texts.append(content[:300])

        combined = "\n\n".join(relevant_texts)
        return combined[:max_length] if combined else "（无相关资料）"

    def _get_fallback_slide(self, slide_outline: Dict[str, Any]) -> Dict[str, Any]:
        """生成默认页面（当生成失败时）"""
        return {
            "slide_number": slide_outline.get("slide_number"),
            "type": slide_outline.get("type", "content"),
            "title": slide_outline.get("title", ""),
            "subtitle": "",
            "content": {
                "points": slide_outline.get("key_points", ["内容生成中..."]),
                "details": {},
                "visuals": []
            }
        }
