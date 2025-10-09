"""
SlideRenderAgent - 

+HTML
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class SlideDesign(BaseModel):
    """TODO: Add docstring."""
    layout_strategy: str = Field(description="")
    visual_style: str = Field(description="")
    color_usage: str = Field(description="")


class SlideContent(BaseModel):
    """TODO: Add docstring."""
    title: Optional[str] = Field(default=None, description="")
    main_points: List[str] = Field(description="3-5")
    data_items: Optional[List[Dict[str, str]]] = Field(default=None, description="")
    detail_text: Optional[str] = Field(default=None, description="")


class SlideRenderAgent:
    """TODO: Add docstring."""

    def __init__(self, colors: Optional[Dict[str, str]] = None):
        """
        

        Args:
            colors:  {primary, accent, background, text, secondary}
        """
        self.colors = colors or {
            'primary': '#3b82f6',
            'accent': '#60a5fa',
            'background': '#ffffff',
            'text': '#1f2937',
            'secondary': '#6b7280'
        }

    def render_slide(
        self,
        slide_number: int,
        design: SlideDesign,
        content: SlideContent
    ) -> Dict[str, str]:
        """
        

        Args:
            slide_number: 
            design: 
            content: 

        Returns:
            {'html_content': '...', 'custom_style': '...'}
        """
        # layout_strategy
        layout_renderers = {
            'center_text': self._render_center_text,
            'left_right_split': self._render_left_right_split,
            'grid_cards': self._render_grid_cards,
            'big_numbers': self._render_big_numbers,
            'top_bottom': self._render_top_bottom,
            'title_page': self._render_title_page,
            'bullets': self._render_bullets,
            'custom': self._render_custom
        }

        renderer = layout_renderers.get(
            design.layout_strategy,
            self._render_custom
        )

        html_content = renderer(design, content)
        custom_style = self._generate_custom_style(design)

        return {
            'html_content': html_content,
            'custom_style': custom_style,
            'slide_number': slide_number
        }

    def _generate_custom_style(self, design: SlideDesign) -> str:
        """TODO: Add docstring."""
        styles = []

        # color_usage
        if '' in design.color_usage or '' in design.color_usage:
            styles.append(f"background: {self.colors['primary']};")
        elif '' in design.color_usage or '' in design.color_usage:
            styles.append("background: #ffffff;")
        elif '' in design.color_usage:
            styles.append(f"background: linear-gradient(135deg, {self.colors['primary']}, {self.colors['accent']});")

        return ' '.join(styles)

    def _render_title_page(
        self,
        design: SlideDesign,
        content: SlideContent
    ) -> str:
        """TODO: Add docstring."""
        text_color = 'text-white' if '' in design.color_usage else 'text-text'

        html = f"""
        <div class="flex flex-col items-center justify-center h-full w-full animate-fadeIn">
            <h1 class="text-7xl font-bold {text_color} mb-8 text-center">
                {content.title or ''}
            </h1>
            {f'<p class="text-2xl {text_color} opacity-75">{content.detail_text}</p>' if content.detail_text else ''}
        </div>
        """
        return html

    def _render_center_text(
        self,
        design: SlideDesign,
        content: SlideContent
    ) -> str:
        """ - """
        text_color = 'text-white' if '' in design.color_usage else 'text-text'

        html = f"""
        <div class="flex flex-col items-center justify-center h-full w-full animate-fadeIn">
            {f'<h2 class="text-6xl font-bold {text_color} mb-6 text-center">{content.title}</h2>' if content.title else ''}
            <div class="text-3xl {text_color} opacity-90 text-center max-w-4xl">
                {content.detail_text or ''}
            </div>
        </div>
        """
        return html

    def _render_left_right_split(
        self,
        design: SlideDesign,
        content: SlideContent
    ) -> str:
        """TODO: Add docstring."""
        html = f"""
        <div class="flex flex-col h-full w-full p-12 animate-slideUp">
            {f'<h2 class="text-5xl font-bold text-primary mb-12">{content.title}</h2>' if content.title else ''}
            <div class="flex flex-row gap-12 flex-1">
                <div class="w-1/2 flex flex-col justify-center">
                    <div class="text-2xl text-text space-y-4">
                        {''.join([f'<p class="border-l-4 border-l-primary pl-4">{point}</p>' for point in content.main_points[:3]])}
                    </div>
                </div>
                <div class="w-1/2 flex flex-col justify-center gap-6">
                    {self._render_data_items(content.data_items) if content.data_items else f'<p class="text-xl text-secondary">{content.detail_text or ""}</p>'}
                </div>
            </div>
        </div>
        """
        return html

    def _render_grid_cards(
        self,
        design: SlideDesign,
        content: SlideContent
    ) -> str:
        """TODO: Add docstring."""
        cards_html = []

        # main_points
        for i, point in enumerate(content.main_points[:4], 1):
            cards_html.append(f"""
                <div class="card animate-slideUp" style="animation-delay: {i*0.1}s;">
                    <div class="text-5xl font-bold text-primary mb-4">{i:02d}</div>
                    <p class="text-xl text-text">{point}</p>
                </div>
            """)

        html = f"""
        <div class="flex flex-col h-full w-full p-12">
            {f'<h2 class="text-5xl font-bold text-primary mb-12">{content.title}</h2>' if content.title else ''}
            <div class="grid grid-cols-2 gap-8 flex-1">
                {''.join(cards_html)}
            </div>
        </div>
        """
        return html

    def _render_big_numbers(
        self,
        design: SlideDesign,
        content: SlideContent
    ) -> str:
        """ - """
        if not content.data_items:
            # bullets
            return self._render_bullets(design, content)

        numbers_html = []
        for item in content.data_items[:4]:
            numbers_html.append(f"""
                <div class="flex flex-col items-center animate-fadeIn">
                    <div class="text-8xl font-black text-primary mb-4">{item.get('value', '')}</div>
                    <div class="text-2xl text-secondary">{item.get('label', '')}</div>
                </div>
            """)

        html = f"""
        <div class="flex flex-col h-full w-full p-12">
            {f'<h2 class="text-5xl font-bold text-text mb-12">{content.title}</h2>' if content.title else ''}
            <div class="grid grid-cols-2 gap-16 flex-1 items-center">
                {''.join(numbers_html)}
            </div>
        </div>
        """
        return html

    def _render_top_bottom(
        self,
        design: SlideDesign,
        content: SlideContent
    ) -> str:
        """TODO: Add docstring."""
        html = f"""
        <div class="flex flex-col h-full w-full p-12 animate-slideUp">
            <div class="flex-1 flex flex-col justify-center">
                {f'<h2 class="text-6xl font-bold text-primary mb-8">{content.title}</h2>' if content.title else ''}
                <p class="text-3xl text-text leading-relaxed">{content.detail_text or ''}</p>
            </div>
            <div class="divider"></div>
            <div class="flex-1 flex items-center">
                <div class="grid grid-cols-3 gap-8 w-full">
                    {''.join([f'<div class="card text-center"><p class="text-xl text-text">{point}</p></div>' for point in content.main_points[:3]])}
                </div>
            </div>
        </div>
        """
        return html

    def _render_bullets(
        self,
        design: SlideDesign,
        content: SlideContent
    ) -> str:
        """ - visual_style"""

        # 
        if content.chart:
            bullets_html = ''.join([f'<div class="flex items-start gap-4 mb-6"><div class="text-3xl text-primary"></div><p class="text-xl text-text flex-1">{p}</p></div>' for p in content.main_points])
            # slide_number
            import random
            chart_html = self._render_chart(content.chart, random.randint(1, 100))

            html = f"""
            <div class="flex flex-col h-full w-full p-12">
                {f'<h2 class="text-5xl font-bold text-primary mb-12">{content.title}</h2>' if content.title else ''}
                <div class="flex flex-row gap-12 flex-1">
                    <div class="w-1/3 flex flex-col justify-center">
                        {bullets_html}
                    </div>
                    <div class="w-2/3 flex items-center justify-center">
                        {chart_html}
                    </div>
                </div>
                {f'<p class="text-sm text-secondary mt-4">{content.detail_text}</p>' if content.detail_text else ''}
            </div>
            """
            return html

        # visual_style
        if '' in design.visual_style or 'card' in design.visual_style.lower():
            # 
            bullets_html = []
            for i, point in enumerate(content.main_points[:4], 1):
                bullets_html.append(f"""
                    <div class="card animate-slideUp p-8" style="animation-delay: {i*0.1}s;">
                        <div class="text-3xl font-bold text-primary mb-4">{i:02d}</div>
                        <p class="text-xl text-text leading-relaxed">{point}</p>
                    </div>
                """)

            html = f"""
            <div class="flex flex-col h-full w-full p-12">
                {f'<h2 class="text-5xl font-bold text-primary mb-12">{content.title}</h2>' if content.title else ''}
                <div class="grid grid-cols-2 gap-8 flex-1">
                    {''.join(bullets_html)}
                </div>
                {f'<p class="text-lg text-secondary mt-8">{content.detail_text}</p>' if content.detail_text else ''}
            </div>
            """
        elif '' in design.visual_style or '' in design.visual_style:
            # 
            half = len(content.main_points) // 2
            left_points = content.main_points[:half]
            right_points = content.main_points[half:]

            left_html = ''.join([f'<div class="flex items-start gap-4 mb-6"><div class="text-3xl text-primary"></div><p class="text-xl text-text flex-1">{p}</p></div>' for p in left_points])
            right_html = ''.join([f'<div class="flex items-start gap-4 mb-6"><div class="text-3xl text-primary"></div><p class="text-xl text-text flex-1">{p}</p></div>' for p in right_points])

            html = f"""
            <div class="flex flex-col h-full w-full p-12">
                {f'<h2 class="text-5xl font-bold text-primary mb-12">{content.title}</h2>' if content.title else ''}
                <div class="flex flex-row gap-16 flex-1">
                    <div class="w-1/2">{left_html}</div>
                    <div class="w-1/2">{right_html}</div>
                </div>
                {f'<p class="text-lg text-secondary mt-8 border-l-4 border-l-primary pl-6">{content.detail_text}</p>' if content.detail_text else ''}
            </div>
            """
        else:
            # 
            bullets_html = []
            for i, point in enumerate(content.main_points, 1):
                bullets_html.append(f"""
                    <div class="flex items-start gap-6 animate-slideUp mb-6" style="animation-delay: {i*0.1}s;">
                        <div class="text-4xl font-bold text-primary">{i:02d}</div>
                        <p class="text-2xl text-text flex-1 leading-relaxed">{point}</p>
                    </div>
                """)

            html = f"""
            <div class="flex flex-col h-full w-full p-12">
                {f'<h2 class="text-5xl font-bold text-primary mb-12">{content.title}</h2>' if content.title else ''}
                <div class="flex flex-col flex-1 justify-center">
                    {''.join(bullets_html)}
                </div>
                {f'<div class="mt-8 p-6 bg-gray-50 rounded-xl"><p class="text-lg text-text leading-relaxed">{content.detail_text}</p></div>' if content.detail_text else ''}
            </div>
            """
        return html

    def _render_custom(
        self,
        design: SlideDesign,
        content: SlideContent
    ) -> str:
        """ - visual_style"""
        # 
        if '' in design.visual_style or '' in design.visual_style:
            return self._render_center_text(design, content)
        elif '' in design.visual_style or '' in design.visual_style:
            return self._render_grid_cards(design, content)
        elif '' in design.visual_style or '' in design.visual_style:
            return self._render_left_right_split(design, content)
        else:
            return self._render_bullets(design, content)

    def _render_data_items(self, data_items: List[Dict[str, str]]) -> str:
        """TODO: Add docstring."""
        items_html = []
        for item in data_items[:4]:
            items_html.append(f"""
                <div class="card">
                    <div class="text-4xl font-bold text-primary mb-2">{item.get('value', '')}</div>
                    <div class="text-lg text-secondary">{item.get('label', '')}</div>
                </div>
            """)
        return ''.join(items_html)

    def _render_chart(self, chart_config: Dict[str, Any], slide_number: int) -> str:
        """TODO: Add docstring."""
        import json
        import random

        chart_id = f"chart_{slide_number}_{random.randint(1000, 9999)}"
        chart_type = chart_config.get('type', 'bar')
        chart_data = chart_config.get('data', {})
        chart_title = chart_config.get('title', '')

        # Chart.js
        chart_config_json = {
            'type': chart_type,
            'data': chart_data,
            'options': {
                'responsive': True,
                'maintainAspectRatio': True,
                'plugins': {
                    'legend': {
                        'display': True,
                        'position': 'top'
                    },
                    'title': {
                        'display': bool(chart_title),
                        'text': chart_title,
                        'font': {
                            'size': 18
                        }
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                } if chart_type in ['bar', 'line'] else {}
            }
        }

        chart_html = f"""
        <div class="chart-container" style="position: relative; height: 400px; width: 100%;">
            <canvas id="{chart_id}"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx, {json.dumps(chart_config_json)});
            }})();
        </script>
        """
        return chart_html
