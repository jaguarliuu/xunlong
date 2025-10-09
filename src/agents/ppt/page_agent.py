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
    style: str = Field(description=": red/business/academic/creative/simple")
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

        # 
        html = response.get("content", "").strip()
        if html.startswith('```html'):
            html = html[7:]
        if html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]

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
        """"""

        # page_type
        layout_hints = {
            'title': '',
            'section': '',
            'content': '//',
            'conclusion': ''
        }

        chart_hint = ""
        if page_spec.has_chart:
            chart_hint = """
****
**Chart.js**

1. CanvasID
   <canvas id="chart_12345"></canvas>

2. Chart.js<script>ID
   <script>
   document.addEventListener('DOMContentLoaded', function() {
       const canvas = document.getElementById('chart_12345');
       if (!canvas) return;

       const ctx = canvas.getContext('2d');
       new Chart(ctx, {
           type: 'bar',  // bar, line, pie, doughnut
           data: {
               labels: ['2020', '2021', '2022', '2023', '2025'],
               datasets: [{
                   label: '',
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
                       text: ''
                   }
               }
           }
       });
   });
   </script>

****
- **Canvas ID**+chart_{page_spec.slide_number}_{{random_number}}
- 
- 
- linebarpie
- canvasstyle="height: 400px"  class="h-96"
- **scriptIDcanvasID**
"""

        return f"""PPT{page_spec.slide_number}**HTML**

# 
- PPT: {global_context.ppt_title}
- : {global_context.style}
- : {global_context.colors}
- : {global_context.total_slides}

# 
- : {page_spec.slide_number}/{global_context.total_slides}
- : {page_spec.page_type}
- : {page_spec.topic}
- : {page_spec.key_points}

# 
{layout_hints.get(page_spec.page_type, '')}

{chart_hint}

# 
{content_data[:1000]}  # 

{self.css_guide}

****
1. **div**
2. ****100vw  100vh****
   - `class="flex flex-col h-full w-full p-12"`
   - 
   - ****
   - 
3. 
4. CSSstyle
5. ****<html>/<body>div

****
- 10-15%text-4xltext-5xl
- 70-80%flex-1
- 5-10%text-smtext-base

HTML
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
