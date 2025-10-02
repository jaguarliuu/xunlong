"""
小说大纲生成器 - 基于六要素生成小说章节大纲
"""
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
import json
import re

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager


class FictionOutlineGenerator:
    """小说大纲生成器"""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "小说大纲生成器"

    async def generate_outline(
        self,
        query: str,
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """基于六要素生成小说大纲"""

        logger.info(f"[{self.name}] 开始生成小说大纲")

        try:
            # 构建大纲生成提示
            outline_prompt = self._build_outline_prompt(query, elements, requirements)

            # 调用LLM生成大纲
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                outline_prompt,
                "你是一个专业的小说大纲设计师，擅长设计引人入胜的故事结构。"
            )

            # 解析大纲
            outline = self._parse_outline_response(response)

            # 验证和优化
            outline = self._validate_and_optimize(outline, elements, requirements)

            logger.info(f"[{self.name}] 大纲生成完成，共 {len(outline['chapters'])} 个章节")

            return {
                "outline": outline,
                "total_chapters": len(outline["chapters"]),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"[{self.name}] 大纲生成失败: {e}")
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
        """构建大纲生成提示"""

        genre = requirements.get("genre", "推理")
        length = requirements.get("length", "short")
        constraints = requirements.get("constraints", [])

        # 准备六要素摘要
        elements_summary = self._format_elements(elements)

        # 确定章节数量
        chapter_count = self._get_chapter_count(length)

        prompt = f"""# 小说大纲生成任务

## 创作需求
{query}

## 小说类型
- **类型**: {genre}
- **篇幅**: {length} (建议 {chapter_count} 个章节)
- **约束**: {', '.join(constraints) if constraints else '无'}

## 六要素设定

{elements_summary}

## 任务要求

基于以上六要素，设计一个完整的小说章节大纲。

### 大纲结构

每个章节应包含：
1. **章节编号**: 从1开始
2. **章节标题**: 简洁有力的标题
3. **写作要点**: 本章节要完成的情节内容
4. **关键场景**: 1-2个关键场景描述
5. **人物发展**: 涉及的主要人物及其行动
6. **悬念设置**: 本章留下的悬念/线索
7. **目标字数**: 建议字数

### 结构要求

- **开篇** (第1章): 引入设定，建立悬念
- **发展** (中间章节): 展开冲突，推进情节
- **高潮** (倒数第2章): 矛盾激化，达到顶峰
- **结局** (最后1章): 解决冲突，揭示真相

## 类型特定要求

{self._get_genre_outline_requirements(genre, constraints)}

## 输出格式

请严格按照以下JSON格式输出：

```json
{{
  "title": "小说标题",
  "synopsis": "一句话梗概",
  "chapters": [
    {{
      "id": 1,
      "title": "章节标题",
      "writing_points": "本章要完成的情节内容（详细）",
      "key_scenes": ["关键场景1", "关键场景2"],
      "characters_involved": ["人物A", "人物B"],
      "suspense": "本章留下的悬念",
      "word_count": 1000
    }}
  ]
}}
```

请开始设计大纲：
"""

        return prompt

    def _get_genre_outline_requirements(self, genre: str, constraints: List[str]) -> str:
        """获取类型特定的大纲要求"""

        requirements_map = {
            "推理": """
### 推理小说大纲要求

- **线索布局**: 每章至少埋下1-2条线索
- **红鲱鱼**: 设置误导性线索
- **逻辑链**: 确保推理链条完整
- **真相揭露**: 最后一章完整揭示真相和推理过程

暴风雪山庄模式特定要求：
- 第1章: 介绍所有人物，建立封闭环境
- 第2章: 第一起命案发生
- 中间章节: 连环杀人，逐步减少人员
- 倒数第2章: 推理过程，排查嫌疑人
- 最后1章: 揭露真凶，解释动机
""",
            "科幻": """
### 科幻小说大纲要求

- **设定展开**: 逐步展现世界观和科技设定
- **冲突升级**: 从个人冲突到更大范围冲突
- **思考深度**: 探讨科技与人性的关系
""",
            "恐怖": """
### 恐怖小说大纲要求

- **氛围营造**: 逐步加强恐怖氛围
- **悬念递进**: 层层推进恐怖感
- **高潮释放**: 在高潮处达到恐怖顶峰
"""
        }

        return requirements_map.get(genre, "请按照小说类型常规结构设计。")

    def _get_chapter_count(self, length: str) -> int:
        """根据篇幅确定章节数"""
        length_map = {
            "short": 5,      # 短篇 5章
            "medium": 12,    # 中篇 12章
            "long": 30       # 长篇 30章
        }
        return length_map.get(length, 5)

    def _format_elements(self, elements: Dict[str, Any]) -> str:
        """格式化六要素"""

        formatted = []

        # 时间
        time_info = elements.get("time", {})
        formatted.append(f"**时间**: {time_info.get('period', '未知')}")

        # 地点
        place_info = elements.get("place", {})
        formatted.append(f"**地点**: {place_info.get('main_location', '未知')}")
        formatted.append(f"  描述: {place_info.get('description', '')}")

        # 人物
        characters = elements.get("characters", [])
        formatted.append(f"\n**人物** ({len(characters)} 人):")
        for char in characters[:6]:  # 最多显示6个
            name = char.get("name", "未知")
            role = char.get("role", "")
            occupation = char.get("occupation", "")
            formatted.append(f"  - {name} ({role}): {occupation}")

        # 情节
        plot = elements.get("plot", {})
        formatted.append(f"\n**核心冲突**: {plot.get('core_conflict', '')}")

        # 主题
        theme = elements.get("theme", {})
        formatted.append(f"**核心主题**: {theme.get('core_theme', '')}")

        return "\n".join(formatted)

    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """解析大纲响应"""

        try:
            # 提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                outline = json.loads(json_match.group())

                # 验证必要字段
                if "chapters" in outline and isinstance(outline["chapters"], list):
                    return outline

            logger.warning(f"[{self.name}] JSON解析失败，使用默认大纲")
            return self._get_default_outline()

        except Exception as e:
            logger.error(f"[{self.name}] 解析大纲失败: {e}")
            return self._get_default_outline()

    def _validate_and_optimize(
        self,
        outline: Dict[str, Any],
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证和优化大纲"""

        chapters = outline.get("chapters", [])

        # 确保章节数量合理
        target_count = self._get_chapter_count(requirements.get("length", "short"))

        if len(chapters) < target_count - 2:
            logger.warning(f"[{self.name}] 章节数量不足 ({len(chapters)} < {target_count})")
            # TODO: 补充章节

        # 确保每章有必要字段
        for i, chapter in enumerate(chapters):
            if "id" not in chapter:
                chapter["id"] = i + 1
            if "word_count" not in chapter:
                chapter["word_count"] = 800

        outline["chapters"] = chapters

        return outline

    def _get_default_outline(self) -> Dict[str, Any]:
        """获取默认大纲"""
        return {
            "title": "暴风雪山庄疑案",
            "synopsis": "暴风雪封锁的山庄中，连环杀人案逐步展开",
            "chapters": [
                {
                    "id": 1,
                    "title": "山庄来客",
                    "writing_points": "介绍所有人物，建立封闭环境，暴风雪来临",
                    "key_scenes": ["众人抵达山庄", "暴风雪封路"],
                    "characters_involved": ["所有人物"],
                    "suspense": "山庄与外界失联",
                    "word_count": 1000
                },
                {
                    "id": 2,
                    "title": "第一起命案",
                    "writing_points": "发现第一具尸体，开始调查",
                    "key_scenes": ["发现尸体", "初步调查"],
                    "characters_involved": ["侦探", "受害者", "嫌疑人"],
                    "suspense": "凶手就在其中",
                    "word_count": 1000
                }
            ]
        }

    def _get_fallback_outline(
        self,
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取备用大纲"""
        return self._get_default_outline()
