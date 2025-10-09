"""
PPT - PPT
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


# ==========  ==========
class PPTOutline(BaseModel):
    """PPT - """
    title: str = Field(description="PPT")
    subtitle: Optional[str] = Field(default=None, description="")
    colors: Dict[str, str] = Field(description="{primary, accent, background, text, secondary}")
    pages: List[Dict[str, Any]] = Field(description="{slide_number, page_type, topic, key_points, has_chart}")


# ==========  ==========
class ColorScheme(BaseModel):
    """TODO: Add docstring."""
    primary: str = Field(description="#ff4757")
    accent: str = Field(description="")
    background: str = Field(description="")
    text: str = Field(description="")
    secondary: str = Field(description="")


class SlideDesign(BaseModel):
    """TODO: Add docstring."""
    layout_strategy: str = Field(description=": center_text|left_right_split|grid_cards|big_numbers|top_bottom|custom")
    visual_style: str = Field(description="''''''")
    color_usage: str = Field(description="'+''+'")


class SlideContent(BaseModel):
    """TODO: Add docstring."""
    title: Optional[str] = Field(default=None, description="")
    main_points: List[str] = Field(description="3-5")
    data_items: Optional[List[Dict[str, str]]] = Field(default=None, description="[{'label':'','value':'4850'}]")
    detail_text: Optional[str] = Field(default=None, description="")
    chart: Optional[Dict[str, Any]] = Field(default=None, description="typedata")


class Slide(BaseModel):
    """ - """
    slide_number: int = Field(description="")
    design: SlideDesign = Field(description="")
    content: SlideContent = Field(description="")


class PPTData(BaseModel):
    """PPT"""
    title: str = Field(description="PPT")
    subtitle: Optional[str] = Field(default=None, description="")
    colors: ColorScheme = Field(description="")
    slides: List[Slide] = Field(description="")


class PPTCoordinator:
    """PPT - PPT"""

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager
    ):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.name = "PPT"

        # 
        self.outline_generator = PPTOutlineGenerator(llm_manager, prompt_manager)
        self.slide_content_generator = SlideContentGenerator(llm_manager, prompt_manager)

    async def generate_ppt_v2(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        ppt_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        PPT ()

        Phase 1: OutlineAgent
        Phase 2: NPageAgentHTML
        Phase 3: AssemblerAgentPPT
        """
        logger.info(f"[{self.name}] PPT: {topic}")

        try:
            style = ppt_config.get('style', 'business')
            slides = ppt_config.get('slides', 10)
            speech_notes = ppt_config.get('speech_notes')  # 

            # Phase 1: 
            logger.info(f"[{self.name}] Phase 1: PPT")
            outline = await self._generate_outline_v2(topic, search_results, style, slides)

            # Phase 2: HTML
            logger.info(f"[{self.name}] Phase 2: {len(outline['pages'])}")
            page_results = await self._parallel_generate_pages(
                outline=outline,
                search_results=search_results,
                style=style,
                speech_scene=speech_notes  # 
            )

            # Phase 3: PPT
            logger.info(f"[{self.name}] Phase 3: PPT")
            html_content = self._assemble_ppt_v2(outline, page_results)

            # 
            speech_notes_data = None
            if speech_notes:
                speech_notes_data = []
                for page in page_results:
                    if "speech_notes" in page:
                        speech_notes_data.append({
                            "slide_number": page["slide_number"],
                            "speech_notes": page["speech_notes"]
                        })

            result = {
                "status": "success",
                "ppt": {
                    "title": outline['title'],
                    "subtitle": outline.get('subtitle', ''),
                    "colors": outline['colors'],
                    "slides": page_results,  # html_contentspeech_notes
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "style": style,
                        "slide_count": len(page_results),
                        "has_speech_notes": bool(speech_notes)
                    }
                },
                "html_content": html_content
            }

            # 
            if speech_notes_data:
                result["speech_notes"] = speech_notes_data

            return result

        except Exception as e:
            logger.error(f"[{self.name}] PPT: {e}")
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
        PPT

        Args:
            topic: PPT
            search_results: 
            ppt_config: PPT
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
                    "title": "PPT",
                    "subtitle": "",
                    "slides": [...],
                    "metadata": {...}
                },
                "html_content": "HTMLPPT"
            }
        """

        logger.info(f"[{self.name}] PPT: {topic}")
        logger.info(f"[{self.name}] PPT: {ppt_config}")

        try:
            style = ppt_config.get('style', 'business')
            logger.info(f"[{self.name}] : {style}")
            slides = ppt_config.get('slides', 10)
            depth = ppt_config.get('depth', 'medium')
            theme = ppt_config.get('theme', 'default')

            # Phase 1: 
            logger.info(f"[{self.name}] Phase 1: PPT")
            template_info = self._load_template_info(style)

            # Phase 2: LLMPPT
            logger.info(f"[{self.name}] Phase 2: PPT")
            ppt_data = await self._generate_ppt_with_template(
                topic=topic,
                style=style,
                slides=slides,
                depth=depth,
                theme=theme,
                template_info=template_info,
                search_results=search_results
            )

            # Phase 3: HTML
            logger.info(f"[{self.name}] Phase 3: HTML")
            html_content = await self._convert_to_html(ppt_data, style, theme)

            logger.info(f"[{self.name}] PPT")

            return {
                "status": "success",
                "ppt": ppt_data,
                "html_content": html_content
            }

        except Exception as e:
            logger.error(f"[{self.name}] PPT: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _load_template_info(self, style: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        from pathlib import Path
        import re

        template_dir = Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'ppt'
        template_file = template_dir / f"{style}.html"

        if not template_file.exists():
            logger.warning(f": {template_file}business")
            template_file = template_dir / "business.html"

        # 
        template_content = template_file.read_text(encoding='utf-8')

        # 
        metadata_match = re.search(r'<!-- METADATA: ({.*?}) -->', template_content)
        metadata = {}
        if metadata_match:
            import json
            metadata = json.loads(metadata_match.group(1))

        # 200
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
        """PPT"""

        # 
        content_summary = self._summarize_search_results(search_results)

        # 
        system_prompt = self._build_template_aware_system_prompt(template_info, style, depth)
        user_prompt = self._build_template_aware_user_prompt(
            topic, slides, content_summary, template_info
        )

        # 
        from ...llm.client import LLMClient

        # LLM
        llm_client = self.llm_manager.get_client("outline_generator")

        # 
        ppt_result = await llm_client.get_structured_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_model=PPTData
        )

        # 
        ppt_data = ppt_result.model_dump()

        # 
        ppt_data["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "style": style,
            "theme": theme,
            "slide_count": len(ppt_data.get("slides", [])),
            "depth": depth
        }

        logger.info(f"[{self.name}] PPT {len(ppt_data['slides'])} ")

        return ppt_data

    def _summarize_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """TODO: Add docstring."""
        summary_parts = []

        for i, result in enumerate(search_results[:15], 1):  # 15
            title = result.get("title", "")
            content = result.get("content", "")[:800]  # 800
            url = result.get("url", "")

            summary_parts.append(f"""{i}{title}
: {url}
: {content}...
---""")

        return "\n\n".join(summary_parts)

    def _build_template_aware_system_prompt(
        self,
        template_info: Dict[str, Any],
        style: str,
        depth: str
    ) -> str:
        """TODO: Add docstring."""

        style_guides = {
            "red": """REDPPT

RED
- ****1-3
- ****3-8
- ****
- ****
- ****minimal - 

****
- ****#ff4757, #ee5a6f, #e84118
- #2d3436, #1e272e, #c23616
- 

****
1. **main_points**3-8
2. **detail_text**20
3. 3
4. 5-12


- title: "AI"
- main_points: ["", "90%", ""]
- detail_text: "GPT-3GPT-5"
""",
            "business": """PPT


- ****3-5
- ****
- ****
- ****
- ****detailed - 

****
- ****#1e3a8a, #2563eb, #3b82f6
- #60a5fa, #93c5fd
- #ffffff

****
1. **main_points**15-25
2. **detail_text******50-150
   - "50""35%"
   - "2025Q3""20258"
   - /"OpenAIGPT-4""MetaLlama"
   - "20233"
3. ****data_itemsmain_points + detail_text
4. data_items

****
```json
{{
  "title": "AI",
  "main_points": [
    "35.2%",
    "20231809",
    ""
  ],
  "detail_text": "Precedence ResearchAI2025562030361OpenAIGoogleAnthropic70%OpenAIChatGPT220221342.83288%"
}}
```

****
```json
{{
  "title": "",
  "main_points": [],  //  Businessmain_points
  "data_items": [{{"label": "", "value": "50"}}],  //  
  "detail_text": null  //  detail_text
}}
```
""",
            "academic": """PPT

- ****
- ****
- ****
- ****detailed - 


- ""
- 
""",
            "creative": """PPT

- ****
- ****
- ****
- ****medium - 
""",
            "simple": """PPT

- ****idea
- ****
- ****minimal - 
"""
        }

        template_desc = template_info.get("description", "")
        style_guide = style_guides.get(style, style_guides["business"])

        # 
        color_guides = {
            "red": """
RED- ****
- primary****#ff4757, #ee5a6f, #e84118, #c23616
- accent#2d3436, #1e272e, #c23616
- background#ffffff#f8f9fa
- text#2d3436
- secondary#636e72

****RED
""",
            "business": """
- ****
- primary****#1e3a8a, #2563eb, #3b82f6, #1d4ed8
- accent#60a5fa, #93c5fd
- background#ffffff
- text#1f2937
- secondary#6b7280

****PPT
- /AI#3b82f6, #6366f1
- +#1e3a8a, #f59e0b
- /****#f97316, #dc2626
- #0ea5e9, #14b8a6
- #3b82f6, #fb923c
""",
            "academic": """

- primary#0f172a, #065f46, #1e3a8a
- accent#f59e0b, #ea580c
- background#ffffff
- text#000000
- secondary#4b5563
""",
            "creative": """

- primary#a855f7, #ec4899, #f43f5e
- accent#06b6d4, #10b981
- background#fafafa
- text#18181b
- secondary#71717a
""",
            "simple": """

- primary#18181b, #0f172a
- accent#52525b, #64748b
- background#ffffff
- text#000000
- secondary#a1a1aa
"""
        }

        color_guide = color_guides.get(style, color_guides["business"])

        return f"""{style_guide}

# 
- {template_info.get("name")}
- {template_desc}

# 
{color_guide}

****PPT
- 
- 
- /
- 
- 
- 

# 

PPT********HTML

JSONPPT
- title: PPT
- subtitle: 
- colors:  {{
    "primary": "#hex",
    "accent": "#hex",
    "background": "#hex",
    "text": "#hex",
    "secondary": "#hex"
  }}
- slides: slide
  - slide_number: 
  - design:  {{
      "layout_strategy": "center_text|left_right_split|grid_cards|big_numbers|top_bottom|title_page|bullets|custom",
      "visual_style": "''/''/''/''/''",
      "color_usage": "'+''+'''"
    }}
  - content:  {{
      "title": "",
      "main_points": ["1", "2", "3"],
      "data_items": [
        {{"label": "", "value": ""}},  // 
        ...
      ],
      "detail_text": "",  // 
      "chart": {{  // 
        "type": "bar/line/pie/area",
        "data": {{
          "labels": ["2022", "2023", "2025"],
          "datasets": [
            {{"label": "", "data": [141, 294, 495]}}
          ]
        }},
        "title": ""
      }}
    }}

****
1. ****design""content""
2. ****
   - title_page: 
   - center_text: 
   - left_right_split: 
   - grid_cards: 
   - big_numbers: 
   - top_bottom: +
   - bullets: 
   - custom: visual_style
3. ****"3"
4. ****
5. ****data_items[{{"label":"","value":"4850"}}]
6. REDBusinessCreative
"""

    def _build_template_aware_user_prompt(
        self,
        topic: str,
        slides: int,
        content_summary: str,
        template_info: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""

        return f"""{template_info.get('name')}PPT

# 
{topic}

# 
{slides}

# 
{content_summary}

# 
1. **{template_info.get('name')}**
2. 1layout_strategy: title_page
3. 1
4. layout_strategy: center_text

5. ****
   - RED****primary#ff4757
   - Business
     * /AI#3b82f6, #6366f1
     * /#f97316, #dc2626
     * +#1e3a8a, #f59e0b
     * #0ea5e9, #14b8a6
   - Creative#a855f7, #ec4899

6. ****
   - Business/Academic
   - evidence
   - RED/Simple

7. ****
   - RED/Simple:
     * 1-3main_points
     * 3-8
     * detail_text20
   - Business:
     * **3-5main_points**
     * **detail_text**50-150
     * data_itemsmain_points + detail_text
   - Academic:
     * 3-4main_points
     * detail_text80-150

****

JSON

**RED**
```json
{{
  "title": "AI",
  "subtitle": "",
  "colors": {{
    "primary": "#ff4757",  // 
    "accent": "#2d3436",
    "background": "#ffffff",
    "text": "#2d3436",
    "secondary": "#636e72"
  }},
  "slides": [
    {{
      "slide_number": 1,
      "design": {{"layout_strategy": "title_page", "visual_style": "", "color_usage": "+"}},
      "content": {{"title": "AI", "main_points": [], "detail_text": ""}}
    }},
    {{
      "slide_number": 2,
      "design": {{"layout_strategy": "bullets", "visual_style": "", "color_usage": "+"}},
      "content": {{"title": "", "main_points": ["", "90%", ""], "detail_text": "GPT-3GPT-5"}}
    }}
  ]
}}
```

**Business**
```json
{{
  "title": "2025",
  "subtitle": "",
  "colors": {{
    "primary": "#f97316",  // 
    "accent": "#fb923c",
    "background": "#ffffff",
    "text": "#1f2937",
    "secondary": "#6b7280"
  }},
  "slides": [
    {{
      "slide_number": 1,
      "design": {{"layout_strategy": "title_page", "visual_style": "", "color_usage": "+"}},
      "content": {{"title": "2025", "main_points": [], "detail_text": ""}}
    }},
    {{
      "slide_number": 2,
      "design": {{"layout_strategy": "bullets", "visual_style": "", "color_usage": "+"}},
      "content": {{
        "title": "",
        "main_points": [
          "2025485033.8%",
          "202630%+",
          "B65%C45%",
          "C40%"
        ],
        "detail_text": "2025"
      }}
    }},
    {{
      "slide_number": 3,
      "design": {{"layout_strategy": "bullets", "visual_style": "", "color_usage": "+"}},
      "content": {{
        "title": "",
        "main_points": [
          "2022-2025",
          "30%",
          "2026"
        ],
        "chart": {{
          "type": "bar",
          "data": {{
            "labels": ["2022", "2023", "2025", "2025E", "2026E"],
            "datasets": [
              {{"label": "", "data": [3200, 4100, 4850, 6500, 10000]}}
            ]
          }},
          "title": ""
        }},
        "detail_text": ""
      }}
    }}
  ]
}}
```

****
- ****RED
- **Businessmain_points**3-5detail_text
- **REDmain_points**3-8detail_text
- **visual_style**"+"
  * 2
  * 3
  * 4
  * 5
  * 6
  * 
- ****
  *   line
  *   bar
  *   pie
  * 2-3
"""

    async def _parallel_generate_slides(
        self,
        slide_outlines: List[Dict[str, Any]],
        style: str,
        available_content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""

        logger.info(f"[{self.name}]  {len(slide_outlines)} ")

        tasks = []
        for i, slide_outline in enumerate(slide_outlines):
            # 
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

        # 
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 
        slides_content = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[{self.name}]  {i+1} : {result}")
                # fallback
                slides_content.append({
                    "slide_number": i + 1,
                    "type": slide_outlines[i].get("type", "content"),
                    "title": slide_outlines[i].get("title", ""),
                    "subtitle": "",
                    "content": {
                        "points": [""],
                        "details": {},
                        "visuals": []
                    }
                })
            else:
                slides_content.append(result)

        logger.info(f"[{self.name}] ")
        return slides_content

    def _assemble_ppt(
        self,
        outline: Dict[str, Any],
        slides_content: List[Dict[str, Any]],
        topic: str,
        style: str,
        theme: str
    ) -> Dict[str, Any]:
        """PPT"""

        logger.info(f"[{self.name}] PPT")

        # 
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

        logger.info(f"[{self.name}] PPT {len(slides_sorted)} ")

        return ppt_data

    async def _convert_to_html(
        self,
        ppt_data: Dict[str, Any],
        style: str,
        theme: str
    ) -> str:
        """PPTHTML - SlideRenderAgent"""
        try:
            from .slide_render_agent import SlideRenderAgent

            logger.info(f"[{self.name}] SlideRenderAgentHTML")

            # 
            render_agent = SlideRenderAgent(colors=ppt_data.get('colors', {}))

            # 
            rendered_slides = []
            for slide_data in ppt_data.get('slides', []):
                # Slide
                slide = Slide(**slide_data)

                # RenderAgent
                rendered = render_agent.render_slide(
                    slide_number=slide.slide_number,
                    design=slide.design,
                    content=slide.content
                )

                rendered_slides.append(rendered)

            # flexible.htmlHTML
            html_content = self._build_html_from_slides(
                ppt_data=ppt_data,
                rendered_slides=rendered_slides
            )

            logger.info(f"[{self.name}] HTML")
            return html_content

        except Exception as e:
            logger.error(f"[{self.name}] HTML: {e}")
            import traceback
            traceback.print_exc()
            # HTML fallback
            return self._get_fallback_html(ppt_data)

    def _get_css_component_guide(self) -> str:
        """CSS"""
        return """# CSS
- : .text-xs/.text-xl/.text-5xl/.text-9xl, .font-bold/.font-black, .text-center
- : .text-primary/.text-white, .bg-primary/.bg-white/.gradient-primary
- : .flex/.flex-col/.flex-1, .items-center/.justify-center, .grid/.grid-cols-2/.grid-cols-3
- : .gap-4/.gap-8/.gap-16, .p-8/.p-16, .mt-4/.mb-8
- : .rounded-xl, .shadow-lg, .border-l-4, .card
- : .animate-fadeIn/.animate-slideUp
- : .w-full/.w-1\\/2, .h-full/.h-64/.h-80/.h-96"""

    async def _generate_slide_html(
        self,
        slide_data: Dict[str, Any],
        colors: Dict[str, str],
        css_guide: str,
        style: str
    ) -> str:
        """LLMHTML"""

        design = slide_data.get('design', {})
        content = slide_data.get('content', {})

        prompt = f"""HTML

# 
- : {design.get('layout_strategy', 'bullets')}
- : {design.get('visual_style', '')}
- : {design.get('color_usage', '')}

# 
- : {content.get('title', '')}
- : {content.get('main_points', [])}
- : {content.get('data_items', [])}
- : {content.get('detail_text', '')}

# 
{colors}

{css_guide}

****
1. visual_styleHTML
2. FlexGridCSS
3. PPT{style}
4. HTMLdiv<html>/<body>
5. ****

HTML
"""

        # LLMHTML
        llm_client = self.llm_manager.get_client("outline_generator")

        response = await llm_client.get_completion(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.8  # 
        )

        # HTML
        html = response.strip()
        # markdown
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
        """flexible.htmlHTML"""
        from jinja2 import Environment, FileSystemLoader
        from pathlib import Path

        # 
        template_dir = Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'ppt'
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('flexible.html')

        # 
        render_data = {
            'title': ppt_data.get('title', 'PPT'),
            'subtitle': ppt_data.get('subtitle', ''),
            'colors': ppt_data.get('colors', {}),
            'slides': rendered_slides,
            'metadata': ppt_data.get('metadata', {}),
            'generated_at': ppt_data.get('metadata', {}).get('generated_at', ''),
            'generator': 'XunLong PPT Generator'
        }

        # HTML
        html = template.render(**render_data)
        return html

    def _get_fallback_html(self, ppt_data: Dict[str, Any]) -> str:
        """fallback HTML"""
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
        Phase 1: PPT
        """
        content_summary = self._summarize_search_results(search_results)

        # 
        prompt = f"""PPT

# 
{topic}

# 
{style}

# 
{slides}

# 
{content_summary[:2000]}

# 
1. 1page_type: title
2. 1page_type: conclusion
3. page_type: section
4. page_type: content
5. topickey_points2-4
6. has_chart: true2-3
7. 
   - RED#ff4757
   - Business#3b82f6, #6366f1
   - Business#f97316, #dc2626

JSON
{{
  "title": "PPT",
  "subtitle": "",
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
      "topic": "2025",
      "key_points": [],
      "has_chart": false
    }},
    {{
      "slide_number": 2,
      "page_type": "content",
      "topic": "",
      "key_points": ["", "", ""],
      "has_chart": true
    }}
  ]
}}
"""

        llm_client = self.llm_manager.get_client("outline_generator")

        # 
        outline_result = await llm_client.get_structured_response(
            prompt=prompt,
            response_model=PPTOutline
        )

        return outline_result.model_dump()

    async def _parallel_generate_pages(
        self,
        outline: Dict[str, Any],
        search_results: List[Dict[str, Any]],
        style: str,
        speech_scene: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Phase 2: HTML

        PageAgent
        """
        from .page_agent import PageAgent, PageSpec, GlobalContext

        # 
        global_context = GlobalContext(
            ppt_title=outline['title'],
            style=style,
            colors=outline['colors'],
            total_slides=len(outline['pages']),
            speech_scene=speech_scene  # 
        )

        # 
        content_summary = self._summarize_search_results(search_results)
        css_guide = self._get_css_component_guide()

        # PageAgent
        llm_client = self.llm_manager.get_client("outline_generator")
        page_agent = PageAgent(llm_client, css_guide)

        # 
        tasks = []
        for page_outline in outline['pages']:
            page_spec = PageSpec(**page_outline)

            task = page_agent.generate_page_html(
                page_spec=page_spec,
                global_context=global_context,
                content_data=content_summary
            )
            tasks.append(task)

        # 
        logger.info(f"[{self.name}] {len(tasks)}...")
        page_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 
        results = []
        for i, result in enumerate(page_results):
            if isinstance(result, Exception):
                logger.error(f"[{self.name}] {i+1}: {result}")
                # fallback
                results.append({
                    "slide_number": i + 1,
                    "html_content": f"<div class='flex items-center justify-center h-full'><p class='text-2xl'></p></div>",
                    "speech_notes": None
                })
            else:
                # result{"html_content": "...", "speech_notes": "..."}
                page_data = {
                    "slide_number": i + 1,
                    "html_content": result.get("html_content", ""),
                }
                if "speech_notes" in result:
                    page_data["speech_notes"] = result.get("speech_notes")
                results.append(page_data)

        return results

    def _assemble_ppt_v2(
        self,
        outline: Dict[str, Any],
        page_htmls: List[Dict[str, Any]]
    ) -> str:
        """
        Phase 3: PPT

        HTMLflexible.html
        """
        from jinja2 import Environment, FileSystemLoader
        from pathlib import Path

        # 
        template_dir = Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'ppt'
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('flexible.html')

        # slidesflexible.html
        slides = []
        for page in page_htmls:
            slides.append({
                'slide_number': page['slide_number'],
                'html_content': page['html_content'],
                'custom_style': ''  # 
            })

        # HTML
        html = template.render(
            title=outline['title'],
            subtitle=outline.get('subtitle', ''),
            colors=outline['colors'],
            slides=slides,
            metadata={'generated_at': datetime.now().isoformat()}
        )

        return html

    def get_status(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "name": self.name,
            "agents": {
                "outline_generator": self.outline_generator.name,
                "slide_content_generator": self.slide_content_generator.name
            }
        }
