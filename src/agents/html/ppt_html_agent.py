"""
PPTHTMLAgent - PPT HTML转换智能体

用于将内容转换为HTML演示文稿（PPT）格式
支持多种模板和主题，以及AI辅助的智能分页和布局优化
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import re
import logging
from .base_html_agent import BaseHTMLAgent

logger = logging.getLogger(__name__)


class PPTHTMLAgent(BaseHTMLAgent):
    """PPT HTML转换智能体"""

    # 支持的PPT框架
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
        初始化PPT HTML转换智能体

        Args:
            template_dir: 模板目录
            default_template: 默认模板
            default_theme: 默认主题
            framework: PPT框架 (reveal, impress, remark, custom)
        """
        self.framework = framework
        super().__init__(template_dir, default_template, default_theme)

    def _get_default_template_dir(self) -> Path:
        """获取默认模板目录"""
        return Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'ppt'

    def get_template_name(self, template: Optional[str] = None) -> str:
        """获取模板文件名"""
        template = template or self.default_template
        return f"{self.framework}_{template}.html"

    def parse_content(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        解析PPT内容

        Args:
            content: 原始内容
            metadata: 元数据

        Returns:
            结构化的PPT数据
        """
        metadata = metadata or {}

        # 提取基本信息
        title = metadata.get('title') or self._extract_title(content)
        author = metadata.get('author', '')
        date = metadata.get('date', '')

        # 提取幻灯片
        slides = self._extract_slides(content)

        # 如果没有幻灯片，尝试智能分页
        if not slides or len(slides) == 1:
            slides = self._smart_split_slides(content, metadata)

        # 为每个幻灯片确定布局
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
        """从内容中提取标题"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled Presentation"

    def _extract_slides(self, content: str) -> List[Dict[str, Any]]:
        """
        提取幻灯片

        幻灯片分隔符：
        - "---" 水平分隔符（新幻灯片）
        - "##" 二级标题（新幻灯片）
        """
        slides = []

        # 方法1：使用 --- 分隔
        if '---' in content:
            slide_contents = content.split('---')
            for i, slide_content in enumerate(slide_contents):
                if slide_content.strip():
                    slides.append(self._parse_slide(slide_content.strip(), i + 1))
            return slides

        # 方法2：使用 ## 二级标题分隔
        lines = content.split('\n')
        current_slide = []
        slide_number = 0

        for line in lines:
            # 检测二级标题
            if re.match(r'^##\s+', line):
                # 保存之前的幻灯片
                if current_slide:
                    slide_number += 1
                    slides.append(self._parse_slide('\n'.join(current_slide), slide_number))
                    current_slide = []

            current_slide.append(line)

        # 保存最后一个幻灯片
        if current_slide:
            slide_number += 1
            slides.append(self._parse_slide('\n'.join(current_slide), slide_number))

        return slides

    def _parse_slide(self, content: str, slide_number: int) -> Dict[str, Any]:
        """解析单个幻灯片"""
        # 提取标题
        title_match = re.search(r'^##?\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ''

        # 移除标题后的内容
        if title_match:
            content = content[title_match.end():].strip()

        # 检测内容类型
        slide_type = self._detect_slide_type(content)

        # 提取列表项
        bullet_points = self._extract_bullet_points(content)

        # 检测图片
        images = self._extract_images(content)

        # 检测代码块
        code_blocks = self._extract_code_blocks(content)

        return {
            'number': slide_number,
            'title': title,
            'content': content,
            'type': slide_type,
            'bullet_points': bullet_points,
            'images': images,
            'code_blocks': code_blocks,
            'layout': 'default'  # 稍后会更新
        }

    def _detect_slide_type(self, content: str) -> str:
        """检测幻灯片类型"""
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
        """提取列表项"""
        bullets = []
        for line in content.split('\n'):
            match = re.match(r'^[-*+]\s+(.+)$', line.strip())
            if match:
                bullets.append(match.group(1))
        return bullets

    def _extract_images(self, content: str) -> List[Dict[str, str]]:
        """提取图片"""
        images = []
        for match in re.finditer(r'!\[(.*?)\]\((.*?)\)', content):
            images.append({
                'alt': match.group(1),
                'src': match.group(2)
            })
        return images

    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """提取代码块"""
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
        智能分页：使用AI辅助将长内容分成合适的幻灯片

        Args:
            content: 内容
            metadata: 元数据

        Returns:
            幻灯片列表
        """
        # 简单实现：按段落和长度分割
        # TODO: 可以集成LLM进行智能分页

        slides = []
        slide_number = 0

        # 首页（标题页）
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

        # 移除标题
        content = re.sub(r'^#\s+.+$', '', content, count=1, flags=re.MULTILINE).strip()

        # 按二级标题分组
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
        为幻灯片分配布局

        布局类型：
        - title: 标题页
        - section: 章节页
        - bullets: 列表页
        - image: 图片页
        - code: 代码页
        - two_column: 两栏布局
        - default: 默认布局
        """
        for i, slide in enumerate(slides):
            # 第一页通常是标题页
            if i == 0:
                slide['layout'] = 'title'
            # 有图片的幻灯片
            elif slide['images']:
                if slide['bullet_points']:
                    slide['layout'] = 'two_column'  # 图文混排
                else:
                    slide['layout'] = 'image'
            # 有代码的幻灯片
            elif slide['code_blocks']:
                slide['layout'] = 'code'
            # 有列表的幻灯片
            elif slide['bullet_points']:
                slide['layout'] = 'bullets'
            # 纯文本但内容少
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
        添加转场效果

        Args:
            slides: 幻灯片列表
            transition: 转场效果 (slide, fade, zoom, cube, etc.)

        Returns:
            更新后的幻灯片列表
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
        添加背景

        Args:
            slides: 幻灯片列表
            background: 背景（颜色或图片URL）
            slide_numbers: 应用背景的幻灯片编号列表（None表示全部）

        Returns:
            更新后的幻灯片列表
        """
        for slide in slides:
            if slide_numbers is None or slide['number'] in slide_numbers:
                slide['background'] = background
        return slides

    def generate_outline_slide(self, slides: List[Dict]) -> Dict[str, Any]:
        """
        生成目录页

        Args:
            slides: 幻灯片列表

        Returns:
            目录幻灯片
        """
        outline_points = []
        for slide in slides:
            if slide.get('layout') not in ['title', 'section'] and slide.get('title'):
                outline_points.append(slide['title'])

        return {
            'number': 2,  # 通常插入第二页
            'title': '目录',
            'content': '',
            'type': 'bullets',
            'bullet_points': outline_points,
            'images': [],
            'code_blocks': [],
            'layout': 'bullets'
        }

    def optimize_for_framework(self, slides: List[Dict]) -> List[Dict]:
        """
        根据不同框架优化幻灯片

        Args:
            slides: 幻灯片列表

        Returns:
            优化后的幻灯片列表
        """
        if self.framework == 'reveal':
            # Reveal.js 特定优化
            for slide in slides:
                slide['data_attrs'] = {
                    'data-transition': slide.get('transition', 'slide'),
                    'data-background': slide.get('background', '')
                }
        elif self.framework == 'impress':
            # Impress.js 特定优化（3D定位）
            for i, slide in enumerate(slides):
                slide['data_attrs'] = {
                    'data-x': i * 1000,
                    'data-y': 0,
                    'data-z': 0,
                    'data-rotate': 0
                }

        return slides
