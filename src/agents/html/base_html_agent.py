"""
BaseHTMLAgent - HTML

HTML
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import logging
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseHTMLAgent(ABC):
    """HTML"""

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        default_template: str = "default",
        default_theme: str = "light"
    ):
        """
        HTML

        Args:
            template_dir: 
            default_template: 
            default_theme: 
        """
        self.template_dir = template_dir or self._get_default_template_dir()
        self.default_template = default_template
        self.default_theme = default_theme

        # Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

        # 
        self._register_filters()

        logger.info(f" {self.__class__.__name__}: {self.template_dir}")

    @abstractmethod
    def _get_default_template_dir(self) -> Path:
        """TODO: Add docstring."""
        pass

    @abstractmethod
    def parse_content(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        

        Args:
            content: Markdown
            metadata: 

        Returns:
            
        """
        pass

    @abstractmethod
    def get_template_name(self, template: Optional[str] = None) -> str:
        """
        

        Args:
            template: 

        Returns:
            
        """
        pass

    def convert_to_html(
        self,
        content: str,
        metadata: Optional[Dict] = None,
        template: Optional[str] = None,
        theme: Optional[str] = None,
        custom_css: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> str:
        """
        HTML

        Args:
            content: 
            metadata: 
            template: 
            theme: 
            custom_css: CSS
            output_path: 

        Returns:
            HTML
        """
        try:
            # 
            parsed_data = self.parse_content(content, metadata)

            # 
            template_name = self.get_template_name(template)
            jinja_template = self.jinja_env.get_template(template_name)

            # 
            render_data = {
                **parsed_data,
                'theme': theme or self.default_theme,
                'custom_css': custom_css or '',
                'generated_at': datetime.now().isoformat(),
                'generator': self.__class__.__name__
            }

            # HTML
            html = jinja_template.render(**render_data)

            # 
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(html, encoding='utf-8')
                logger.info(f"HTML: {output_path}")

            return html

        except TemplateNotFound as e:
            logger.error(f": {e}")
            raise
        except Exception as e:
            logger.error(f"HTML: {e}")
            raise

    def _register_filters(self):
        """Jinja2"""

        # MarkdownHTML
        def markdown_filter(text: str) -> str:
            try:
                import markdown
                return markdown.markdown(
                    text,
                    extensions=['extra', 'codehilite', 'toc', 'tables']
                )
            except ImportError:
                logger.warning("markdownMarkdown")
                # Markdown
                import re
                import html as html_module

                # HTML
                text = html_module.escape(text)

                #  ```
                text = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code class="\1">\2</code></pre>', text, flags=re.DOTALL)

                #  `code`
                text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

                #  ![alt](url) - 
                text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)

                #  [text](url)
                text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

                #  ***text*** - 
                text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
                text = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', text)

                #  **text**  __text__ - 
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

                #  *text*  _text_
                text = re.sub(r'\*([^\*]+?)\*', r'<em>\1</em>', text)
                text = re.sub(r'\b_([^_]+?)_\b', r'<em>\1</em>', text)

                # 
                text = text.replace('\n\n', '</p><p>')
                text = text.replace('\n', '<br>')
                text = '<p>' + text + '</p>'

                return text

        # 
        def dateformat_filter(value, format='%Y-%m-%d %H:%M:%S'):
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except:
                    return value
            if isinstance(value, datetime):
                return value.strftime(format)
            return value

        # JSON
        def jsonify_filter(value):
            return json.dumps(value, ensure_ascii=False, indent=2)

        # 
        self.jinja_env.filters['markdown'] = markdown_filter
        self.jinja_env.filters['dateformat'] = dateformat_filter
        self.jinja_env.filters['jsonify'] = jsonify_filter

    def list_available_templates(self) -> List[str]:
        """TODO: Add docstring."""
        templates = []
        for file in self.template_dir.glob('*.html'):
            templates.append(file.stem)
        return sorted(templates)

    def validate_template(self, template_name: str) -> bool:
        """TODO: Add docstring."""
        try:
            self.jinja_env.get_template(self.get_template_name(template_name))
            return True
        except TemplateNotFound:
            return False

    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """
        

        Returns:
            
        """
        try:
            template_path = self.template_dir / self.get_template_name(template_name)
            if not template_path.exists():
                return None

            content = template_path.read_text(encoding='utf-8')

            # HTML
            # : <!-- METADATA: {"name": "...", "description": "..."} -->
            import re
            match = re.search(r'<!--\s*METADATA:\s*({.*?})\s*-->', content, re.DOTALL)
            if match:
                return json.loads(match.group(1))

            return {
                'name': template_name,
                'description': 'No description available'
            }
        except Exception as e:
            logger.error(f": {e}")
            return None


class TemplateManager:
    """ - HTML Agent"""

    def __init__(self, base_template_dir: Optional[Path] = None):
        """
        

        Args:
            base_template_dir: 
        """
        if base_template_dir is None:
            # 
            base_template_dir = Path(__file__).parent.parent.parent.parent / 'templates' / 'html'

        self.base_template_dir = Path(base_template_dir)
        self.registered_templates: Dict[str, Dict] = {}

        # 
        self.base_template_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f": {self.base_template_dir}")

    def register_template(
        self,
        agent_type: str,
        template_name: str,
        template_file: str,
        metadata: Optional[Dict] = None
    ):
        """
        

        Args:
            agent_type: Agent (document, fiction, ppt)
            template_name: 
            template_file: 
            metadata: 
        """
        key = f"{agent_type}:{template_name}"
        self.registered_templates[key] = {
            'agent_type': agent_type,
            'template_name': template_name,
            'template_file': template_file,
            'metadata': metadata or {}
        }
        logger.info(f": {key}")

    def get_template_path(self, agent_type: str, template_name: str) -> Optional[Path]:
        """TODO: Add docstring."""
        key = f"{agent_type}:{template_name}"
        if key in self.registered_templates:
            return self.base_template_dir / agent_type / self.registered_templates[key]['template_file']
        return None

    def list_templates(self, agent_type: Optional[str] = None) -> Dict[str, List[Dict]]:
        """TODO: Add docstring."""
        if agent_type:
            return {
                agent_type: [
                    v for k, v in self.registered_templates.items()
                    if v['agent_type'] == agent_type
                ]
            }

        # agent_type
        result = {}
        for template_info in self.registered_templates.values():
            at = template_info['agent_type']
            if at not in result:
                result[at] = []
            result[at].append(template_info)

        return result

    def get_template_dir(self, agent_type: str) -> Path:
        """Agent"""
        dir_path = self.base_template_dir / agent_type
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path


# 
_global_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """TODO: Add docstring."""
    global _global_template_manager
    if _global_template_manager is None:
        _global_template_manager = TemplateManager()
    return _global_template_manager
