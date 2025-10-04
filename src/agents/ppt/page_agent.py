"""
PageAgent - 单页PPT生成智能体

每个PageAgent负责生成一个完整的PPT页面HTML
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class PageSpec(BaseModel):
    """页面规格 - 从大纲中获取"""
    slide_number: int = Field(description="页码")
    page_type: str = Field(description="页面类型: title/content/section/conclusion")
    topic: str = Field(description="本页主题")
    key_points: list[str] = Field(description="关键要点提示")
    has_chart: bool = Field(default=False, description="是否需要图表")


class GlobalContext(BaseModel):
    """全局上下文 - 所有PageAgent共享"""
    ppt_title: str = Field(description="PPT总标题")
    style: str = Field(description="风格: red/business/academic/creative/simple")
    colors: Dict[str, str] = Field(description="配色方案")
    total_slides: int = Field(description="总页数")


class PageAgent:
    """单页PPT生成智能体"""

    def __init__(self, llm_client, css_guide: str):
        """
        初始化PageAgent

        Args:
            llm_client: LLM客户端
            css_guide: CSS组件库说明
        """
        self.llm_client = llm_client
        self.css_guide = css_guide

    async def generate_page_html(
        self,
        page_spec: PageSpec,
        global_context: GlobalContext,
        content_data: str
    ) -> str:
        """
        生成单个页面的完整HTML

        Args:
            page_spec: 页面规格
            global_context: 全局上下文
            content_data: 可用的内容素材

        Returns:
            完整的HTML片段（一个div容器）
        """
        prompt = self._build_prompt(page_spec, global_context, content_data)

        logger.info(f"[PageAgent] 生成第{page_spec.slide_number}页: {page_spec.topic}")

        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.9  # 高温度，鼓励创造性
        )

        # 提取返回的内容
        html = response.get("content", "").strip()
        if html.startswith('```html'):
            html = html[7:]
        if html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]

        return html.strip()

    def _build_prompt(
        self,
        page_spec: PageSpec,
        global_context: GlobalContext,
        content_data: str
    ) -> str:
        """构建生成提示词"""

        # 根据page_type给出布局建议
        layout_hints = {
            'title': '封面页：超大标题居中，渐变背景，极简设计',
            'section': '章节页：大字居中，留白充足，突出主题',
            'content': '内容页：左右分栏/卡片网格/列表布局，内容丰富',
            'conclusion': '总结页：核心要点突出，呼应主题'
        }

        chart_hint = ""
        if page_spec.has_chart:
            chart_hint = """
**重要**：本页需要包含图表！
你必须生成**完整的Chart.js代码**，包括：

1. Canvas元素（带唯一ID）：
   <canvas id="chart_12345"></canvas>

2. Chart.js初始化脚本（必须包含在<script>标签中，使用唯一ID）：
   <script>
   document.addEventListener('DOMContentLoaded', function() {
       const canvas = document.getElementById('chart_12345');
       if (!canvas) return;

       const ctx = canvas.getContext('2d');
       new Chart(ctx, {
           type: 'bar',  // bar, line, pie, doughnut等
           data: {
               labels: ['2020', '2021', '2022', '2023', '2024'],
               datasets: [{
                   label: '数据名称',
                   data: [100, 120, 150, 180, 200],
                   backgroundColor: 'rgba(59, 130, 246, 0.5)',
                   borderColor: 'rgba(59, 130, 246, 1)',
                   borderWidth: 2
               }]
           },
           options: {
               responsive: true,
               maintainAspectRatio: false,
               plugins: {
                   title: {
                       display: true,
                       text: '图表标题'
                   }
               }
           }
       });
   });
   </script>

**图表数据要求**：
- **Canvas ID必须唯一**！使用页码+随机数，如：chart_{page_spec.slide_number}_{{random_number}}
- 数据必须基于内容素材中的真实信息
- 如果没有具体数据，创造合理的示例数据
- 图表类型要符合数据特点（趋势用line，对比用bar，占比用pie）
- 为canvas容器设置固定高度（如：style="height: 400px" 或 class="h-96"）
- **script标签中的ID必须和canvas的ID完全一致**
"""

        return f"""你是一个PPT页面设计专家。请为第{page_spec.slide_number}页生成**完整的HTML代码**。

# 全局上下文（所有页面共享）
- PPT标题: {global_context.ppt_title}
- 风格: {global_context.style}
- 配色方案: {global_context.colors}
- 总页数: {global_context.total_slides}

# 本页规格
- 页码: {page_spec.slide_number}/{global_context.total_slides}
- 页面类型: {page_spec.page_type}
- 主题: {page_spec.topic}
- 关键要点: {page_spec.key_points}

# 布局建议
{layout_hints.get(page_spec.page_type, '内容页：自由发挥')}

{chart_hint}

# 可用内容素材
{content_data[:1000]}  # 截取部分内容

{self.css_guide}

**要求**：
1. 生成一个**完整的div容器**，包含本页所有内容
2. **关键**：页面固定尺寸为100vw × 100vh，内容**绝对不能溢出**！
   - 使用`class="flex flex-col h-full w-full p-12"`作为根容器
   - 标题、内容、底部说明要合理分配空间
   - 如果内容过多，**必须删减**，不能让内容超出页面
   - 字体大小要适中，避免过大导致溢出
3. 充分发挥创造力，设计独特的布局
4. 使用CSS工具类组合样式，不要内联style
5. **不要**生成<html>/<body>等标签，只要一个div

**布局建议**：
- 标题区：占10-15%高度（text-4xl或text-5xl）
- 内容区：占70-80%高度（flex-1，让它自动填充）
- 底部说明：占5-10%高度（text-sm或text-base）

只输出HTML代码，不要任何解释：
"""
