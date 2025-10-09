"""



"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TemplateInfo:
    """TODO: Add docstring."""
    name: str
    agent_type: str  # document, fiction, ppt
    file_path: str
    description: str
    framework: Optional[str] = None  # PPT
    supports_themes: List[str] = None
    preview_url: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.supports_themes is None:
            self.supports_themes = ['light', 'dark']
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ThemeInfo:
    """TODO: Add docstring."""
    name: str
    display_name: str
    description: str
    css_vars: Dict[str, str]  # CSS
    applies_to: List[str]  # 

    def to_dict(self) -> Dict:
        return asdict(self)


class TemplateRegistry:
    """TODO: Add docstring."""

    def __init__(self, config_file: Optional[Path] = None):
        """
        

        Args:
            config_file: 
        """
        self.config_file = config_file or self._get_default_config_file()
        self.templates: Dict[str, TemplateInfo] = {}
        self.themes: Dict[str, ThemeInfo] = {}

        # 
        self._load_config()

        # 
        self._register_default_templates()

        # 
        self._register_default_themes()

    def _get_default_config_file(self) -> Path:
        """TODO: Add docstring."""
        return Path(__file__).parent.parent.parent.parent / 'config' / 'html_templates.json'

    def _load_config(self):
        """TODO: Add docstring."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 
                for template_data in config.get('templates', []):
                    template = TemplateInfo(**template_data)
                    self.templates[self._make_key(template.agent_type, template.name)] = template

                # 
                for theme_data in config.get('themes', []):
                    theme = ThemeInfo(**theme_data)
                    self.themes[theme.name] = theme

                logger.info(f" {len(self.templates)}  {len(self.themes)} ")
            except Exception as e:
                logger.error(f": {e}")

    def save_config(self):
        """TODO: Add docstring."""
        try:
            config = {
                'templates': [t.to_dict() for t in self.templates.values()],
                'themes': [t.to_dict() for t in self.themes.values()]
            }

            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f": {self.config_file}")
        except Exception as e:
            logger.error(f": {e}")

    def _make_key(self, agent_type: str, template_name: str) -> str:
        """TODO: Add docstring."""
        return f"{agent_type}:{template_name}"

    def _register_default_templates(self):
        """TODO: Add docstring."""
        default_templates = [
            # 
            TemplateInfo(
                name="academic",
                agent_type="document",
                file_path="academic.html",
                description="",
                supports_themes=['light', 'dark'],
                tags=['academic', 'formal', 'research']
            ),
            TemplateInfo(
                name="technical",
                agent_type="document",
                file_path="technical.html",
                description="API",
                supports_themes=['light', 'dark'],
                tags=['technical', 'documentation']
            ),
            # 
            TemplateInfo(
                name="novel",
                agent_type="fiction",
                file_path="novel.html",
                description="",
                supports_themes=['light', 'dark', 'sepia'],
                tags=['fiction', 'reading', 'novel']
            ),
            TemplateInfo(
                name="ebook",
                agent_type="fiction",
                file_path="ebook.html",
                description="Kindle",
                supports_themes=['light', 'dark', 'sepia'],
                tags=['fiction', 'ebook']
            ),
            # PPT
            TemplateInfo(
                name="default",
                agent_type="ppt",
                file_path="reveal_default.html",
                description="Reveal.js",
                framework="reveal",
                supports_themes=['black', 'white', 'league', 'sky', 'beige', 'simple', 'serif', 'blood', 'night', 'moon', 'solarized'],
                tags=['presentation', 'reveal', 'default']
            ),
            TemplateInfo(
                name="business",
                agent_type="ppt",
                file_path="reveal_business.html",
                description="",
                framework="reveal",
                supports_themes=['white', 'black', 'league'],
                tags=['presentation', 'business', 'corporate']
            ),
        ]

        for template in default_templates:
            key = self._make_key(template.agent_type, template.name)
            if key not in self.templates:
                self.templates[key] = template

    def _register_default_themes(self):
        """TODO: Add docstring."""
        default_themes = [
            # 
            ThemeInfo(
                name="light",
                display_name="",
                description="",
                css_vars={
                    "--bg-color": "#ffffff",
                    "--text-color": "#333333",
                    "--primary-color": "#2c3e50",
                    "--secondary-color": "#3498db"
                },
                applies_to=['document', 'fiction']
            ),
            ThemeInfo(
                name="dark",
                display_name="",
                description="",
                css_vars={
                    "--bg-color": "#1a1a1a",
                    "--text-color": "#d4d4d4",
                    "--primary-color": "#f39c12",
                    "--secondary-color": "#3498db"
                },
                applies_to=['document', 'fiction']
            ),
            ThemeInfo(
                name="sepia",
                display_name="",
                description="",
                css_vars={
                    "--bg-color": "#f5f0e8",
                    "--text-color": "#5c4a3a",
                    "--primary-color": "#8b4513",
                    "--secondary-color": "#cd853f"
                },
                applies_to=['fiction']
            ),
        ]

        for theme in default_themes:
            if theme.name not in self.themes:
                self.themes[theme.name] = theme

    def register_template(self, template: TemplateInfo):
        """
        

        Args:
            template: 
        """
        key = self._make_key(template.agent_type, template.name)
        self.templates[key] = template
        logger.info(f": {key}")

    def register_theme(self, theme: ThemeInfo):
        """
        

        Args:
            theme: 
        """
        self.themes[theme.name] = theme
        logger.info(f": {theme.name}")

    def get_template(self, agent_type: str, template_name: str) -> Optional[TemplateInfo]:
        """TODO: Add docstring."""
        key = self._make_key(agent_type, template_name)
        return self.templates.get(key)

    def get_theme(self, theme_name: str) -> Optional[ThemeInfo]:
        """TODO: Add docstring."""
        return self.themes.get(theme_name)

    def list_templates(self, agent_type: Optional[str] = None) -> List[TemplateInfo]:
        """
        

        Args:
            agent_type: 

        Returns:
            
        """
        if agent_type:
            return [t for t in self.templates.values() if t.agent_type == agent_type]
        return list(self.templates.values())

    def list_themes(self, applies_to: Optional[str] = None) -> List[ThemeInfo]:
        """
        

        Args:
            applies_to: 

        Returns:
            
        """
        if applies_to:
            return [t for t in self.themes.values() if applies_to in t.applies_to]
        return list(self.themes.values())

    def recommend_template(
        self,
        agent_type: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        

        Args:
            agent_type: Agent
            content: 
            metadata: 

        Returns:
            
        """
        templates = self.list_templates(agent_type)

        if not templates:
            return "default"

        # AI
        metadata = metadata or {}

        if agent_type == 'document':
            # academic
            if any(keyword in content.lower() for keyword in ['abstract', 'references', 'citation', '', '']):
                return "academic"
            return "technical"

        elif agent_type == 'fiction':
            # novel
            return "novel"

        elif agent_type == 'ppt':
            # business
            if any(keyword in content.lower() for keyword in ['market', 'business', '', '', '']):
                return "business"
            return "default"

        return templates[0].name

    def recommend_theme(
        self,
        agent_type: str,
        template_name: str,
        user_preference: Optional[str] = None
    ) -> str:
        """
        

        Args:
            agent_type: Agent
            template_name: 
            user_preference: 

        Returns:
            
        """
        # 
        if user_preference:
            theme = self.get_theme(user_preference)
            if theme and agent_type in theme.applies_to:
                return user_preference

        # 
        template = self.get_template(agent_type, template_name)
        if template and template.supports_themes:
            # 
            return template.supports_themes[0]

        # 
        return "light" if agent_type != 'ppt' else "white"


# 
_global_registry: Optional[TemplateRegistry] = None


def get_template_registry() -> TemplateRegistry:
    """TODO: Add docstring."""
    global _global_registry
    if _global_registry is None:
        _global_registry = TemplateRegistry()
    return _global_registry
