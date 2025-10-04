"""
PPT大纲生成器 - 根据主题和风格生成PPT大纲
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager
from ..base import BaseAgent, AgentConfig


class PPTOutlineGenerator(BaseAgent):
    """PPT大纲生成器 - 生成符合风格的PPT大纲"""

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager = None
    ):
        config = AgentConfig(
            name="PPT大纲生成器",
            description="根据主题和风格生成PPT大纲",
            llm_config_name="outline_generator",
            temperature=0.7,
            max_tokens=3000
        )
        super().__init__(llm_manager, prompt_manager, config)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """实现BaseAgent的抽象方法"""
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
        生成PPT大纲

        Args:
            topic: PPT主题
            style: PPT风格 (red/business/academic/creative/simple)
            slides: 目标页数
            search_results: 搜索结果
            depth: 内容深度

        Returns:
            {
                "status": "success/error",
                "outline": {
                    "title": "PPT标题",
                    "subtitle": "副标题",
                    "slides": [
                        {
                            "slide_number": 1,
                            "type": "cover/content/section/conclusion",
                            "title": "页面标题",
                            "key_points": ["要点1", "要点2"],
                            "content_density": "minimal/medium/detailed"
                        }
                    ]
                }
            }
        """
        try:
            logger.info(f"[{self.name}] 开始生成PPT大纲 (主题: {topic}, 风格: {style}, 页数: {slides})")

            # 构建提示词
            system_prompt = self._get_system_prompt(style)
            user_prompt = self._build_user_prompt(topic, style, slides, search_results, depth)

            # 调用LLM
            response = await self.get_llm_response(user_prompt, system_prompt)

            # 解析大纲
            outline = self._parse_outline(response, topic, slides)

            logger.info(f"[{self.name}] 大纲生成完成，共 {len(outline['slides'])} 页")

            return {
                "status": "success",
                "outline": outline
            }

        except Exception as e:
            logger.error(f"[{self.name}] 大纲生成失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _get_system_prompt(self, style: str) -> str:
        """获取系统提示词"""

        style_guides = {
            "red": """
你是一位擅长RED风格PPT的设计师。
RED风格特点：
- 极简主义，每页只有核心主题
- 不需要详细内容，只需要醒目的标题和关键词
- 视觉冲击力强
- 适合快速浏览和社交媒体分享
""",
            "business": """
你是一位专业的商务PPT设计师。
商务风格特点：
- 结构清晰，逻辑严密
- 每页包含标题、要点、数据支撑
- 内容详细但简洁
- 适合商业汇报和提案
""",
            "academic": """
你是一位学术PPT设计专家。
学术风格特点：
- 严谨专业，逻辑严密
- 每页包含标题、详细论述、数据图表
- 注重论证过程
- 适合学术报告和研讨会
""",
            "creative": """
你是一位创意PPT设计师。
创意风格特点：
- 新颖独特，打破常规
- 每页有创意的视觉呈现
- 内容生动有趣
- 适合品牌宣传和创意提案
""",
            "simple": """
你是一位极简风格PPT设计师。
极简风格特点：
- 简洁明了，去除冗余
- 每页一个核心观点
- 内容适中
- 适合快速演讲和分享
"""
        }

        base_prompt = style_guides.get(style, style_guides["business"])

        return base_prompt + """
你的任务：
1. 分析主题和资料
2. 设计符合风格的PPT结构
3. 规划每一页的内容框架
4. 确保整体连贯性

输出格式（JSON）：
{
  "title": "PPT标题",
  "subtitle": "副标题",
  "slides": [
    {
      "slide_number": 1,
      "type": "cover/content/section/conclusion",
      "title": "页面标题",
      "key_points": ["要点1", "要点2", "要点3"],
      "content_density": "minimal/medium/detailed"
    }
  ]
}

注意：
- slide_number从1开始
- type类型：cover(封面), content(内容页), section(章节页), conclusion(总结页)
- content_density根据风格调整：
  * red/simple: minimal (只有标题和1-2个关键词)
  * business/creative: medium (标题+3-5个要点)
  * academic: detailed (标题+详细要点+可能的数据)
"""

    def _build_user_prompt(
        self,
        topic: str,
        style: str,
        slides: int,
        search_results: List[Dict[str, Any]],
        depth: str
    ) -> str:
        """构建用户提示词"""

        prompt = f"""请为以下主题设计一个PPT大纲：

主题：{topic}
风格：{style}
目标页数：{slides}
内容深度：{depth}

参考资料摘要：
"""

        # 添加搜索结果摘要
        for i, result in enumerate(search_results[:5], 1):  # 最多5个
            title = result.get("title", "无标题")
            snippet = result.get("snippet", result.get("full_content", ""))[:200]
            prompt += f"\n{i}. {title}\n   {snippet}...\n"

        prompt += f"""

请根据{style}风格设计大纲，确保：
1. 第一页是封面 (type: cover)
2. 最后一页是总结 (type: conclusion)
3. 中间页面根据主题合理分配
4. 内容密度符合{style}风格
5. 整体页数控制在{slides}页左右（可以±2页）

请直接返回JSON格式的大纲。"""

        return prompt

    def _parse_outline(self, response: str, topic: str, target_slides: int) -> Dict[str, Any]:
        """解析LLM返回的大纲"""
        import json
        import re

        try:
            # 提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                outline = json.loads(json_match.group(0))
            else:
                raise ValueError("未找到有效的JSON格式")

            # 验证和补充
            if "title" not in outline:
                outline["title"] = topic

            if "slides" not in outline or not outline["slides"]:
                raise ValueError("大纲中没有slides")

            # 确保slide_number连续
            for i, slide in enumerate(outline["slides"], 1):
                slide["slide_number"] = i

            return outline

        except Exception as e:
            logger.error(f"解析大纲失败: {e}, 使用默认大纲")
            # 返回默认大纲
            return self._get_default_outline(topic, target_slides)

    def _get_default_outline(self, topic: str, slides: int) -> Dict[str, Any]:
        """生成默认大纲"""
        default_slides = [
            {
                "slide_number": 1,
                "type": "cover",
                "title": topic,
                "key_points": [],
                "content_density": "minimal"
            }
        ]

        # 生成内容页
        for i in range(2, slides):
            default_slides.append({
                "slide_number": i,
                "type": "content",
                "title": f"主题{i-1}",
                "key_points": ["要点1", "要点2", "要点3"],
                "content_density": "medium"
            })

        # 添加总结页
        default_slides.append({
            "slide_number": slides,
            "type": "conclusion",
            "title": "总结",
            "key_points": ["总结要点"],
            "content_density": "medium"
        })

        return {
            "title": topic,
            "subtitle": "",
            "slides": default_slides
        }
