"""
DocumentHTMLAgent - 文档HTML转换智能体

用于将研究报告、分析文档等转换为美观的HTML格式
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import re
import logging
from .base_html_agent import BaseHTMLAgent

logger = logging.getLogger(__name__)


class DocumentHTMLAgent(BaseHTMLAgent):
    """文档HTML转换智能体"""

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        default_template: str = "academic",
        default_theme: str = "light"
    ):
        """
        初始化文档HTML转换智能体

        Args:
            template_dir: 模板目录
            default_template: 默认模板 (academic, technical, simple)
            default_theme: 默认主题
        """
        super().__init__(template_dir, default_template, default_theme)

    def _get_default_template_dir(self) -> Path:
        """获取默认模板目录"""
        return Path(__file__).parent.parent.parent.parent / 'templates' / 'html' / 'document'

    def get_template_name(self, template: Optional[str] = None) -> str:
        """获取模板文件名"""
        template = template or self.default_template
        return f"{template}.html"

    def parse_content(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        解析文档内容

        Args:
            content: Markdown格式的文档内容
            metadata: 元数据（标题、作者等）

        Returns:
            结构化的文档数据
        """
        metadata = metadata or {}

        # 提取标题
        title = metadata.get('title') or self._extract_title(content)

        # 提取章节 - 如果metadata已提供sections（带visualizations），直接使用
        if 'sections' in metadata and metadata['sections']:
            sections = metadata['sections']
        else:
            sections = self._extract_sections(content)

        # 提取摘要
        abstract = metadata.get('abstract') or self._extract_abstract(content, sections)

        # 提取目录
        toc = self._generate_toc(sections)

        # 提取关键词
        keywords = metadata.get('keywords', [])

        # 统计信息 - 如果metadata已提供，优先使用
        if 'stats' in metadata:
            stats = metadata['stats']
        else:
            stats = self._calculate_stats(content)

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
        """从内容中提取标题"""
        # 查找第一个 # 标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled Document"

    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """提取文档章节"""
        sections = []

        # 按标题分割内容
        lines = content.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            # 检测标题
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                # 保存之前的章节
                if current_section:
                    current_section['content'] = '\n'.join(current_content).strip()
                    sections.append(current_section)

                # 创建新章节
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
                # 添加内容到当前章节
                if current_section:
                    current_content.append(line)

        # 保存最后一个章节
        if current_section:
            current_section['content'] = '\n'.join(current_content).strip()
            sections.append(current_section)

        return sections

    def _extract_abstract(self, content: str, sections: List[Dict]) -> str:
        """提取摘要"""
        # 查找名为"摘要"、"Abstract"的章节
        for section in sections:
            if section['title'].lower() in ['摘要', 'abstract', 'summary', '概要']:
                return section['content']

        # 如果没有摘要章节，返回第一段
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            # 跳过标题行
            if not para.strip().startswith('#') and len(para.strip()) > 50:
                return para.strip()[:300] + '...'

        return ""

    def _generate_toc(self, sections: List[Dict]) -> List[Dict]:
        """生成目录"""
        toc = []
        for section in sections:
            toc.append({
                'level': section['level'],
                'title': section['title'],
                'id': section['id'],
                'indent': (section['level'] - 1) * 20  # 缩进像素
            })
        return toc

    def _generate_section_id(self, title: str) -> str:
        """生成章节ID"""
        # 转换为URL友好的ID
        section_id = re.sub(r'[^\w\s-]', '', title.lower())
        section_id = re.sub(r'[\s_-]+', '-', section_id)
        return section_id

    def _calculate_stats(self, content: str) -> Dict[str, int]:
        """计算文档统计信息"""
        # 字数统计
        words = len(re.findall(r'\w+', content))

        # 中文字符统计
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))

        # 段落数
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])

        # 图片数
        images = len(re.findall(r'!\[.*?\]\(.*?\)', content))

        # 代码块数
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
        添加引用

        Args:
            content: 文档内容
            citations: 引用列表，每项包含 {title, author, year, url}

        Returns:
            添加了引用的内容
        """
        if not citations:
            return content

        citation_section = "\n\n## 参考文献\n\n"
        for i, citation in enumerate(citations, 1):
            citation_section += f"{i}. {citation.get('author', 'Unknown')}. "
            citation_section += f"*{citation.get('title', 'Untitled')}*. "
            citation_section += f"{citation.get('year', 'n.d.')}. "
            if citation.get('url'):
                citation_section += f"[链接]({citation['url']})"
            citation_section += "\n"

        return content + citation_section

    def add_appendix(
        self,
        content: str,
        appendices: List[Dict[str, str]]
    ) -> str:
        """
        添加附录

        Args:
            content: 文档内容
            appendices: 附录列表，每项包含 {title, content}

        Returns:
            添加了附录的内容
        """
        if not appendices:
            return content

        appendix_section = "\n\n## 附录\n\n"
        for i, appendix in enumerate(appendices, 1):
            appendix_section += f"### 附录 {i}: {appendix.get('title', 'Untitled')}\n\n"
            appendix_section += appendix.get('content', '') + "\n\n"

        return content + appendix_section
