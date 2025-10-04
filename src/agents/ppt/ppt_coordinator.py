"""
PPT协调器 - 协调多智能体生成PPT
"""

import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from datetime import datetime
from pydantic import BaseModel, Field

from ...llm.manager import LLMManager
from ...llm.prompts import PromptManager
from .outline_generator import PPTOutlineGenerator
from .slide_content_generator import SlideContentGenerator


# ========== 新架构：简化大纲结构 ==========
class PPTOutline(BaseModel):
    """PPT大纲 - 只包含元数据"""
    title: str = Field(description="PPT标题")
    subtitle: Optional[str] = Field(default=None, description="副标题")
    colors: Dict[str, str] = Field(description="配色方案{primary, accent, background, text, secondary}")
    pages: List[Dict[str, Any]] = Field(description="页面大纲列表，每页包含{slide_number, page_type, topic, key_points, has_chart}")


# ========== 旧架构：完整数据结构（保留兼容） ==========
class ColorScheme(BaseModel):
    """配色方案"""
    primary: str = Field(description="主色调，用于标题、重点强调（十六进制颜色，如#ff4757）")
    accent: str = Field(description="强调色，用于按钮、链接、图标（十六进制颜色）")
    background: str = Field(description="背景色（十六进制颜色）")
    text: str = Field(description="正文文字颜色（十六进制颜色）")
    secondary: str = Field(description="次要文字颜色（十六进制颜色）")


class SlideDesign(BaseModel):
    """幻灯片设计方案"""
    layout_strategy: str = Field(description="布局策略: center_text|left_right_split|grid_cards|big_numbers|top_bottom|custom")
    visual_style: str = Field(description="视觉风格描述，如'极简大字留白'、'专业数据卡片'、'创意对比布局'")
    color_usage: str = Field(description="配色使用建议，如'主色背景+白色文字'、'白底+主色标题'")


class SlideContent(BaseModel):
    """幻灯片内容"""
    title: Optional[str] = Field(default=None, description="标题文字")
    main_points: List[str] = Field(description="主要内容点（3-5个）")
    data_items: Optional[List[Dict[str, str]]] = Field(default=None, description="数据项，如[{'label':'市场规模','value':'4850亿'}]")
    detail_text: Optional[str] = Field(default=None, description="详细说明文字")
    chart: Optional[Dict[str, Any]] = Field(default=None, description="图表配置，包含type和data")


class Slide(BaseModel):
    """单个幻灯片 - 设计与内容分离"""
    slide_number: int = Field(description="页码")
    design: SlideDesign = Field(description="设计方案")
    content: SlideContent = Field(description="内容数据")


class PPTData(BaseModel):
    """完整PPT数据"""
    title: str = Field(description="PPT标题")
    subtitle: Optional[str] = Field(default=None, description="副标题")
    colors: ColorScheme = Field(description="配色方案，根据内容主题和风格选择")
    slides: List[Slide] = Field(description="幻灯片列表")


class PPTCoordinator:
    """PPT协调器 - 管理PPT生成的整个流程"""

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager
    ):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "PPT协调器"

        # 初始化智能体
        self.outline_generator = PPTOutlineGenerator(llm_manager, prompt_manager)
        self.slide_content_generator = SlideContentGenerator(llm_manager, prompt_manager)

    async def generate_ppt_v2(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        ppt_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        多智能体协作生成PPT (新架构)

        Phase 1: OutlineAgent生成大纲
        Phase 2: N个PageAgent并行生成页面HTML
        Phase 3: AssemblerAgent组装最终PPT
        """
        logger.info(f"[{self.name}] 使用多智能体架构生成PPT: {topic}")

        try:
            style = ppt_config.get('style', 'business')
            slides = ppt_config.get('slides', 10)

            # Phase 1: 生成大纲
            logger.info(f"[{self.name}] Phase 1: 生成PPT大纲")
            outline = await self._generate_outline_v2(topic, search_results, style, slides)

            # Phase 2: 并行生成所有页面HTML
            logger.info(f"[{self.name}] Phase 2: 并行生成{len(outline['pages'])}个页面")
            page_htmls = await self._parallel_generate_pages(
                outline=outline,
                search_results=search_results,
                style=style
            )

            # Phase 3: 组装最终PPT
            logger.info(f"[{self.name}] Phase 3: 组装最终PPT")
            html_content = self._assemble_ppt_v2(outline, page_htmls)

            return {
                "status": "success",
                "ppt": {
                    "title": outline['title'],
                    "subtitle": outline.get('subtitle', ''),
                    "colors": outline['colors'],
                    "slides": page_htmls,  # 简化后的数据
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "style": style,
                        "slide_count": len(page_htmls)
                    }
                },
                "html_content": html_content
            }

        except Exception as e:
            logger.error(f"[{self.name}] PPT生成失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    async def generate_ppt(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        ppt_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        协调生成PPT

        Args:
            topic: PPT主题
            search_results: 搜索结果
            ppt_config: PPT配置
                {
                    'style': 'red/business/academic/creative/simple',
                    'slides': 10,
                    'depth': 'surface/medium/deep',
                    'theme': 'default/blue/red/green/purple'
                }

        Returns:
            {
                "status": "success/error",
                "ppt": {
                    "title": "PPT标题",
                    "subtitle": "副标题",
                    "slides": [...],
                    "metadata": {...}
                },
                "html_content": "HTML格式的PPT"
            }
        """

        logger.info(f"[{self.name}] 开始生成PPT: {topic}")
        logger.info(f"[{self.name}] PPT配置: {ppt_config}")

        try:
            style = ppt_config.get('style', 'business')
            logger.info(f"[{self.name}] 使用风格: {style}")
            slides = ppt_config.get('slides', 10)
            depth = ppt_config.get('depth', 'medium')
            theme = ppt_config.get('theme', 'default')

            # Phase 1: 读取模板文件和模板元数据
            logger.info(f"[{self.name}] Phase 1: 读取PPT模板")
            template_info = self._load_template_info(style)

            # Phase 2: 让LLM根据模板特性生成PPT内容
            logger.info(f"[{self.name}] Phase 2: 根据模板生成PPT内容")
            ppt_data = await self._generate_ppt_with_template(
                topic=topic,
                style=style,
                slides=slides,
                depth=depth,
                theme=theme,
                template_info=template_info,
                search_results=search_results
            )

            # Phase 3: 转换为HTML
            logger.info(f"[{self.name}] Phase 3: 渲染HTML")
            html_content = await self._convert_to_html(ppt_data, style, theme)

            logger.info(f"[{self.name}] PPT生成完成")

            return {
                "status": "success",
                "ppt": ppt_data,
                "html_content": html_content
            }

        except Exception as e:
            logger.error(f"[{self.name}] PPT生成失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _load_template_info(self, style: str) -> Dict[str, Any]:
        """读取模板文件和元数据"""
        from pathlib import Path
        import re

        template_dir = Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'ppt'
        template_file = template_dir / f"{style}.html"

        if not template_file.exists():
            logger.warning(f"模板文件不存在: {template_file}，使用business模板")
            template_file = template_dir / "business.html"

        # 读取模板内容
        template_content = template_file.read_text(encoding='utf-8')

        # 提取元数据
        metadata_match = re.search(r'<!-- METADATA: ({.*?}) -->', template_content)
        metadata = {}
        if metadata_match:
            import json
            metadata = json.loads(metadata_match.group(1))

        # 提取模板结构示例（前200行）
        template_lines = template_content.split('\n')[:200]
        template_structure = '\n'.join(template_lines)

        return {
            "style": style,
            "name": metadata.get("name", style),
            "description": metadata.get("description", ""),
            "template_structure": template_structure,
            "metadata": metadata
        }

    async def _generate_ppt_with_template(
        self,
        topic: str,
        style: str,
        slides: int,
        depth: str,
        theme: str,
        template_info: Dict[str, Any],
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """根据模板特性生成PPT内容"""

        # 准备搜索内容摘要
        content_summary = self._summarize_search_results(search_results)

        # 构建提示词
        system_prompt = self._build_template_aware_system_prompt(template_info, style, depth)
        user_prompt = self._build_template_aware_user_prompt(
            topic, slides, content_summary, template_info
        )

        # 使用结构化输出
        from ...llm.client import LLMClient

        # 获取LLM客户端
        llm_client = self.llm_manager.get_client("outline_generator")

        # 调用结构化输出
        ppt_result = await llm_client.get_structured_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_model=PPTData
        )

        # 转换为字典
        ppt_data = ppt_result.model_dump()

        # 添加元数据
        ppt_data["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "style": style,
            "theme": theme,
            "slide_count": len(ppt_data.get("slides", [])),
            "depth": depth
        }

        logger.info(f"[{self.name}] PPT内容生成成功，共 {len(ppt_data['slides'])} 页")

        return ppt_data

    def _summarize_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """总结搜索结果为可用内容"""
        summary_parts = []

        for i, result in enumerate(search_results[:15], 1):  # 取前15个
            title = result.get("title", "")
            content = result.get("content", "")[:800]  # 增加到800字，保留更多数据和案例
            url = result.get("url", "")

            summary_parts.append(f"""【资料{i}】{title}
来源: {url}
内容: {content}...
---""")

        return "\n\n".join(summary_parts)

    def _build_template_aware_system_prompt(
        self,
        template_info: Dict[str, Any],
        style: str,
        depth: str
    ) -> str:
        """构建模板感知的系统提示词"""

        style_guides = {
            "red": """你是RED风格PPT专家。

RED风格特点：
- **极简主义**：每页只有1-3个核心观点
- **短语表达**：每个要点3-8个字，不用完整句子
- **视觉冲击**：关键词醒目，易于记忆和分享
- **社交传播**：每页可以独立截图分享
- **内容密度**：minimal - 只保留最核心信息

**配色要求**：
- 必须使用**红色系**作为主色（#ff4757, #ee5a6f, #e84118等）
- 强调色用深色系（#2d3436, #1e272e, #c23616）
- 背景色用纯白或浅灰

**内容要求**：
1. **main_points**：必须是短语，不是句子！3-8个字
2. **detail_text**：可选，如有则不超过20字，补充核心数据
3. 每页最多3个要点
4. 标题简短有力（5-12字）

示例：
- title: "AI技术突破"
- main_points: ["推理能力飞跃", "成本暴降90%", "多模态融合"]
- detail_text: "从GPT-3到GPT-5的性能革命"
""",
            "business": """你是商务PPT专家。

商务风格特点：
- **结构清晰**：每页3-5个要点，每个要点必须有详细说明
- **逻辑严密**：符合商业汇报的逻辑，有层次感
- **数据支撑**：必须包含具体数字、百分比、时间、公司名称等硬数据
- **实例丰富**：引用真实的产品、公司、项目案例
- **内容密度**：detailed - 信息量大但表达简洁

**配色要求**：
- 必须使用**蓝色系**作为主色（#1e3a8a, #2563eb, #3b82f6等）
- 强调色用辅助蓝（#60a5fa, #93c5fd）
- 背景色用白色#ffffff

**内容要求**（重要！）：
1. **main_points**：每个要点15-25字，是完整的观点陈述
2. **detail_text**：**必填**，50-150字，包含：
   - 具体数字（如："市场规模达50亿美元"、"增长率35%"）
   - 时间节点（如："2024年Q3"、"2025年8月"）
   - 公司/产品案例（如："OpenAI的GPT-4"、"Meta的Llama"）
   - 对比数据（如："相比2023年提升3倍"）
3. **不要**只用data_items，要优先使用main_points + detail_text组合
4. data_items只在纯数字对比页面使用

**正确示例**：
```json
{{
  "title": "AI市场格局变化",
  "main_points": [
    "大语言模型市场爆发式增长，年复合增长率达35.2%",
    "中国市场投融资活跃，2023年投资金额达1809亿元",
    "头部企业占据主要市场份额，竞争格局初步形成"
  ],
  "detail_text": "根据Precedence Research数据，全球AI语言模型市场规模从2024年的56亿美元增长至2030年预计的361亿美元。OpenAI、Google、Anthropic三家占据70%市场份额，其中OpenAI的ChatGPT用户突破2亿。中国市场方面，较2022年增加1342.83亿元，增幅288%。百度文心一言、阿里通义千问、腾讯混元等国产大模型竞相推出。"
}}
```

**错误示例**（不要这样）：
```json
{{
  "title": "市场数据",
  "main_points": [],  // ❌ 错误！Business风格main_points不能为空
  "data_items": [{{"label": "规模", "value": "50亿"}}],  // ❌ 错误！不要只用数据，缺少详细说明
  "detail_text": null  // ❌ 错误！detail_text必填
}}
```
""",
            "academic": """你是学术PPT专家。
学术风格特点：
- **严谨专业**：每页包含详细论述和数据
- **逻辑论证**：注重因果关系和论证过程
- **引用支撑**：引用权威数据和研究
- **内容密度**：detailed - 内容详尽

示例页面内容：
- 标题："大语言模型的技术演进"
- 要点和详细说明（每个要点都有详细论述）
""",
            "creative": """你是创意PPT专家。
创意风格特点：
- **新颖独特**：用创意的表达方式
- **生动有趣**：语言活泼，容易记忆
- **视觉化**：善用比喻和类比
- **内容密度**：medium - 既有趣又有料
""",
            "simple": """你是极简PPT专家。
极简风格特点：
- **一页一观点**：每页只讲一个核心idea
- **简洁明了**：文字极少，重点突出
- **内容密度**：minimal - 只保留最核心信息
"""
        }

        template_desc = template_info.get("description", "")
        style_guide = style_guides.get(style, style_guides["business"])

        # 配色指南
        color_guides = {
            "red": """
配色要求（RED风格）- **必须使用红色系**：
- primary（主色）：**必须是红色**，如#ff4757, #ee5a6f, #e84118, #c23616
- accent（强调色）：深色系，如#2d3436, #1e272e, #c23616
- background（背景色）：纯白#ffffff或浅灰#f8f9fa
- text（文字色）：深灰#2d3436
- secondary（次要文字）：中灰#636e72

**禁止使用蓝色**作为主色！RED风格必须用红色！
""",
            "business": """
配色要求（商务风格）- **必须使用蓝色系**：
- primary（主色）：**必须是蓝色**，如#1e3a8a, #2563eb, #3b82f6, #1d4ed8
- accent（强调色）：辅助蓝，如#60a5fa, #93c5fd
- background（背景色）：白色#ffffff
- text（文字色）：深灰#1f2937
- secondary（次要文字）：灰色#6b7280

**但是**：根据PPT主题调整色调
- 科技/AI主题：蓝紫色（#3b82f6, #6366f1）
- 金融主题：深蓝+金色（#1e3a8a, #f59e0b）
- 餐饮/食品主题：**改用暖色**（#f97316橙色, #dc2626红色）
- 医疗健康：蓝绿色（#0ea5e9, #14b8a6）
- 教育培训：蓝橙组合（#3b82f6, #fb923c）
""",
            "academic": """
配色要求（学术风格）：
- primary（主色）：深蓝或墨绿，如#0f172a, #065f46, #1e3a8a
- accent（强调色）：金色或橙色，如#f59e0b, #ea580c
- background（背景色）：白色#ffffff
- text（文字色）：黑色#000000
- secondary（次要文字）：深灰#4b5563
""",
            "creative": """
配色要求（创意风格）：
- primary（主色）：鲜艳色，如#a855f7紫, #ec4899粉, #f43f5e红
- accent（强调色）：对比色，如#06b6d4青, #10b981绿
- background（背景色）：浅色#fafafa或渐变色
- text（文字色）：深色#18181b
- secondary（次要文字）：中灰#71717a
""",
            "simple": """
配色要求（极简风格）：
- primary（主色）：单一深色，如#18181b, #0f172a
- accent（强调色）：同色系浅色，如#52525b, #64748b
- background（背景色）：纯白#ffffff
- text（文字色）：黑色#000000
- secondary（次要文字）：灰色#a1a1aa
"""
        }

        color_guide = color_guides.get(style, color_guides["business"])

        return f"""{style_guide}

# 模板信息
- 模板名称：{template_info.get("name")}
- 模板描述：{template_desc}

# 配色方案
{color_guide}

**重要**：你需要根据PPT内容主题、行业特点和上述风格建议，选择最合适的配色方案。
- 科技类：蓝色、紫色
- 金融类：深蓝、金色
- 餐饮/食品：橙色、红色、绿色
- 医疗健康：蓝色、绿色
- 教育培训：蓝色、橙色
- 创意设计：紫色、粉色、渐变色

# 输出要求（多智能体架构）

你负责规划PPT的**设计方案**和**内容数据**，然后由专门的渲染智能体负责生成HTML。

生成JSON格式的PPT数据，包含：
- title: PPT总标题
- subtitle: 副标题
- colors: 配色方案对象 {{
    "primary": "#hex颜色",
    "accent": "#hex颜色",
    "background": "#hex颜色",
    "text": "#hex颜色",
    "secondary": "#hex颜色"
  }}
- slides: 幻灯片数组，每个slide包含：
  - slide_number: 页码
  - design: 设计方案 {{
      "layout_strategy": "布局策略（center_text|left_right_split|grid_cards|big_numbers|top_bottom|title_page|bullets|custom）",
      "visual_style": "视觉风格描述，用关键词触发不同样式：'卡片网格'/'左右分栏'/'编号列表'/'大数字对比'/'极简留白'",
      "color_usage": "配色使用建议（如'主色背景+白色文字'、'白底+主色标题'、'渐变背景'）"
    }}
  - content: 内容数据 {{
      "title": "页面标题",
      "main_points": ["要点1", "要点2", "要点3"],
      "data_items": [
        {{"label": "标签", "value": "数值"}},  // 可选，用于数据展示
        ...
      ],
      "detail_text": "详细说明文字",  // 可选
      "chart": {{  // 可选，添加图表可视化
        "type": "bar/line/pie/area",
        "data": {{
          "labels": ["2022", "2023", "2024"],
          "datasets": [
            {{"label": "市场规模", "data": [141, 294, 495]}}
          ]
        }},
        "title": "图表标题"
      }}
    }}

**关键要求**：
1. **设计与内容分离**：design字段描述"怎么呈现"，content字段提供"呈现什么"
2. **布局策略说明**：
   - title_page: 标题页，适合封面
   - center_text: 居中大字，适合章节页、引言
   - left_right_split: 左右分栏，适合对比、图文混排
   - grid_cards: 卡片网格，适合多要点展示
   - big_numbers: 大数字展示，适合关键指标
   - top_bottom: 上下布局，适合标题+内容分离
   - bullets: 列表布局，适合常规要点
   - custom: 自定义，由visual_style描述具体样式
3. **视觉风格要具体**：描述清楚你期望的视觉效果，如"左侧大标题右侧3个数据卡片"
4. **配色方案必须根据内容主题选择**（如餐饮用暖色、科技用蓝紫、金融用深蓝）
5. **数据项格式**：data_items用于展示关键数据，如[{{"label":"市场规模","value":"4850亿"}}]
6. RED风格要极简大胆，Business风格要专业详实，Creative风格要新颖有趣
"""

    def _build_template_aware_user_prompt(
        self,
        topic: str,
        slides: int,
        content_summary: str,
        template_info: Dict[str, Any]
    ) -> str:
        """构建用户提示词"""

        return f"""请根据以下主题和资料，生成一个{template_info.get('name')}风格的PPT。

# 主题
{topic}

# 目标页数
{slides}页（包括封面和总结）

# 可用资料
{content_summary}

# 要求
1. **严格按照{template_info.get('name')}的风格特点生成内容**
2. 第1页必须是封面页（layout_strategy: title_page）
3. 最后1页是总结页，总结核心要点
4. 中间可以插入章节分隔页（layout_strategy: center_text）来分隔不同主题

5. **配色方案**（重要！）：
   - RED风格：**必须用红色**作为primary（#ff4757等），禁止用蓝色
   - Business风格：根据主题选择配色
     * 科技/AI主题：蓝紫色（#3b82f6, #6366f1）
     * 餐饮/食品主题：橙红色（#f97316, #dc2626）
     * 金融主题：深蓝+金色（#1e3a8a, #f59e0b）
     * 医疗健康：蓝绿色（#0ea5e9, #14b8a6）
   - Creative风格：鲜艳对比色（紫色#a855f7, 粉色#ec4899等）

6. **从可用资料中提取具体数据和案例**：
   - Business/Academic风格：必须引用资料中的具体数字、百分比、公司名、产品名、时间
   - 不要泛泛而谈，要有具体evidence
   - RED/Simple风格：提炼核心数据和金句

7. **根据风格控制内容密度**（关键！）：
   - RED/Simple:
     * 每页1-3个main_points
     * 每个要点3-8字短语
     * detail_text可选，不超过20字
   - Business:
     * **每页必须有3-5个main_points**（不能为空数组！）
     * **detail_text必填**，50-150字，包含具体数字、时间、公司案例
     * 不要只用data_items，要用main_points + detail_text组合
   - Academic:
     * 每页3-4个main_points
     * detail_text包含详细论述（80-150字）

**重要**：仔细阅读可用资料，提取其中的具体数据、案例、公司名、产品名、时间节点！

请以JSON格式输出。

**RED风格示例**（极简、红色系）：
```json
{{
  "title": "AI革命",
  "subtitle": "技术突破",
  "colors": {{
    "primary": "#ff4757",  // 必须是红色！
    "accent": "#2d3436",
    "background": "#ffffff",
    "text": "#2d3436",
    "secondary": "#636e72"
  }},
  "slides": [
    {{
      "slide_number": 1,
      "design": {{"layout_strategy": "title_page", "visual_style": "大标题居中，红色渐变", "color_usage": "红色渐变背景+白色文字"}},
      "content": {{"title": "AI革命", "main_points": [], "detail_text": "技术突破"}}
    }},
    {{
      "slide_number": 2,
      "design": {{"layout_strategy": "bullets", "visual_style": "极简大字留白", "color_usage": "白底+红色标题"}},
      "content": {{"title": "核心突破", "main_points": ["推理能力飞跃", "成本暴降90%", "多模态融合"], "detail_text": "从GPT-3到GPT-5的性能革命"}}
    }}
  ]
}}
```

**Business风格示例**（详实、根据主题配色）：
```json
{{
  "title": "2025预制菜产业报告",
  "subtitle": "万亿赛道的破局之战",
  "colors": {{
    "primary": "#f97316",  // 餐饮主题用橙色，不是蓝色！
    "accent": "#fb923c",
    "background": "#ffffff",
    "text": "#1f2937",
    "secondary": "#6b7280"
  }},
  "slides": [
    {{
      "slide_number": 1,
      "design": {{"layout_strategy": "title_page", "visual_style": "专业标题页", "color_usage": "橙色渐变背景+白色文字"}},
      "content": {{"title": "2025预制菜产业报告", "main_points": [], "detail_text": "万亿赛道的破局之战"}}
    }},
    {{
      "slide_number": 2,
      "design": {{"layout_strategy": "bullets", "visual_style": "卡片网格，要点突出", "color_usage": "白底+橙色标题"}},
      "content": {{
        "title": "市场规模快速增长",
        "main_points": [
          "2024年市场规模达4850亿元，同比增长33.8%",
          "预计2026年突破万亿，年复合增长率30%+",
          "B端占比65%，C端增速45%领先",
          "头部企业C端营收占比超40%"
        ],
        "detail_text": "数据来源：艾媒咨询2024年预制菜行业报告"
      }}
    }},
    {{
      "slide_number": 3,
      "design": {{"layout_strategy": "bullets", "visual_style": "左右分栏，左侧要点右侧图表", "color_usage": "白底+橙色标题"}},
      "content": {{
        "title": "市场规模增长趋势",
        "main_points": [
          "2022-2024年保持高速增长",
          "年复合增长率超30%",
          "2026年预计突破万亿"
        ],
        "chart": {{
          "type": "bar",
          "data": {{
            "labels": ["2022", "2023", "2024", "2025E", "2026E"],
            "datasets": [
              {{"label": "市场规模（亿元）", "data": [3200, 4100, 4850, 6500, 10000]}}
            ]
          }},
          "title": "中国预制菜市场规模"
        }},
        "detail_text": "数据来源：艾媒咨询"
      }}
    }}
  ]
}}
```

**关键点**：
- **配色必须根据风格和主题选择**：RED用红色，餐饮用橙色，科技用蓝紫色
- **Business风格main_points不能为空**，每页3-5个要点，detail_text必填且包含具体数据
- **RED风格main_points是短语**（3-8字），detail_text可选
- **visual_style要多样化**：不要每页都用"要点+详细说明"，要变化使用：
  * 第2页：卡片网格
  * 第3页：左右分栏对比
  * 第4页：大数字展示
  * 第5页：编号列表
  * 第6页：极简章节页
  * 避免单调重复！
- **重要：积极使用图表**：
  * 趋势数据 → line图表（折线图）
  * 对比数据 → bar图表（柱状图）
  * 占比数据 → pie图表（饼图）
  * 至少2-3页使用图表，提升可视化效果
"""

    async def _parallel_generate_slides(
        self,
        slide_outlines: List[Dict[str, Any]],
        style: str,
        available_content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """并行生成所有页面内容"""

        logger.info(f"[{self.name}] 开始并行生成 {len(slide_outlines)} 页内容")

        tasks = []
        for i, slide_outline in enumerate(slide_outlines):
            # 构建上下文（包含前一页信息）
            context = {}
            if i > 0:
                context["previous_slide"] = slide_outlines[i - 1]

            task = self.slide_content_generator.generate_slide_content(
                slide_outline=slide_outline,
                style=style,
                available_content=available_content,
                context=context
            )
            tasks.append(task)

        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        slides_content = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[{self.name}] 页面 {i+1} 生成失败: {result}")
                # 使用fallback
                slides_content.append({
                    "slide_number": i + 1,
                    "type": slide_outlines[i].get("type", "content"),
                    "title": slide_outlines[i].get("title", ""),
                    "subtitle": "",
                    "content": {
                        "points": ["生成失败"],
                        "details": {},
                        "visuals": []
                    }
                })
            else:
                slides_content.append(result)

        logger.info(f"[{self.name}] 并行生成完成")
        return slides_content

    def _assemble_ppt(
        self,
        outline: Dict[str, Any],
        slides_content: List[Dict[str, Any]],
        topic: str,
        style: str,
        theme: str
    ) -> Dict[str, Any]:
        """组装PPT"""

        logger.info(f"[{self.name}] 开始组装PPT")

        # 排序页面
        slides_sorted = sorted(slides_content, key=lambda x: x.get("slide_number", 0))

        ppt_data = {
            "title": outline.get("title", topic),
            "subtitle": outline.get("subtitle", ""),
            "slides": slides_sorted,
            "metadata": {
                "topic": topic,
                "style": style,
                "theme": theme,
                "slide_count": len(slides_sorted),
                "generated_at": datetime.now().isoformat(),
                "generator": "XunLong PPT Generator"
            }
        }

        logger.info(f"[{self.name}] PPT组装完成，共 {len(slides_sorted)} 页")

        return ppt_data

    async def _convert_to_html(
        self,
        ppt_data: Dict[str, Any],
        style: str,
        theme: str
    ) -> str:
        """将PPT转换为HTML格式 - 使用SlideRenderAgent渲染（临时方案）"""
        try:
            from .slide_render_agent import SlideRenderAgent

            logger.info(f"[{self.name}] 使用SlideRenderAgent渲染HTML")

            # 创建渲染智能体
            render_agent = SlideRenderAgent(colors=ppt_data.get('colors', {}))

            # 渲染每个幻灯片
            rendered_slides = []
            for slide_data in ppt_data.get('slides', []):
                # 将Slide数据转换为渲染所需格式
                slide = Slide(**slide_data)

                # 使用RenderAgent渲染
                rendered = render_agent.render_slide(
                    slide_number=slide.slide_number,
                    design=slide.design,
                    content=slide.content
                )

                rendered_slides.append(rendered)

            # 使用flexible.html模板生成最终HTML
            html_content = self._build_html_from_slides(
                ppt_data=ppt_data,
                rendered_slides=rendered_slides
            )

            logger.info(f"[{self.name}] HTML转换完成")
            return html_content

        except Exception as e:
            logger.error(f"[{self.name}] HTML转换失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回简单的HTML fallback
            return self._get_fallback_html(ppt_data)

    def _get_css_component_guide(self) -> str:
        """获取CSS组件库简化说明"""
        return """# 可用CSS工具类
- 文本: .text-xs/.text-xl/.text-5xl/.text-9xl, .font-bold/.font-black, .text-center
- 颜色: .text-primary/.text-white, .bg-primary/.bg-white/.gradient-primary
- 布局: .flex/.flex-col/.flex-1, .items-center/.justify-center, .grid/.grid-cols-2/.grid-cols-3
- 间距: .gap-4/.gap-8/.gap-16, .p-8/.p-16, .mt-4/.mb-8
- 装饰: .rounded-xl, .shadow-lg, .border-l-4, .card
- 动画: .animate-fadeIn/.animate-slideUp
- 尺寸: .w-full/.w-1\\/2, .h-full/.h-64/.h-80/.h-96"""

    async def _generate_slide_html(
        self,
        slide_data: Dict[str, Any],
        colors: Dict[str, str],
        css_guide: str,
        style: str
    ) -> str:
        """使用LLM为单个幻灯片生成HTML"""

        design = slide_data.get('design', {})
        content = slide_data.get('content', {})

        prompt = f"""请根据以下设计方案和内容，生成一个完整的HTML片段（幻灯片内容）。

# 设计方案
- 布局策略: {design.get('layout_strategy', 'bullets')}
- 视觉风格: {design.get('visual_style', '')}
- 配色使用: {design.get('color_usage', '')}

# 内容数据
- 标题: {content.get('title', '')}
- 要点: {content.get('main_points', [])}
- 数据项: {content.get('data_items', [])}
- 详细说明: {content.get('detail_text', '')}

# 配色方案
{colors}

{css_guide}

**要求**：
1. 根据visual_style的描述，创造性地设计HTML结构
2. 充分利用Flex、Grid、大字号等CSS类
3. 确保布局符合PPT风格（{style}风格）
4. HTML要包含在一个容器div内，不要包含<html>/<body>等标签
5. **重要**：不同页面要有不同的布局创意，不要千篇一律！

只输出HTML代码，不要任何解释：
"""

        # 调用LLM生成HTML
        llm_client = self.llm_manager.get_client("outline_generator")

        response = await llm_client.get_completion(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.8  # 提高温度增加创造性
        )

        # 清理返回的HTML
        html = response.strip()
        # 移除可能的markdown代码块标记
        if html.startswith('```html'):
            html = html[7:]
        if html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]

        return html.strip()

    def _build_html_from_slides(
        self,
        ppt_data: Dict[str, Any],
        rendered_slides: List[Dict[str, str]]
    ) -> str:
        """使用flexible.html模板组装最终HTML"""
        from jinja2 import Environment, FileSystemLoader
        from pathlib import Path

        # 加载模板
        template_dir = Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'ppt'
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('flexible.html')

        # 准备渲染数据
        render_data = {
            'title': ppt_data.get('title', 'PPT'),
            'subtitle': ppt_data.get('subtitle', ''),
            'colors': ppt_data.get('colors', {}),
            'slides': rendered_slides,
            'metadata': ppt_data.get('metadata', {}),
            'generated_at': ppt_data.get('metadata', {}).get('generated_at', ''),
            'generator': 'XunLong PPT Generator'
        }

        # 渲染HTML
        html = template.render(**render_data)
        return html

    def _get_fallback_html(self, ppt_data: Dict[str, Any]) -> str:
        """生成fallback HTML"""
        slides_html = []
        for slide in ppt_data.get("slides", []):
            slides_html.append(f"""
<div class="slide">
    <h2>{slide.get('title', '')}</h2>
    <ul>
        {''.join(f'<li>{p}</li>' for p in slide.get('content', {}).get('points', []))}
    </ul>
</div>
""")

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{ppt_data.get('title', 'PPT')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .slide {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
        h2 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>{ppt_data.get('title', 'PPT')}</h1>
    {''.join(slides_html)}
</body>
</html>
"""

    async def _generate_outline_v2(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        style: str,
        slides: int
    ) -> Dict[str, Any]:
        """
        Phase 1: 生成PPT大纲（只包含元数据，不生成具体内容）
        """
        content_summary = self._summarize_search_results(search_results)

        # 构建简化的大纲生成提示词
        prompt = f"""请为以下主题生成PPT大纲（只需要结构和主题，不需要具体内容）。

# 主题
{topic}

# 风格
{style}

# 目标页数
{slides}页

# 可用资料
{content_summary[:2000]}

# 要求
1. 第1页是封面页（page_type: title）
2. 最后1页是总结页（page_type: conclusion）
3. 中间可以插入章节分隔页（page_type: section）
4. 其他是内容页（page_type: content）
5. 每页只需要：主题（topic）和关键要点提示（key_points，2-4个关键词）
6. 标记需要图表的页面（has_chart: true），至少2-3页使用图表
7. 根据风格选择配色：
   - RED风格：红色系（#ff4757等）
   - Business风格科技主题：蓝紫色（#3b82f6, #6366f1）
   - Business风格餐饮主题：橙红色（#f97316, #dc2626）

请以JSON格式输出：
{{
  "title": "PPT标题",
  "subtitle": "副标题",
  "colors": {{
    "primary": "#3b82f6",
    "accent": "#6366f1",
    "background": "#ffffff",
    "text": "#1f2937",
    "secondary": "#6b7280"
  }},
  "pages": [
    {{
      "slide_number": 1,
      "page_type": "title",
      "topic": "2025人工智能发展报告",
      "key_points": [],
      "has_chart": false
    }},
    {{
      "slide_number": 2,
      "page_type": "content",
      "topic": "市场规模与增长",
      "key_points": ["市场规模", "增长趋势", "预测数据"],
      "has_chart": true
    }}
  ]
}}
"""

        llm_client = self.llm_manager.get_client("outline_generator")

        # 使用结构化输出
        outline_result = await llm_client.get_structured_response(
            prompt=prompt,
            response_model=PPTOutline
        )

        return outline_result.model_dump()

    async def _parallel_generate_pages(
        self,
        outline: Dict[str, Any],
        search_results: List[Dict[str, Any]],
        style: str
    ) -> List[Dict[str, Any]]:
        """
        Phase 2: 并行生成所有页面HTML

        为每个页面创建独立的PageAgent，并行执行
        """
        from .page_agent import PageAgent, PageSpec, GlobalContext

        # 准备全局上下文
        global_context = GlobalContext(
            ppt_title=outline['title'],
            style=style,
            colors=outline['colors'],
            total_slides=len(outline['pages'])
        )

        # 准备内容素材
        content_summary = self._summarize_search_results(search_results)
        css_guide = self._get_css_component_guide()

        # 创建PageAgent
        llm_client = self.llm_manager.get_client("outline_generator")
        page_agent = PageAgent(llm_client, css_guide)

        # 为每个页面创建生成任务
        tasks = []
        for page_outline in outline['pages']:
            page_spec = PageSpec(**page_outline)

            task = page_agent.generate_page_html(
                page_spec=page_spec,
                global_context=global_context,
                content_data=content_summary
            )
            tasks.append(task)

        # 并行执行所有任务
        logger.info(f"[{self.name}] 并行生成{len(tasks)}个页面...")
        page_htmls = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        results = []
        for i, html in enumerate(page_htmls):
            if isinstance(html, Exception):
                logger.error(f"[{self.name}] 页面{i+1}生成失败: {html}")
                # 使用fallback
                results.append({
                    "slide_number": i + 1,
                    "html_content": f"<div class='flex items-center justify-center h-full'><p class='text-2xl'>页面生成失败</p></div>"
                })
            else:
                results.append({
                    "slide_number": i + 1,
                    "html_content": html
                })

        return results

    def _assemble_ppt_v2(
        self,
        outline: Dict[str, Any],
        page_htmls: List[Dict[str, Any]]
    ) -> str:
        """
        Phase 3: 组装最终PPT

        将所有页面HTML插入flexible.html模板
        """
        from jinja2 import Environment, FileSystemLoader
        from pathlib import Path

        # 加载模板
        template_dir = Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'ppt'
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('flexible.html')

        # 准备slides数据（flexible.html需要的格式）
        slides = []
        for page in page_htmls:
            slides.append({
                'slide_number': page['slide_number'],
                'html_content': page['html_content'],
                'custom_style': ''  # 可以后续添加自定义样式
            })

        # 渲染HTML
        html = template.render(
            title=outline['title'],
            subtitle=outline.get('subtitle', ''),
            colors=outline['colors'],
            slides=slides,
            metadata={'generated_at': datetime.now().isoformat()}
        )

        return html

    def get_status(self) -> Dict[str, Any]:
        """获取协调器状态"""
        return {
            "name": self.name,
            "agents": {
                "outline_generator": self.outline_generator.name,
                "slide_content_generator": self.slide_content_generator.name
            }
        }
