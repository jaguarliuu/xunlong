"""
FictionHTMLAgent - HTML

HTML
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import re
import logging
from .base_html_agent import BaseHTMLAgent

logger = logging.getLogger(__name__)


class FictionHTMLAgent(BaseHTMLAgent):
    """HTML"""

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        default_template: str = "novel",
        default_theme: str = "sepia"
    ):
        """
        HTML

        Args:
            template_dir: 
            default_template:  (novel, ebook, magazine)
            default_theme:  (light, dark, sepia)
        """
        super().__init__(template_dir, default_template, default_theme)

    def _get_default_template_dir(self) -> Path:
        """TODO: Add docstring."""
        return Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'fiction'

    def get_template_name(self, template: Optional[str] = None) -> str:
        """TODO: Add docstring."""
        template = template or self.default_template
        return f"{template}.html"

    def parse_content(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        

        Args:
            content: 
            metadata: 

        Returns:
            
        """
        metadata = metadata or {}

        # 
        title = metadata.get('title') or self._extract_title(content)
        author = metadata.get('author', '')
        genre = metadata.get('genre', '')

        # 
        chapters = self._extract_chapters(content)

        # 
        characters = metadata.get('characters', [])

        # 
        synopsis = metadata.get('synopsis') or self._generate_synopsis(content, chapters)

        # 
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
        """TODO: Add docstring."""
        #  # 
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_chapters(self, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        chapters = []

        # 
        patterns = [
            r'^##\s+([0-9]+)[]\s*[:]?\s*(.*)$',  # ## X
            r'^##\s+Chapter\s+(\d+)[:]?\s*(.*)$',  # ## Chapter X: Title
            r'^##\s+([0-9]+)[\.]\s*(.*)$',  # ## 1. 
            r'^##\s+(.+)$',  # ## 
        ]

        lines = content.split('\n')
        current_chapter = None
        current_content = []
        chapter_number = 0

        for line in lines:
            is_chapter = False

            # 
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    # 
                    if current_chapter:
                        current_chapter['content'] = '\n'.join(current_content).strip()
                        chapters.append(current_chapter)

                    # 
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

        # 
        if current_chapter:
            current_chapter['content'] = '\n'.join(current_content).strip()
            chapters.append(current_chapter)

        # 
        if not chapters:
            chapters = [{
                'number': 1,
                'id': '1',
                'title': '',
                'content': content
            }]

        return chapters

    def _generate_synopsis(self, content: str, chapters: List[Dict]) -> str:
        """TODO: Add docstring."""
        # Extract synopsis from first chapter if it exists
        if chapters and any(keyword in chapters[0]['title'] for keyword in ['', '', 'Synopsis']):
            return chapters[0]['content'][:500]

        # 
        paragraphs = []
        for line in content.split('\n\n'):
            line = line.strip()
            # 
            if line and not line.startswith('#'):
                paragraphs.append(line)
                if len(paragraphs) >= 3:
                    break

        synopsis = '\n\n'.join(paragraphs)
        return synopsis[:500] + ('...' if len(synopsis) > 500 else '')

    def _calculate_fiction_stats(self, content: str, chapters: List[Dict]) -> Dict[str, int]:
        """TODO: Add docstring."""
        # 
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))

        # 
        all_chars = len(content.replace('\n', '').replace(' ', ''))

        # 
        chapter_count = len(chapters)

        # 
        avg_chars_per_chapter = chinese_chars // chapter_count if chapter_count > 0 else 0

        # 
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
        

        Args:
            metadata: 
            cover_url: URL

        Returns:
            
        """
        metadata['cover'] = cover_url
        return metadata

    def add_character_profiles(
        self,
        characters: List[str]
    ) -> List[Dict[str, str]]:
        """
        

        Args:
            characters: 

        Returns:
            
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
        

        Args:
            content: 
            chars_per_page: 

        Returns:
            
        """
        pages = []
        current_page = []
        current_length = 0

        for paragraph in content.split('\n\n'):
            paragraph = paragraph.strip()
            para_length = len(paragraph)

            if current_length + para_length > chars_per_page and current_page:
                # 
                pages.append('\n\n'.join(current_page))
                current_page = [paragraph]
                current_length = para_length
            else:
                current_page.append(paragraph)
                current_length += para_length

        # 
        if current_page:
            pages.append('\n\n'.join(current_page))

        return pages
