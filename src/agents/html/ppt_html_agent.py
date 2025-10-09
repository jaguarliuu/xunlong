"""
PPTHTMLAgent - PPT HTML

HTMLPPT
AI
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import re
import logging
from .base_html_agent import BaseHTMLAgent

logger = logging.getLogger(__name__)


class PPTHTMLAgent(BaseHTMLAgent):
    """PPT HTML"""

    # PPT
    FRAMEWORKS = {
        'reveal': 'Reveal.js',
        'impress': 'Impress.js',
        'remark': 'Remark.js',
        'custom': 'Custom Framework'
    }

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        default_template: str = "reveal",
        default_theme: str = "default",
        framework: str = "reveal"
    ):
        """
        PPT HTML

        Args:
            template_dir: 
            default_template: 
            default_theme: 
            framework: PPT (reveal, impress, remark, custom)
        """
        self.framework = framework
        super().__init__(template_dir, default_template, default_theme)

    def _get_default_template_dir(self) -> Path:
        """"""
        return Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'ppt'

    def get_template_name(self, template: Optional[str] = None) -> str:
        """"""
        template = template or self.default_template
        return f"{self.framework}_{template}.html"

    def parse_content(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        PPT

        Args:
            content: 
            metadata: 

        Returns:
            PPT
        """
        metadata = metadata or {}

        # 
        title = metadata.get('title') or self._extract_title(content)
        author = metadata.get('author', '')
        date = metadata.get('date', '')

        # 
        slides = self._extract_slides(content)

        # 
        if not slides or len(slides) == 1:
            slides = self._smart_split_slides(content, metadata)

        # 
        slides = self._assign_layouts(slides, metadata)

        return {
            'title': title,
            'author': author,
            'date': date,
            'slides': slides,
            'framework': self.framework,
            'metadata': metadata
        }

    def _extract_title(self, content: str) -> str:
        """"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled Presentation"

    def _extract_slides(self, content: str) -> List[Dict[str, Any]]:
        """
        

        
        - "---" 
        - "##" 
        """
        slides = []

        # 1 --- 
        if '---' in content:
            slide_contents = content.split('---')
            for i, slide_content in enumerate(slide_contents):
                if slide_content.strip():
                    slides.append(self._parse_slide(slide_content.strip(), i + 1))
            return slides

        # 2 ## 
        lines = content.split('\n')
        current_slide = []
        slide_number = 0

        for line in lines:
            # 
            if re.match(r'^##\s+', line):
                # 
                if current_slide:
                    slide_number += 1
                    slides.append(self._parse_slide('\n'.join(current_slide), slide_number))
                    current_slide = []

            current_slide.append(line)

        # 
        if current_slide:
            slide_number += 1
            slides.append(self._parse_slide('\n'.join(current_slide), slide_number))

        return slides

    def _parse_slide(self, content: str, slide_number: int) -> Dict[str, Any]:
        """"""
        # 
        title_match = re.search(r'^##?\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ''

        # 
        if title_match:
            content = content[title_match.end():].strip()

        # 
        slide_type = self._detect_slide_type(content)

        # 
        bullet_points = self._extract_bullet_points(content)

        # 
        images = self._extract_images(content)

        # 
        code_blocks = self._extract_code_blocks(content)

        return {
            'number': slide_number,
            'title': title,
            'content': content,
            'type': slide_type,
            'bullet_points': bullet_points,
            'images': images,
            'code_blocks': code_blocks,
            'layout': 'default'  # 
        }

    def _detect_slide_type(self, content: str) -> str:
        """"""
        if re.search(r'!\[.*?\]\(.*?\)', content):
            return 'image'
        elif re.search(r'^[-*+]\s+', content, re.MULTILINE):
            return 'bullets'
        elif re.search(r'```', content):
            return 'code'
        elif len(content) < 100:
            return 'title'
        else:
            return 'content'

    def _extract_bullet_points(self, content: str) -> List[str]:
        """"""
        bullets = []
        for line in content.split('\n'):
            match = re.match(r'^[-*+]\s+(.+)$', line.strip())
            if match:
                bullets.append(match.group(1))
        return bullets

    def _extract_images(self, content: str) -> List[Dict[str, str]]:
        """"""
        images = []
        for match in re.finditer(r'!\[(.*?)\]\((.*?)\)', content):
            images.append({
                'alt': match.group(1),
                'src': match.group(2)
            })
        return images

    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """"""
        code_blocks = []
        for match in re.finditer(r'```(\w+)?\n(.*?)```', content, re.DOTALL):
            code_blocks.append({
                'language': match.group(1) or 'text',
                'code': match.group(2).strip()
            })
        return code_blocks

    def _smart_split_slides(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        AI

        Args:
            content: 
            metadata: 

        Returns:
            
        """
        # 
        # TODO: LLM

        slides = []
        slide_number = 0

        # 
        title = self._extract_title(content)
        slides.append({
            'number': 1,
            'title': title,
            'content': metadata.get('subtitle', ''),
            'type': 'title',
            'bullet_points': [],
            'images': [],
            'code_blocks': [],
            'layout': 'title'
        })
        slide_number = 1

        # 
        content = re.sub(r'^#\s+.+$', '', content, count=1, flags=re.MULTILINE).strip()

        # 
        sections = re.split(r'^##\s+(.+)$', content, flags=re.MULTILINE)

        current_content = sections[0] if sections else ''

        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_title = sections[i].strip()
                section_content = sections[i + 1].strip()

                slide_number += 1
                slides.append({
                    'number': slide_number,
                    'title': section_title,
                    'content': section_content,
                    'type': self._detect_slide_type(section_content),
                    'bullet_points': self._extract_bullet_points(section_content),
                    'images': self._extract_images(section_content),
                    'code_blocks': self._extract_code_blocks(section_content),
                    'layout': 'default'
                })

        return slides

    def _assign_layouts(
        self,
        slides: List[Dict[str, Any]],
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        

        
        - title: 
        - section: 
        - bullets: 
        - image: 
        - code: 
        - two_column: 
        - default: 
        """
        for i, slide in enumerate(slides):
            # 
            if i == 0:
                slide['layout'] = 'title'
            # 
            elif slide['images']:
                if slide['bullet_points']:
                    slide['layout'] = 'two_column'  # 
                else:
                    slide['layout'] = 'image'
            # 
            elif slide['code_blocks']:
                slide['layout'] = 'code'
            # 
            elif slide['bullet_points']:
                slide['layout'] = 'bullets'
            # 
            elif len(slide['content']) < 100:
                slide['layout'] = 'section'
            else:
                slide['layout'] = 'default'

        return slides

    def add_transition(
        self,
        slides: List[Dict],
        transition: str = "slide"
    ) -> List[Dict]:
        """
        

        Args:
            slides: 
            transition:  (slide, fade, zoom, cube, etc.)

        Returns:
            
        """
        for slide in slides:
            slide['transition'] = transition
        return slides

    def add_background(
        self,
        slides: List[Dict],
        background: str,
        slide_numbers: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        

        Args:
            slides: 
            background: URL
            slide_numbers: None

        Returns:
            
        """
        for slide in slides:
            if slide_numbers is None or slide['number'] in slide_numbers:
                slide['background'] = background
        return slides

    def generate_outline_slide(self, slides: List[Dict]) -> Dict[str, Any]:
        """
        

        Args:
            slides: 

        Returns:
            
        """
        outline_points = []
        for slide in slides:
            if slide.get('layout') not in ['title', 'section'] and slide.get('title'):
                outline_points.append(slide['title'])

        return {
            'number': 2,  # 
            'title': '',
            'content': '',
            'type': 'bullets',
            'bullet_points': outline_points,
            'images': [],
            'code_blocks': [],
            'layout': 'bullets'
        }

    def optimize_for_framework(self, slides: List[Dict]) -> List[Dict]:
        """
        

        Args:
            slides: 

        Returns:
            
        """
        if self.framework == 'reveal':
            # Reveal.js 
            for slide in slides:
                slide['data_attrs'] = {
                    'data-transition': slide.get('transition', 'slide'),
                    'data-background': slide.get('background', '')
                }
        elif self.framework == 'impress':
            # Impress.js 3D
            for i, slide in enumerate(slides):
                slide['data_attrs'] = {
                    'data-x': i * 1000,
                    'data-y': 0,
                    'data-z': 0,
                    'data-rotate': 0
                }

        return slides

    def convert_ppt_to_html(
        self,
        ppt_data: Dict[str, Any],
        style: str = "business",
        theme: str = "default"
    ) -> str:
        """
        PPTHTML

        Args:
            ppt_data: PPT
            style: PPT (red/business/academic/creative/simple)
            theme: 

        Returns:
            HTML
        """
        try:
            # flexible.htmlHTML
            template_name = "flexible.html"
            jinja_template = self.jinja_env.get_template(template_name)
            logger.info(f"flexible{style}PPT")

            # 
            render_data = {
                'title': ppt_data.get('title', 'PPT'),
                'subtitle': ppt_data.get('subtitle', ''),
                'colors': ppt_data.get('colors', {}),  # 
                'slides': ppt_data.get('slides', []),
                'metadata': ppt_data.get('metadata', {}),
                'theme': theme,
                'generated_at': ppt_data.get('metadata', {}).get('generated_at', ''),
                'generator': 'XunLong PPT Generator'
            }

            # HTML
            html = jinja_template.render(**render_data)
            return html

        except Exception as e:
            logger.error(f"PPTHTML: {e}")
            raise
