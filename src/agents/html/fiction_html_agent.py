"""
FictionHTMLAgent - 小说HTML转换智能体

用于将小说内容转换为适合阅读的HTML格式
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import re
import logging
from .base_html_agent import BaseHTMLAgent

logger = logging.getLogger(__name__)


class FictionHTMLAgent(BaseHTMLAgent):
    """小说HTML转换智能体"""

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        default_template: str = "novel",
        default_theme: str = "sepia"
    ):
        """
        初始化小说HTML转换智能体

        Args:
            template_dir: 模板目录
            default_template: 默认模板 (novel, ebook, magazine)
            default_theme: 默认主题 (light, dark, sepia)
        """
        super().__init__(template_dir, default_template, default_theme)

    def _get_default_template_dir(self) -> Path:
        """获取默认模板目录"""
        return Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'fiction'

    def get_template_name(self, template: Optional[str] = None) -> str:
        """获取模板文件名"""
        template = template or self.default_template
        return f"{template}.html"

    def parse_content(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        解析小说内容

        Args:
            content: 小说文本内容
            metadata: 元数据（标题、作者、简介等）

        Returns:
            结构化的小说数据
        """
        metadata = metadata or {}

        # 提取基本信息
        title = metadata.get('title') or self._extract_title(content)
        author = metadata.get('author', '佚名')
        genre = metadata.get('genre', '小说')

        # 提取章节
        chapters = self._extract_chapters(content)

        # 提取人物
        characters = metadata.get('characters', [])

        # 生成简介（如果没有提供）
        synopsis = metadata.get('synopsis') or self._generate_synopsis(content, chapters)

        # 统计信息
        stats = self._calculate_fiction_stats(content, chapters)

        return {
            'title': title,
            'author': author,
            'genre': genre,
            'synopsis': synopsis,
            'characters': characters,
            'chapters': chapters,
            'stats': stats,
            'metadata': metadata
        }

    def _extract_title(self, content: str) -> str:
        """从内容中提取标题"""
        # 查找第一个 # 标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "未命名小说"

    def _extract_chapters(self, content: str) -> List[Dict[str, Any]]:
        """提取章节"""
        chapters = []

        # 多种章节标题模式
        patterns = [
            r'^##\s+第([0-9一二三四五六七八九十百千零]+)[章回节]\s*[：:、]?\s*(.*)$',  # ## 第X章：标题
            r'^##\s+Chapter\s+(\d+)[：:、]?\s*(.*)$',  # ## Chapter X: Title
            r'^##\s+([0-9]+)[\.、]\s*(.*)$',  # ## 1. 标题
            r'^##\s+(.+)$',  # ## 任意标题
        ]

        lines = content.split('\n')
        current_chapter = None
        current_content = []
        chapter_number = 0

        for line in lines:
            is_chapter = False

            # 尝试匹配章节标题
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    # 保存之前的章节
                    if current_chapter:
                        current_chapter['content'] = '\n'.join(current_content).strip()
                        chapters.append(current_chapter)

                    # 创建新章节
                    chapter_number += 1
                    if len(match.groups()) >= 2:
                        chapter_id = match.group(1)
                        chapter_title = match.group(2).strip()
                    else:
                        chapter_id = str(chapter_number)
                        chapter_title = match.group(1).strip()

                    current_chapter = {
                        'number': chapter_number,
                        'id': chapter_id,
                        'title': chapter_title,
                        'content': ''
                    }
                    current_content = []
                    is_chapter = True
                    break

            if not is_chapter and current_chapter:
                current_content.append(line)

        # 保存最后一个章节
        if current_chapter:
            current_chapter['content'] = '\n'.join(current_content).strip()
            chapters.append(current_chapter)

        # 如果没有找到章节，将整个内容作为一章
        if not chapters:
            chapters = [{
                'number': 1,
                'id': '1',
                'title': '正文',
                'content': content
            }]

        return chapters

    def _generate_synopsis(self, content: str, chapters: List[Dict]) -> str:
        """生成小说简介"""
        # 如果第一章标题包含"简介"、"内容简介"等，使用第一章内容
        if chapters and any(keyword in chapters[0]['title'] for keyword in ['简介', '内容简介', 'Synopsis']):
            return chapters[0]['content'][:500]

        # 否则取前几段
        paragraphs = []
        for line in content.split('\n\n'):
            line = line.strip()
            # 跳过标题和空行
            if line and not line.startswith('#'):
                paragraphs.append(line)
                if len(paragraphs) >= 3:
                    break

        synopsis = '\n\n'.join(paragraphs)
        return synopsis[:500] + ('...' if len(synopsis) > 500 else '')

    def _calculate_fiction_stats(self, content: str, chapters: List[Dict]) -> Dict[str, int]:
        """计算小说统计信息"""
        # 总字数（中文字符）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))

        # 总字数（所有字符）
        all_chars = len(content.replace('\n', '').replace(' ', ''))

        # 章节数
        chapter_count = len(chapters)

        # 平均每章字数
        avg_chars_per_chapter = chinese_chars // chapter_count if chapter_count > 0 else 0

        # 段落数
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])

        return {
            'total_chars': all_chars,
            'chinese_chars': chinese_chars,
            'chapter_count': chapter_count,
            'avg_chars_per_chapter': avg_chars_per_chapter,
            'paragraphs': paragraphs
        }

    def add_book_cover(
        self,
        metadata: Dict,
        cover_url: str
    ) -> Dict:
        """
        添加封面图片

        Args:
            metadata: 元数据
            cover_url: 封面图片URL

        Returns:
            更新后的元数据
        """
        metadata['cover'] = cover_url
        return metadata

    def add_character_profiles(
        self,
        characters: List[str]
    ) -> List[Dict[str, str]]:
        """
        创建人物简介结构

        Args:
            characters: 人物名称列表

        Returns:
            人物简介列表
        """
        return [
            {
                'name': char,
                'description': '',
                'role': ''
            }
            for char in characters
        ]

    def split_into_pages(
        self,
        content: str,
        chars_per_page: int = 1000
    ) -> List[str]:
        """
        将内容分页

        Args:
            content: 内容文本
            chars_per_page: 每页字符数

        Returns:
            分页后的内容列表
        """
        pages = []
        current_page = []
        current_length = 0

        for paragraph in content.split('\n\n'):
            paragraph = paragraph.strip()
            para_length = len(paragraph)

            if current_length + para_length > chars_per_page and current_page:
                # 保存当前页
                pages.append('\n\n'.join(current_page))
                current_page = [paragraph]
                current_length = para_length
            else:
                current_page.append(paragraph)
                current_length += para_length

        # 保存最后一页
        if current_page:
            pages.append('\n\n'.join(current_page))

        return pages
