"""
Design Coordinator Agent - PPT全局设计协调器

在大纲生成后、页面生成前，生成统一的配色方案、主题风格、设计模式
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
import logging
import json

logger = logging.getLogger(__name__)


class DesignSpec(BaseModel):
    """PPT全局设计规范"""

    # 配色方案
    primary_color: str = Field(description="主色调 (hex)")
    secondary_color: str = Field(description="次要色 (hex)")
    accent_color: str = Field(description="强调色 (hex)")
    background_color: str = Field(description="背景色 (hex)")
    text_color: str = Field(description="文字色 (hex)")
    text_secondary_color: str = Field(description="次要文字色 (hex)")

    # 字体方案
    title_font_size: str = Field(description="标题字号")
    content_font_size: str = Field(description="正文字号")
    font_family: str = Field(description="字体族")

    # 布局风格
    layout_style: str = Field(description="布局风格: modern/business/minimal/creative")
    spacing: str = Field(description="间距风格: compact/normal/spacious")
    border_radius: str = Field(description="圆角大小: 0px/0.5rem/1rem")

    # 视觉元素
    use_shadows: bool = Field(description="是否使用阴影")
    use_gradients: bool = Field(description="是否使用渐变")
    animation_style: str = Field(description="动画风格: none/subtle/dynamic")

    # 图表配色
    chart_colors: list[str] = Field(description="图表配色数组")


class DesignCoordinator:
    """PPT全局设计协调器"""

    def __init__(self, llm_client):
        """
        初始化设计协调器

        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client

    async def generate_design_spec(
        self,
        topic: str,
        outline: Dict[str, Any],
        style: str
    ) -> DesignSpec:
        """
        生成PPT全局设计规范

        Args:
            topic: PPT主题
            outline: PPT大纲
            style: 用户指定的风格 (ted/business/academic/creative/simple)

        Returns:
            DesignSpec: 设计规范对象
        """
        prompt = self._build_design_prompt(topic, outline, style)

        logger.info(f"[DesignCoordinator] 生成设计规范: {topic}")

        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.9  # 提高创造性，让LLM更自由地选择配色
        )

        # 解析LLM返回的JSON
        content = response.get("content", "").strip()

        # 清理可能的markdown代码块标记
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()

        try:
            design_dict = json.loads(content)
            design_spec = DesignSpec(**design_dict)
            logger.info(f"[DesignCoordinator] 设计规范生成成功: {design_spec.layout_style}风格")
            return design_spec
        except Exception as e:
            logger.error(f"[DesignCoordinator] 解析设计规范失败: {e}")
            # 返回默认设计规范
            return self._get_default_design(style)

    def _build_design_prompt(
        self,
        topic: str,
        outline: Dict[str, Any],
        style: str
    ) -> str:
        """构建设计生成提示词"""

        # 提取大纲关键信息
        pages = outline.get('pages', [])
        page_topics = [p.get('topic', '') for p in pages[:5]]  # 前5个页面主题

        style_guides = {
            'ted': 'TED演讲风格，极简主义，每页只有大标题+核心观点，文字极少，适合现场演讲。配色根据主题灵活选择，要大胆有冲击力',
            'business': '商务汇报风格，内容详实，包含详细数据、图表、要点列表，适合专业汇报。配色根据主题内容灵活选择',
            'academic': '学术严谨风格，配色应该根据主题内容选择，可以使用深色系或其他合适的颜色',
            'creative': '创意活泼风格，鼓励使用大胆、有趣的配色',
            'simple': '极简主义风格，使用简洁配色，但可以根据主题选择合适的颜色'
        }

        style_hint = style_guides.get(style, '根据主题内容自由选择合适的配色')

        return f"""你是一位富有创意的PPT视觉设计师。请根据PPT主题内容，设计一套独特、吸引人的视觉方案。

# PPT主题分析
**主题**: {topic}
**主要内容**: {', '.join(page_topics)}
**风格**: {style} - {style_hint}

# 设计任务
**请根据主题内容的特点，创造性地设计配色方案和视觉风格！**

## 配色设计要点
1. **风格优先级**:
   - **如果风格是 {style}，请优先遵循该风格的要求**
   - ted风格：大胆冲击力的配色，根据主题选择最吸引人的颜色组合
   - business风格：专业但灵活，根据主题选择合适配色，不局限于蓝色
   - creative风格：大胆使用对比色和鲜艳色彩

2. **主题相关性** (在遵循风格的前提下):
   - 游戏主题？考虑鲜艳、活力的颜色（如紫色、橙色、青色、品红等）
   - 宠物主题？考虑温暖、可爱的颜色（如粉色、浅橙、天蓝、草绿等）
   - 科技主题？考虑未来感的颜色（如深蓝、青色、紫色等）
   - 自然/环保主题？考虑绿色系、大地色系
   - 美食主题？考虑暖色系（红、橙、黄）
   - 金融/专业主题？考虑稳重的颜色（深蓝、墨绿、灰色）

3. **色彩搭配**: 主色、次色、强调色要形成有趣的对比和呼应
4. **可读性**: 确保文字和背景有足够的对比度

## 视觉元素设计
- **layout_style**: 根据主题选择（modern/playful/elegant/tech/artistic/minimal等）
- **use_gradients**: 游戏、科技类主题适合用渐变
- **border_radius**: 可爱主题用大圆角，专业主题用小圆角
- **animation_style**: 活泼主题用dynamic，严肃主题用subtle或none

# 创意示例

**TED演讲风格示例 (适用于ted风格)**:
{{
    "primary_color": "#dc2626",  // 大胆的主色 - 根据主题选择
    "secondary_color": "#1f2937",  // 深色 - 对比
    "accent_color": "#fbbf24",  // 强调色 - 吸引注意
    "background_color": "#ffffff",
    "title_font_size": "4rem",  // TED风格用超大标题
    "content_font_size": "1.5rem",  // 正文也要大
    "use_shadows": false,  // 极简，不用阴影
    "use_gradients": false,  // 极简，不用渐变
    "animation_style": "none",  // 极简，不用动画
    "chart_colors": ["#dc2626", "#1f2937", "#fbbf24", "#6b7280", "#f97316"]
}}

**游戏主题示例**:
{{
    "primary_color": "#8b5cf6",  // 紫色 - 游戏感
    "secondary_color": "#ec4899",  // 品红 - 活力
    "accent_color": "#f59e0b",  // 橙色 - 强调
    "chart_colors": ["#8b5cf6", "#ec4899", "#06b6d4", "#10b981", "#f59e0b"]
}}

**宠物主题示例**:
{{
    "primary_color": "#f472b6",  // 粉色 - 可爱
    "secondary_color": "#fb923c",  // 浅橙 - 温暖
    "accent_color": "#60a5fa",  // 天蓝 - 清新
    "chart_colors": ["#f472b6", "#fb923c", "#a78bfa", "#34d399", "#fbbf24"]
}}

**科技/AI主题示例**:
{{
    "primary_color": "#06b6d4",  // 青色 - 科技感
    "secondary_color": "#8b5cf6",  // 紫色 - 未来感
    "accent_color": "#10b981",  // 绿色 - 智能
    "chart_colors": ["#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899"]
}}

# 输出要求
**只输出JSON！不要任何说明！**

JSON结构:
{{
    "primary_color": "#xxxxxx",
    "secondary_color": "#xxxxxx",
    "accent_color": "#xxxxxx",
    "background_color": "#ffffff",
    "text_color": "#1f2937",
    "text_secondary_color": "#6b7280",
    "title_font_size": "2.5rem",
    "content_font_size": "1rem",
    "font_family": "'Segoe UI', 'Microsoft YaHei', sans-serif",
    "layout_style": "根据主题选择",
    "spacing": "normal",
    "border_radius": "1rem",
    "use_shadows": true,
    "use_gradients": true,
    "animation_style": "subtle",
    "chart_colors": ["颜色1", "颜色2", "颜色3", "颜色4", "颜色5"]
}}

**重要提示**:
- 当前风格是 "{style}"，请严格遵循该风格的要求
- ted风格要超大字体(title_font_size: 4rem)、极简设计、大胆配色
- business风格要详实内容、适中字体、专业配色
- 不要总是用蓝色！根据主题"{topic}"选择最合适的颜色
- 要有创意，让配色方案与主题内容相呼应
- chart_colors要包含5种协调的颜色

立即输出JSON:
"""

    def _get_default_design(self, style: str) -> DesignSpec:
        """获取默认设计规范"""

        default_designs = {
            'ted': DesignSpec(
                primary_color="#dc2626",
                secondary_color="#1f2937",
                accent_color="#fbbf24",
                background_color="#ffffff",
                text_color="#1f2937",
                text_secondary_color="#6b7280",
                title_font_size="4rem",  # TED风格超大标题
                content_font_size="1.5rem",  # TED风格大正文
                font_family="'Segoe UI', 'Microsoft YaHei', sans-serif",
                layout_style="minimal",  # 极简布局
                spacing="spacious",  # 宽松间距
                border_radius="0px",  # 无圆角，极简
                use_shadows=False,  # 无阴影
                use_gradients=False,  # 无渐变
                animation_style="none",  # 无动画
                chart_colors=["#dc2626", "#1f2937", "#fbbf24", "#6b7280", "#f97316"]
            ),
            'business': DesignSpec(
                primary_color="#2563eb",
                secondary_color="#1d4ed8",
                accent_color="#3b82f6",
                background_color="#ffffff",
                text_color="#1f2937",
                text_secondary_color="#6b7280",
                title_font_size="2.5rem",
                content_font_size="1rem",
                font_family="'Segoe UI', 'Microsoft YaHei', sans-serif",
                layout_style="business",
                spacing="normal",
                border_radius="0.5rem",
                use_shadows=True,
                use_gradients=True,
                animation_style="subtle",
                chart_colors=["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#dbeafe"]
            ),
            'simple': DesignSpec(
                primary_color="#1f2937",
                secondary_color="#374151",
                accent_color="#4b5563",
                background_color="#ffffff",
                text_color="#1f2937",
                text_secondary_color="#6b7280",
                title_font_size="2.5rem",
                content_font_size="1rem",
                font_family="'Segoe UI', 'Microsoft YaHei', sans-serif",
                layout_style="minimal",
                spacing="spacious",
                border_radius="0px",
                use_shadows=False,
                use_gradients=False,
                animation_style="none",
                chart_colors=["#1f2937", "#374151", "#4b5563", "#6b7280", "#9ca3af"]
            )
        }

        return default_designs.get(style, default_designs['business'])

    def design_spec_to_dict(self, design_spec: DesignSpec) -> Dict[str, Any]:
        """将DesignSpec转换为字典，用于传递给PageAgent"""
        return design_spec.model_dump()
