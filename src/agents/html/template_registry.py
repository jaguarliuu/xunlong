"""
模板注册和主题管理系统

支持动态注册模板和主题，以及模板选择推荐
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TemplateInfo:
    """模板信息"""
    name: str
    agent_type: str  # document, fiction, ppt
    file_path: str
    description: str
    framework: Optional[str] = None  # PPT专用
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
    """主题信息"""
    name: str
    display_name: str
    description: str
    css_vars: Dict[str, str]  # CSS变量定义
    applies_to: List[str]  # 适用的模板类型

    def to_dict(self) -> Dict:
        return asdict(self)


class TemplateRegistry:
    """模板注册中心"""

    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化模板注册中心

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or self._get_default_config_file()
        self.templates: Dict[str, TemplateInfo] = {}
        self.themes: Dict[str, ThemeInfo] = {}

        # 加载配置
        self._load_config()

        # 注册默认模板
        self._register_default_templates()

        # 注册默认主题
        self._register_default_themes()

    def _get_default_config_file(self) -> Path:
        """获取默认配置文件路径"""
        return Path(__file__).parent.parent.parent.parent / 'config' / 'html_templates.json'

    def _load_config(self):
        """从配置文件加载"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 加载模板
                for template_data in config.get('templates', []):
                    template = TemplateInfo(**template_data)
                    self.templates[self._make_key(template.agent_type, template.name)] = template

                # 加载主题
                for theme_data in config.get('themes', []):
                    theme = ThemeInfo(**theme_data)
                    self.themes[theme.name] = theme

                logger.info(f"从配置文件加载了 {len(self.templates)} 个模板和 {len(self.themes)} 个主题")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")

    def save_config(self):
        """保存配置到文件"""
        try:
            config = {
                'templates': [t.to_dict() for t in self.templates.values()],
                'themes': [t.to_dict() for t in self.themes.values()]
            }

            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f"配置已保存到: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def _make_key(self, agent_type: str, template_name: str) -> str:
        """生成模板键"""
        return f"{agent_type}:{template_name}"

    def _register_default_templates(self):
        """注册默认模板"""
        default_templates = [
            # 文档模板
            TemplateInfo(
                name="academic",
                agent_type="document",
                file_path="academic.html",
                description="学术风格文档，适合研究报告和论文",
                supports_themes=['light', 'dark'],
                tags=['academic', 'formal', 'research']
            ),
            TemplateInfo(
                name="technical",
                agent_type="document",
                file_path="technical.html",
                description="技术文档风格，适合API文档和技术说明",
                supports_themes=['light', 'dark'],
                tags=['technical', 'documentation']
            ),
            # 小说模板
            TemplateInfo(
                name="novel",
                agent_type="fiction",
                file_path="novel.html",
                description="小说阅读模板，提供舒适的阅读体验",
                supports_themes=['light', 'dark', 'sepia'],
                tags=['fiction', 'reading', 'novel']
            ),
            TemplateInfo(
                name="ebook",
                agent_type="fiction",
                file_path="ebook.html",
                description="电子书风格，类似Kindle阅读器",
                supports_themes=['light', 'dark', 'sepia'],
                tags=['fiction', 'ebook']
            ),
            # PPT模板
            TemplateInfo(
                name="default",
                agent_type="ppt",
                file_path="reveal_default.html",
                description="基于Reveal.js的默认演示模板",
                framework="reveal",
                supports_themes=['black', 'white', 'league', 'sky', 'beige', 'simple', 'serif', 'blood', 'night', 'moon', 'solarized'],
                tags=['presentation', 'reveal', 'default']
            ),
            TemplateInfo(
                name="business",
                agent_type="ppt",
                file_path="reveal_business.html",
                description="商务风格演示模板",
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
        """注册默认主题"""
        default_themes = [
            # 通用主题
            ThemeInfo(
                name="light",
                display_name="浅色主题",
                description="明亮的浅色配色方案",
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
                display_name="深色主题",
                description="护眼的深色配色方案",
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
                display_name="复古主题",
                description="温暖的复古纸张配色",
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
        注册新模板

        Args:
            template: 模板信息
        """
        key = self._make_key(template.agent_type, template.name)
        self.templates[key] = template
        logger.info(f"注册模板: {key}")

    def register_theme(self, theme: ThemeInfo):
        """
        注册新主题

        Args:
            theme: 主题信息
        """
        self.themes[theme.name] = theme
        logger.info(f"注册主题: {theme.name}")

    def get_template(self, agent_type: str, template_name: str) -> Optional[TemplateInfo]:
        """获取模板信息"""
        key = self._make_key(agent_type, template_name)
        return self.templates.get(key)

    def get_theme(self, theme_name: str) -> Optional[ThemeInfo]:
        """获取主题信息"""
        return self.themes.get(theme_name)

    def list_templates(self, agent_type: Optional[str] = None) -> List[TemplateInfo]:
        """
        列出模板

        Args:
            agent_type: 如果指定，只列出该类型的模板

        Returns:
            模板信息列表
        """
        if agent_type:
            return [t for t in self.templates.values() if t.agent_type == agent_type]
        return list(self.templates.values())

    def list_themes(self, applies_to: Optional[str] = None) -> List[ThemeInfo]:
        """
        列出主题

        Args:
            applies_to: 如果指定，只列出适用于该类型的主题

        Returns:
            主题信息列表
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
        推荐模板

        Args:
            agent_type: Agent类型
            content: 内容
            metadata: 元数据

        Returns:
            推荐的模板名称
        """
        templates = self.list_templates(agent_type)

        if not templates:
            return "default"

        # 简单推荐逻辑（可以扩展为AI推荐）
        metadata = metadata or {}

        if agent_type == 'document':
            # 如果有学术相关标签，推荐academic
            if any(keyword in content.lower() for keyword in ['abstract', 'references', 'citation', '摘要', '参考文献']):
                return "academic"
            return "technical"

        elif agent_type == 'fiction':
            # 小说统一使用novel模板
            return "novel"

        elif agent_type == 'ppt':
            # 如果是商务内容，推荐business
            if any(keyword in content.lower() for keyword in ['market', 'business', '市场', '商业', '销售']):
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
        推荐主题

        Args:
            agent_type: Agent类型
            template_name: 模板名称
            user_preference: 用户偏好

        Returns:
            推荐的主题名称
        """
        # 如果用户指定了偏好
        if user_preference:
            theme = self.get_theme(user_preference)
            if theme and agent_type in theme.applies_to:
                return user_preference

        # 获取模板支持的主题
        template = self.get_template(agent_type, template_name)
        if template and template.supports_themes:
            # 返回第一个支持的主题
            return template.supports_themes[0]

        # 默认主题
        return "light" if agent_type != 'ppt' else "white"


# 全局注册中心实例
_global_registry: Optional[TemplateRegistry] = None


def get_template_registry() -> TemplateRegistry:
    """获取全局模板注册中心实例"""
    global _global_registry
    if _global_registry is None:
        _global_registry = TemplateRegistry()
    return _global_registry
