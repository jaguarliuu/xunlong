"""
PageAgent - PPT

PageAgentPPTHTML
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class PageSpec(BaseModel):
    """ - """
    slide_number: int = Field(description="")
    page_type: str = Field(description=": title/content/section/conclusion")
    topic: str = Field(description="")
    key_points: list[str] = Field(description="")
    has_chart: bool = Field(default=False, description="")


class GlobalContext(BaseModel):
    """ - PageAgent"""
    ppt_title: str = Field(description="PPT")
    style: str = Field(description=": ted/business/academic/creative/simple")
    colors: Dict[str, str] = Field(description="")
    total_slides: int = Field(description="")
    speech_scene: Optional[str] = Field(default=None, description="")


class PageAgent:
    """PPT"""

    def __init__(self, llm_client, css_guide: str):
        """
        PageAgent

        Args:
            llm_client: LLM
            css_guide: CSS
        """
        self.llm_client = llm_client
        self.css_guide = css_guide

    async def generate_page_html(
        self,
        page_spec: PageSpec,
        global_context: GlobalContext,
        content_data: str
    ) -> Dict[str, str]:
        """
        HTML

        Args:
            page_spec: 
            global_context: 
            content_data: 

        Returns:
            
            - html_content: HTMLdiv
            - speech_notes: 
        """
        prompt = self._build_prompt(page_spec, global_context, content_data)

        logger.info(f"[PageAgent] {page_spec.slide_number}: {page_spec.topic}")

        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.9  #
        )

        # 清理LLM输出：去除描述性文本和代码块标记
        html = response.get("content", "").strip()

        # 1. 查找第一个HTML标签的位置
        import re

        # 查找第一个 < 开始的HTML标签
        first_tag_match = re.search(r'<[a-zA-Z!]', html)
        if first_tag_match:
            # 去除HTML之前的所有描述性文本
            html = html[first_tag_match.start():]

        # 2. 去除markdown代码块标记
        if html.startswith('```html'):
            html = html[7:]
        if html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]

        # 3. 再次清理可能的前置文本
        html = html.strip()
        first_tag_match = re.search(r'<[a-zA-Z!]', html)
        if first_tag_match and first_tag_match.start() > 0:
            html = html[first_tag_match.start():]

        result = {"html_content": html.strip()}

        # 
        if global_context.speech_scene:
            speech_notes = await self._generate_speech_notes(
                page_spec, global_context, content_data, html
            )
            result["speech_notes"] = speech_notes

        return result

    def _build_prompt(
        self,
        page_spec: PageSpec,
        global_context: GlobalContext,
        content_data: str
    ) -> str:
        """TODO: Add docstring."""

        # page_type
        layout_hints = {
            'title': '',
            'section': '',
            'content': '//',
            'conclusion': ''
        }

        # 根据风格添加特殊布局提示
        style_hint = ""
        if global_context.style == 'ted':
            style_hint = """
****TED演讲风格要求（重要！）****
这是TED演讲风格的PPT，必须遵循以下原则：

1. **极简内容**:
   - 每页只有1个大标题 + 1-3句核心观点
   - 标题要用超大字号（text-6xl或text-7xl，font-size: 3-5rem）
   - 核心观点用大字号（text-2xl或text-3xl，font-size: 1.5-2rem）
   - **不要**长段落、不要详细列表、不要密集文字

2. **视觉冲击**:
   - 大量留白，内容居中
   - 使用全局配色方案中的大胆颜色
   - 背景简洁，突出核心信息

3. **布局比例**:
   - 标题区占30-40%（超大标题）
   - 核心观点区占30-40%（1-3句话）
   - 其他区域留白
   - 页脚极简（只显示页码）

4. **禁止元素**:
   - ❌ 不要多级列表
   - ❌ 不要详细数据表格
   - ❌ 不要长段落说明
   - ❌ 不要复杂布局

**TED风格示例**:
```html
<div style="height: 60%; display: flex; align-items: center; justify-content: center;">
    <h1 style="font-size: 4rem; font-weight: bold; text-align: center;">
        核心观点标题
    </h1>
</div>
<div style="height: 30%; display: flex; align-items: center; justify-content: center;">
    <p style="font-size: 1.8rem; text-align: center; max-width: 70%;">
        一句话说明核心观点
    </p>
</div>
```
"""
        elif global_context.style == 'business':
            style_hint = """
****商务汇报风格要求****
这是商务汇报风格的PPT，可以包含详细内容：

1. **内容详实**: 可以包含多个要点、数据、图表
2. **结构清晰**: 使用列表、卡片等组织内容
3. **专业布局**: 标题、内容区、图表合理分布
4. **字号适中**: 标题text-4xl (2.5rem)，正文text-base (1rem)
"""

        chart_hint = ""
        if page_spec.has_chart:
            chart_hint = """
****图表生成要求****
**使用Chart.js创建图表**

1. **Canvas元素要求**
   <canvas id="chart_{page_spec.slide_number}_{{random_number}}"></canvas>

2. **图表容器高度限制（重要！）**
   图表容器必须设置明确的高度，避免超出页面范围：
   - 推荐使用固定高度：height: 350px 或 height: 400px
   - 或使用max-height限制：max-height: 400px
   - **不要**使用flex: 1或100%高度，会导致图表超出页面

3. **Chart.js配置示例**
   <script>
   document.addEventListener('DOMContentLoaded', function() {{
       const canvas = document.getElementById('chart_{{page_spec.slide_number}}_12345');
       if (!canvas) return;

       const ctx = canvas.getContext('2d');
       new Chart(ctx, {{
           type: 'bar',  // bar, line, pie, doughnut
           data: {{
               labels: ['2020', '2021', '2022', '2023', '2024'],
               datasets: [{{
                   label: '数据标签',
                   data: [100, 120, 150, 180, 200],
                   backgroundColor: 'rgba(59, 130, 246, 0.5)',
                   borderColor: 'rgba(59, 130, 246, 1)',
                   borderWidth: 2
               }}]
           }},
           options: {{
               responsive: true,
               maintainAspectRatio: false,
               plugins: {{
                   legend: {{ display: true }}
               }},
               scales: {{
                   y: {{ beginAtZero: true }}
               }}
           }}
       }});
   }});
   </script>

****重要注意事项****
- **Canvas ID**: 使用chart_{{page_spec.slide_number}}_{{随机数}}避免ID冲突
- **图表容器**: 必须设置固定高度（如height: 350px），不要用flex: 1
- **图表类型**: bar（柱状图）、line（折线图）、pie（饼图）、doughnut（环形图）
- **responsive**: 设为true，图表会自适应容器
- **maintainAspectRatio**: 设为false，图表高度由容器控制
- **script标签中的ID**: 必须与canvas的ID完全一致
"""

        return f"""你是一个HTML代码生成器。你只能输出HTML代码，不能输出任何其他内容。

# 任务
为PPT第{page_spec.slide_number}页生成完整的HTML代码

# 全局信息
- PPT标题: {global_context.ppt_title}
- 风格: {global_context.style}
- 配色: {global_context.colors}
- 总页数: {global_context.total_slides}

# 本页信息
- 页码: {page_spec.slide_number}/{global_context.total_slides}
- 类型: {page_spec.page_type}
- 主题: {page_spec.topic}
- 要点: {page_spec.key_points}

# 风格要求
{style_hint}

# 布局建议
{layout_hints.get(page_spec.page_type, '')}

{chart_hint}

# 内容数据
{content_data[:1000]}

{self.css_guide}

# ================================
# 严格输出要求 (CRITICAL!)
# ================================

**你必须严格遵守以下规则，否则输出将被拒绝:**

1. **只输出HTML代码！不要输出任何说明、描述、注释、设计思路！**
2. **不要输出markdown代码块标记！不要```html或```！**
3. **不要输出"基于您提供的内容"、"我将创建"、"## 设计说明"等描述性文字！**
4. **直接从<!DOCTYPE html>开始输出，到</html>结束！**
5. **HTML必须是完整的、自包含的页面，100vw × 100vh全屏布局**
6. **使用全局配色方案中的颜色，不得自行修改**
7. **必须包含完整的<head>部分，包含Chart.js引用（如果需要图表）**

**禁止的输出示例（这些都是错误的）：**
❌ "# 宠物市场分析..."
❌ "基于您提供的内容，我将创建..."
❌ "```html"
❌ "## 设计说明"
❌ "以下是HTML代码："

**正确的输出格式（唯一正确的格式）：**
✅ 直接输出：<!DOCTYPE html><html lang="zh-CN"><head>...

**布局比例建议:**
- 页眉（标题区）占10-15%，使用text-4xl或text-5xl
- 内容区占70-80%，使用flex-1
- 页脚（页码等）占5-10%，使用text-sm或text-base

**再次强调：只输出HTML代码！不要任何解释！立即开始输出HTML代码：**
"""

    async def _generate_speech_notes(
        self,
        page_spec: PageSpec,
        global_context: GlobalContext,
        content_data: str,
        html_content: str
    ) -> str:
        """
        

        Args:
            page_spec: 
            global_context: 
            content_data: 
            html_content: HTML

        Returns:
            
        """
        prompt = f"""PPT{page_spec.slide_number}

# 
{global_context.speech_scene}

# PPT
- PPT: {global_context.ppt_title}
- : {page_spec.slide_number}/{global_context.total_slides}
- : {page_spec.page_type}

# 
- : {page_spec.topic}
- : {page_spec.key_points}

# 
{html_content[:500]}  # HTML

# 
1. **{global_context.speech_scene}**
2. 
   - title(): 
   - section(): 
   - content(): 
   - conclusion(): 
3. 150-300
4. 
5. 
6. ****


"""

        logger.info(f"[PageAgent] {page_spec.slide_number}")

        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7  # 
        )

        speech_notes = response.get("content", "").strip()

        return speech_notes
