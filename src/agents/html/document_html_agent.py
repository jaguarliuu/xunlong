"""
DocumentHTMLAgent - HTML

HTML
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import re
import logging
from .base_html_agent import BaseHTMLAgent

logger = logging.getLogger(__name__)


class DocumentHTMLAgent(BaseHTMLAgent):
    """HTML"""

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        default_template: str = "academic",
        default_theme: str = "light"
    ):
        """
        HTML

        Args:
            template_dir: 
            default_template:  (academic, technical, simple)
            default_theme: 
        """
        super().__init__(template_dir, default_template, default_theme)

    def _get_default_template_dir(self) -> Path:
        """"""
        return Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'document'

    def get_template_name(self, template: Optional[str] = None) -> str:
        """"""
        template = template or self.default_template
        return f"{template}.html"

    def parse_content(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        

        Args:
            content: Markdown
            metadata: 

        Returns:
            
        """
        metadata = metadata or {}

        # 
        title = metadata.get('title') or self._extract_title(content)

        #  - metadatasectionsvisualizations
        sections = []
        if 'sections' in metadata and metadata['sections']:
            for section in metadata['sections']:
                sections.append({
                    'level': section.get('level', 2),
                    'title': section.get('title', ''),
                    'id': section.get('id') or self._generate_section_id(section.get('title', '')),
                    'content': section.get('content', ''),
                    'content_html': section.get('content_html', ''),
                    'visualizations': section.get('visualizations', [])
                })
        else:
            sections = self._extract_sections(content)

        # 
        abstract = metadata.get('abstract') or self._extract_abstract(content, sections)

        # 
        toc = self._generate_toc(sections)

        # 
        keywords = metadata.get('keywords', [])

        #  - metadata
        if 'stats' in metadata:
            stats = metadata['stats']
        else:
            aggregate_content = '\n\n'.join(section.get('content', '') for section in sections) if sections else content
            stats = self._calculate_stats(aggregate_content)

        return {
            'title': title,
            'author': metadata.get('author', ''),
            'date': metadata.get('date', ''),
            'abstract': abstract,
            'keywords': keywords,
            'sections': sections,
            'toc': toc,
            'stats': stats,
            'metadata': metadata
        }

    def _extract_title(self, content: str) -> str:
        """"""
        #  # 
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled Document"

    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """"""
        sections = []

        # 
        lines = content.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            # 
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                # 
                if current_section:
                    current_section['content'] = '\n'.join(current_content).strip()
                    sections.append(current_section)

                # 
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()

                current_section = {
                    'level': level,
                    'title': title,
                    'id': self._generate_section_id(title),
                    'content': ''
                }
                current_content = []
            else:
                # 
                if current_section:
                    current_content.append(line)

        # 
        if current_section:
            current_section['content'] = '\n'.join(current_content).strip()
            sections.append(current_section)

        return sections

    def _extract_abstract(self, content: str, sections: List[Dict]) -> str:
        """"""
        # """Abstract"
        for section in sections:
            if section['title'].lower() in ['', 'abstract', 'summary', '']:
                return section['content']

        # 
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            # 
            if not para.strip().startswith('#') and len(para.strip()) > 50:
                return para.strip()[:300] + '...'

        return ""

    def _generate_toc(self, sections: List[Dict]) -> List[Dict]:
        """"""
        toc = []
        for section in sections:
            toc.append({
                'level': section['level'],
                'title': section['title'],
                'id': section['id'],
                'indent': (section['level'] - 1) * 20  # 
            })
        return toc

    def _generate_section_id(self, title: str) -> str:
        """ID"""
        # URLID
        section_id = re.sub(r'[^\w\s-]', '', title.lower())
        section_id = re.sub(r'[\s_-]+', '-', section_id)
        return section_id

    def _calculate_stats(self, content: str) -> Dict[str, int]:
        """"""
        # 
        words = len(re.findall(r'\w+', content))

        # 
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))

        # 
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])

        # 
        images = len(re.findall(r'!\[.*?\]\(.*?\)', content))

        # 
        code_blocks = len(re.findall(r'```', content)) // 2

        return {
            'words': words,
            'chinese_chars': chinese_chars,
            'paragraphs': paragraphs,
            'images': images,
            'code_blocks': code_blocks
        }

    def add_citation(
        self,
        content: str,
        citations: List[Dict[str, str]]
    ) -> str:
        """
        

        Args:
            content: 
            citations:  {title, author, year, url}

        Returns:
            
        """
        if not citations:
            return content

        citation_section = "\n\n## \n\n"
        for i, citation in enumerate(citations, 1):
            citation_section += f"{i}. {citation.get('author', 'Unknown')}. "
            citation_section += f"*{citation.get('title', 'Untitled')}*. "
            citation_section += f"{citation.get('year', 'n.d.')}. "
            if citation.get('url'):
                citation_section += f"[]({citation['url']})"
            citation_section += "\n"

        return content + citation_section

    def add_appendix(
        self,
        content: str,
        appendices: List[Dict[str, str]]
    ) -> str:
        """
        

        Args:
            content: 
            appendices:  {title, content}

        Returns:
            
        """
        if not appendices:
            return content

        appendix_section = "\n\n## \n\n"
        for i, appendix in enumerate(appendices, 1):
            appendix_section += f"###  {i}: {appendix.get('title', 'Untitled')}\n\n"
            appendix_section += appendix.get('content', '') + "\n\n"

        return content + appendix_section
