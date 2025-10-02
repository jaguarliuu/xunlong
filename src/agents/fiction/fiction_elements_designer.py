"""
小说六要素设计器 - 为小说创作定义时间、地点、人物、情节、环境、主题
"""
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
import json
import re

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager


class FictionElementsDesigner:
    """小说六要素设计器"""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "小说六要素设计器"

    async def design_elements(
        self,
        query: str,
        requirements: Dict[str, Any],
        search_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """设计小说六要素"""

        logger.info(f"[{self.name}] 开始设计小说六要素")

        try:
            # 构建设计提示
            design_prompt = self._build_design_prompt(query, requirements, search_results)

            # 调用LLM设计
            client = self.llm_manager.get_client("default")
            response = await client.simple_chat(
                design_prompt,
                "你是一个专业的小说创作顾问，擅长设计小说的核心要素。"
            )

            # 解析六要素
            elements = self._parse_elements_response(response)

            # 验证和优化
            elements = self._validate_and_optimize(elements, requirements)

            logger.info(f"[{self.name}] 六要素设计完成")

            return {
                "elements": elements,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"[{self.name}] 六要素设计失败: {e}")
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
        """构建设计提示"""

        genre = requirements.get("genre", "推理")
        length = requirements.get("length", "short")
        constraints = requirements.get("constraints", [])

        # 准备参考资料
        references = ""
        if search_results:
            references = self._format_references(search_results[:5])

        prompt = f"""# 小说六要素设计任务

## 创作需求
用户查询: {query}

## 小说类型与要求
- **类型**: {genre}小说
- **篇幅**: {length} ({self._get_length_desc(length)})
- **特殊约束**: {', '.join(constraints) if constraints else '无'}

## 参考资料
{references if references else "无参考资料，请基于类型常规设定"}

## 任务说明

请为这篇小说设计**六要素**，确保要素之间逻辑一致、相互支撑。

### 六要素定义

1. **时间 (Time)**
   - 故事发生的时代/时间
   - 时间跨度
   - 关键时间节点

2. **地点 (Place)**
   - 主要场景
   - 场景特点
   - 空间布局（如适用）

3. **人物 (Characters)**
   - 主角（姓名、年龄、职业、性格）
   - 主要配角（3-5人）
   - 每个人物的动机和秘密

4. **情节 (Plot)**
   - 核心冲突
   - 关键转折点
   - 结局走向（开放/封闭）

5. **环境 (Environment)**
   - 社会环境
   - 自然环境
   - 氛围营造

6. **主题 (Theme)**
   - 核心主题
   - 要传达的思想
   - 情感基调

## 类型特定要求

{self._get_genre_specific_requirements(genre, constraints)}

## 输出格式

请严格按照以下JSON格式输出：

```json
{{
  "time": {{
    "period": "具体时代/时间",
    "duration": "时间跨度",
    "key_moments": ["关键时间点1", "关键时间点2"]
  }},
  "place": {{
    "main_location": "主要场景名称",
    "description": "场景详细描述",
    "layout": "空间布局说明（如适用）",
    "significance": "场景对情节的意义"
  }},
  "characters": [
    {{
      "role": "protagonist",
      "name": "姓名",
      "age": 年龄,
      "occupation": "职业",
      "personality": "性格特征",
      "motivation": "核心动机",
      "secret": "隐藏的秘密"
    }},
    {{
      "role": "antagonist/supporting",
      "name": "姓名",
      ...
    }}
  ],
  "plot": {{
    "core_conflict": "核心冲突描述",
    "inciting_incident": "引发事件",
    "turning_points": ["转折点1", "转折点2", "转折点3"],
    "climax": "高潮设定",
    "resolution": "结局方向"
  }},
  "environment": {{
    "social": "社会环境描述",
    "natural": "自然环境描述",
    "atmosphere": "整体氛围"
  }},
  "theme": {{
    "core_theme": "核心主题",
    "message": "要传达的思想",
    "tone": "情感基调"
  }}
}}
```

## 设计原则

1. **一致性**: 所有要素应相互支撑，逻辑自洽
2. **新颖性**: 避免老套设定，提供新鲜视角
3. **可行性**: 符合篇幅要求，可实际展开
4. **吸引力**: 设定应有足够吸引力和悬念

请开始设计：
"""

        return prompt

    def _get_genre_specific_requirements(self, genre: str, constraints: List[str]) -> str:
        """获取类型特定要求"""

        requirements_map = {
            "推理": """
### 推理小说特定要求

- **人物**: 至少包含侦探/推理者、受害者、嫌疑人（3人以上）
- **情节**: 必须有清晰的谜题和推理线索
- **环境**: 营造适合推理的氛围（神秘、压抑等）
- **主题**: 围绕真相、正义、人性等

如果包含"暴风雪山庄"或"密室"等约束：
- **地点**: 必须是封闭空间（山庄、别墅、孤岛等）
- **人物**: 所有人物都困于同一空间
- **情节**: 包含连环杀人和逐一排查
- **环境**: 强调隔绝感和恐惧氛围
""",
            "科幻": """
### 科幻小说特定要求

- **时间**: 通常设定在未来或平行时空
- **地点**: 包含科技元素（太空站、未来城市等）
- **环境**: 展现科技对社会的影响
- **主题**: 探讨科技与人性的关系
""",
            "奇幻": """
### 奇幻小说特定要求

- **地点**: 虚构世界或魔法世界
- **人物**: 包含魔法能力或特殊天赋
- **环境**: 建立完整的魔法体系
- **主题**: 善恶对抗、成长等
""",
            "恐怖": """
### 恐怖小说特定要求

- **环境**: 营造恐怖、压抑的氛围
- **情节**: 包含惊悚、悬疑元素
- **主题**: 探讨恐惧、未知等
"""
        }

        return requirements_map.get(genre, "请根据小说类型常规设定进行设计。")

    def _get_length_desc(self, length: str) -> str:
        """获取篇幅描述"""
        length_map = {
            "short": "5000字以内，适合2-3个场景",
            "medium": "5000-30000字，适合多个章节",
            "long": "30000字以上，适合完整故事线"
        }
        return length_map.get(length, "短篇")

    def _format_references(self, search_results: List[Dict[str, Any]]) -> str:
        """格式化参考资料"""

        formatted = []
        for i, result in enumerate(search_results, 1):
            title = result.get("title", "无标题")
            content = result.get("content", "")[:300]
            formatted.append(f"### 参考资料 {i}: {title}\n{content}...\n")

        return "\n".join(formatted)

    def _parse_elements_response(self, response: str) -> Dict[str, Any]:
        """解析六要素响应"""

        try:
            # 提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                elements = json.loads(json_match.group())

                # 验证必要字段
                required_keys = ["time", "place", "characters", "plot", "environment", "theme"]
                if all(key in elements for key in required_keys):
                    return elements

            logger.warning(f"[{self.name}] JSON解析失败，使用默认要素")
            return self._get_default_elements()

        except Exception as e:
            logger.error(f"[{self.name}] 解析六要素失败: {e}")
            return self._get_default_elements()

    def _validate_and_optimize(
        self,
        elements: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证和优化六要素"""

        # 确保人物列表不为空
        if not elements.get("characters") or len(elements["characters"]) == 0:
            elements["characters"] = [
                {
                    "role": "protagonist",
                    "name": "主角",
                    "age": 30,
                    "occupation": "侦探",
                    "personality": "聪明、敏锐",
                    "motivation": "查明真相",
                    "secret": "未知"
                }
            ]

        # 确保至少有主角和2个配角
        if len(elements["characters"]) < 3:
            logger.info(f"[{self.name}] 人物数量不足，补充配角")
            # TODO: 补充人物

        return elements

    def _get_default_elements(self) -> Dict[str, Any]:
        """获取默认六要素"""
        return {
            "time": {
                "period": "现代",
                "duration": "24小时",
                "key_moments": ["事件发生", "调查开始", "真相揭露"]
            },
            "place": {
                "main_location": "山庄",
                "description": "偏僻的山中别墅",
                "layout": "二层建筑，共10个房间",
                "significance": "封闭空间，无法逃离"
            },
            "characters": [
                {
                    "role": "protagonist",
                    "name": "侦探",
                    "age": 35,
                    "occupation": "私家侦探",
                    "personality": "冷静、理性",
                    "motivation": "寻找真相",
                    "secret": "未知"
                }
            ],
            "plot": {
                "core_conflict": "连环杀人案",
                "inciting_incident": "第一起命案",
                "turning_points": ["第二起命案", "发现关键线索", "真凶暴露"],
                "climax": "最终对决",
                "resolution": "真相大白"
            },
            "environment": {
                "social": "现代社会",
                "natural": "暴风雪封锁山路",
                "atmosphere": "紧张、压抑"
            },
            "theme": {
                "core_theme": "真相与正义",
                "message": "罪恶终将被揭露",
                "tone": "悬疑、紧张"
            }
        }

    def _get_fallback_elements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """获取备用要素"""
        return self._get_default_elements()
