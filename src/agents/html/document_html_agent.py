"""
DocumentHTMLAgent - HTML

HTML
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import re
import logging
from .base_html_agent import BaseHTMLAgent
from .echarts_generator import EChartsGenerator

logger = logging.getLogger(__name__)


class DocumentHTMLAgent(BaseHTMLAgent):
    """HTML"""

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        default_template: str = "enhanced_professional",
        default_theme: str = "light"
    ):
        """
        HTML

        Args:
            template_dir:
            default_template:  (enhanced_professional, academic, technical, simple)
            default_theme:
        """
        super().__init__(template_dir, default_template, default_theme)
        self.chart_generator = EChartsGenerator()

    def _get_default_template_dir(self) -> Path:
        """Get default template directory - using built-in templates."""
        return Path(__file__).parent / 'templates'

    def get_template_name(self, template: Optional[str] = None) -> str:
        """TODO: Add docstring."""
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

        # Auto-detect and generate charts from data
        charts = []
        if metadata.get('enable_charts', True):
            charts = self.detect_and_visualize_data(sections)

        # Extract references from metadata
        references = metadata.get('references', [])

        # Generate project ID for AIGC metadata
        import uuid
        project_id = metadata.get('project_id', str(uuid.uuid4())[:8])

        # Generate full HTML content from sections
        content_html = self._generate_content_html(sections, charts)

        return {
            'title': title,
            'author': metadata.get('author', ''),
            'date': metadata.get('date', ''),
            'abstract': abstract,
            'keywords': keywords,
            'sections': sections,
            'toc': toc,
            'stats': stats,
            'charts': charts,
            'references': references,
            'project_id': project_id,
            'content': content_html,  # Add the HTML content string
            'metadata': metadata
        }

    def _extract_title(self, content: str) -> str:
        """TODO: Add docstring."""
        #  # 
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled Document"

    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
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
        """TODO: Add docstring."""
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

    def _generate_toc(self, sections: List[Dict]) -> str:
        """
        Generate HTML table of contents from sections.

        Args:
            sections: List of section dictionaries

        Returns:
            HTML string representing the TOC
        """
        if not sections:
            return ""

        toc_html = ['<ul>']
        current_level = 1

        for section in sections:
            level = section.get('level', 2)
            title = section.get('title', '')
            section_id = section.get('id', '')

            # Adjust nesting based on level changes
            if level > current_level:
                # Open nested lists for deeper levels
                for _ in range(level - current_level):
                    toc_html.append('<ul>')
            elif level < current_level:
                # Close nested lists for shallower levels
                for _ in range(current_level - level):
                    toc_html.append('</ul></li>')
            else:
                # Same level, close previous item
                if len(toc_html) > 1:  # Not the first item
                    toc_html.append('</li>')

            # Add the current item
            toc_html.append(f'<li><a href="#{section_id}">{title}</a>')
            current_level = level

        # Close all remaining open tags
        for _ in range(current_level - 1):
            toc_html.append('</li></ul>')
        toc_html.append('</li>')
        toc_html.append('</ul>')

        return '\n'.join(toc_html)

    def _generate_content_html(self, sections: List[Dict], charts: List[Dict]) -> str:
        """
        Generate complete HTML content from sections and charts.

        Args:
            sections: List of section dictionaries
            charts: List of chart configurations

        Returns:
            HTML string with all sections and chart placeholders
        """
        if not sections:
            return ""

        # Create a mapping of section index to charts
        chart_map = {}
        for chart in charts:
            chart_id = chart.get('id', '')
            # Extract section index from chart_id (format: chart_X_Y)
            if chart_id.startswith('chart_'):
                parts = chart_id.split('_')
                if len(parts) >= 2:
                    try:
                        section_idx = int(parts[1])
                        if section_idx not in chart_map:
                            chart_map[section_idx] = []
                        chart_map[section_idx].append(chart)
                    except (ValueError, IndexError):
                        pass

        content_parts = []

        for idx, section in enumerate(sections):
            level = section.get('level', 2)
            title = section.get('title', '')
            section_id = section.get('id', '')
            section_content = section.get('content_html') or section.get('content', '')

            # Add section heading with anchor
            heading_tag = f'h{level}'
            content_parts.append(f'<{heading_tag} id="{section_id}">{title}</{heading_tag}>')

            # Convert markdown to HTML if needed
            if section_content and not section.get('content_html'):
                try:
                    import markdown
                    section_content = markdown.markdown(
                        section_content,
                        extensions=['extra', 'codehilite', 'toc', 'tables']
                    )
                except ImportError:
                    # Fallback: wrap in paragraphs
                    section_content = '<p>' + section_content.replace('\n\n', '</p><p>').replace('\n', '<br>') + '</p>'

            content_parts.append(section_content)

            # Add chart placeholders for this section
            if idx in chart_map:
                for chart in chart_map[idx]:
                    chart_id = chart.get('id', '')
                    chart_title = chart.get('title', '')
                    content_parts.append(f'<div class="chart-wrapper" id="{chart_id}"></div>')
                    if chart_title:
                        content_parts.append(f'<p class="data-source">数据图表: {chart_title}</p>')

        return '\n\n'.join(content_parts)

    def _generate_section_id(self, title: str) -> str:
        """ID"""
        # URLID
        section_id = re.sub(r'[^\w\s-]', '', title.lower())
        section_id = re.sub(r'[\s_-]+', '-', section_id)
        return section_id

    def _calculate_stats(self, content: str) -> Dict[str, int]:
        """TODO: Add docstring."""
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

    def detect_and_visualize_data(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect data in sections and generate appropriate visualizations.

        Args:
            sections: List of section dictionaries

        Returns:
            List of chart configurations
        """
        self.chart_generator.clear()

        for i, section in enumerate(sections):
            content = section.get('content', '')

            # Detect tables that can be visualized
            tables = self._extract_tables(content)
            for j, table_data in enumerate(tables):
                chart_id = f"chart_{i}_{j}"
                self._create_chart_from_table(chart_id, section['title'], table_data)

        return self.chart_generator.get_all_charts()

    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract Markdown tables from content.

        Returns:
            List of table data dictionaries with headers and rows
        """
        tables = []
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Check if line is a table header (starts and ends with |)
            if line.startswith('|') and line.endswith('|'):
                # Extract header
                headers = [h.strip() for h in line.split('|')[1:-1]]

                # Skip separator line
                if i + 1 < len(lines) and '---' in lines[i + 1]:
                    i += 2
                    rows = []

                    # Extract data rows
                    while i < len(lines):
                        row_line = lines[i].strip()
                        if row_line.startswith('|') and row_line.endswith('|'):
                            row = [cell.strip() for cell in row_line.split('|')[1:-1]]
                            rows.append(row)
                            i += 1
                        else:
                            break

                    if rows:
                        tables.append({
                            'headers': headers,
                            'rows': rows
                        })
                    continue

            i += 1

        return tables

    def _create_chart_from_table(self, chart_id: str, section_title: str, table_data: Dict[str, Any]):
        """
        Create an appropriate chart based on table data.

        Args:
            chart_id: Unique chart identifier
            section_title: Section title for chart title
            table_data: Table data with headers and rows
        """
        headers = table_data['headers']
        rows = table_data['rows']

        if len(headers) < 2 or len(rows) == 0:
            return

        # Extract categories (first column) and values
        categories = [row[0] for row in rows]

        # Try to detect numeric data
        try:
            # Second column as primary data
            data = [float(row[1].replace(',', '').replace('%', '')) for row in rows]

            # Determine chart type based on data characteristics
            if len(categories) <= 7:
                # Bar chart for small datasets
                self.chart_generator.add_bar_chart(
                    chart_id=chart_id,
                    title=f"{section_title} - {headers[1]}",
                    categories=categories,
                    data=data,
                    y_axis_name=headers[1]
                )
            else:
                # Line chart for larger datasets (trends)
                self.chart_generator.add_line_chart(
                    chart_id=chart_id,
                    title=f"{section_title} - {headers[1]}",
                    categories=categories,
                    data=data,
                    y_axis_name=headers[1]
                )

            # If there's a third numeric column, create dual-axis chart
            if len(headers) >= 3 and len(rows[0]) >= 3:
                try:
                    data2 = [float(row[2].replace(',', '').replace('%', '')) for row in rows]
                    dual_chart_id = f"{chart_id}_dual"

                    self.chart_generator.add_dual_axis_chart(
                        chart_id=dual_chart_id,
                        title=f"{section_title} - 对比分析",
                        categories=categories,
                        bar_data=data,
                        line_data=data2,
                        bar_name=headers[1],
                        line_name=headers[2],
                        bar_y_axis_name=headers[1],
                        line_y_axis_name=headers[2]
                    )
                except (ValueError, IndexError):
                    pass

        except (ValueError, IndexError):
            # Not numeric data, skip visualization
            pass

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
