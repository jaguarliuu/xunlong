"""
BaseHTMLAgent - HTML转换智能体基类

提供统一的HTML转换接口和通用功能
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
    """HTML转换智能体基类"""

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        default_template: str = "default",
        default_theme: str = "light"
    ):
        """
        初始化HTML转换智能体

        Args:
            template_dir: 模板目录路径
            default_template: 默认模板名称
            default_theme: 默认主题名称
        """
        self.template_dir = template_dir or self._get_default_template_dir()
        self.default_template = default_template
        self.default_theme = default_theme

        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

        # 添加自定义过滤器
        self._register_filters()

        logger.info(f"初始化 {self.__class__.__name__}，模板目录: {self.template_dir}")

    @abstractmethod
    def _get_default_template_dir(self) -> Path:
        """获取默认模板目录"""
        pass

    @abstractmethod
    def parse_content(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        解析内容

        Args:
            content: 原始内容（通常是Markdown）
            metadata: 元数据

        Returns:
            解析后的结构化数据
        """
        pass

    @abstractmethod
    def get_template_name(self, template: Optional[str] = None) -> str:
        """
        获取模板文件名

        Args:
            template: 模板名称

        Returns:
            完整的模板文件名
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
        转换内容为HTML

        Args:
            content: 原始内容
            metadata: 元数据
            template: 模板名称
            theme: 主题名称
            custom_css: 自定义CSS
            output_path: 输出路径（如果提供，会保存文件）

        Returns:
            生成的HTML字符串
        """
        try:
            # 解析内容
            parsed_data = self.parse_content(content, metadata)

            # 获取模板
            template_name = self.get_template_name(template)
            jinja_template = self.jinja_env.get_template(template_name)

            # 准备渲染数据
            render_data = {
                **parsed_data,
                'theme': theme or self.default_theme,
                'custom_css': custom_css or '',
                'generated_at': datetime.now().isoformat(),
                'generator': self.__class__.__name__
            }

            # 渲染HTML
            html = jinja_template.render(**render_data)

            # 保存文件
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(html, encoding='utf-8')
                logger.info(f"HTML已保存到: {output_path}")

            return html

        except TemplateNotFound as e:
            logger.error(f"模板未找到: {e}")
            raise
        except Exception as e:
            logger.error(f"HTML转换失败: {e}")
            raise

    def _register_filters(self):
        """注册Jinja2自定义过滤器"""

        # Markdown转HTML过滤器
        def markdown_filter(text: str) -> str:
            try:
                import markdown
                return markdown.markdown(
                    text,
                    extensions=['extra', 'codehilite', 'toc', 'tables']
                )
            except ImportError:
                logger.warning("markdown库未安装，使用简单Markdown处理")
                # 基础Markdown语法转换
                import re
                import html as html_module

                # HTML转义
                text = html_module.escape(text)

                # 处理代码块 ```
                text = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code class="\1">\2</code></pre>', text, flags=re.DOTALL)

                # 处理行内代码 `code`
                text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

                # 处理图片 ![alt](url) - 必须在链接之前处理
                text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)

                # 处理链接 [text](url)
                text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

                # 处理粗体加斜体 ***text*** - 必须在单独的粗体和斜体之前
                text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
                text = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', text)

                # 处理粗体 **text** 或 __text__ - 必须在斜体之前
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

                # 处理斜体 *text* 或 _text_
                text = re.sub(r'\*([^\*]+?)\*', r'<em>\1</em>', text)
                text = re.sub(r'\b_([^_]+?)_\b', r'<em>\1</em>', text)

                # 处理换行
                text = text.replace('\n\n', '</p><p>')
                text = text.replace('\n', '<br>')
                text = '<p>' + text + '</p>'

                return text

        # 日期格式化过滤器
        def dateformat_filter(value, format='%Y-%m-%d %H:%M:%S'):
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except:
                    return value
            if isinstance(value, datetime):
                return value.strftime(format)
            return value

        # JSON格式化过滤器
        def jsonify_filter(value):
            return json.dumps(value, ensure_ascii=False, indent=2)

        # 注册过滤器
        self.jinja_env.filters['markdown'] = markdown_filter
        self.jinja_env.filters['dateformat'] = dateformat_filter
        self.jinja_env.filters['jsonify'] = jsonify_filter

    def list_available_templates(self) -> List[str]:
        """列出可用的模板"""
        templates = []
        for file in self.template_dir.glob('*.html'):
            templates.append(file.stem)
        return sorted(templates)

    def validate_template(self, template_name: str) -> bool:
        """验证模板是否存在"""
        try:
            self.jinja_env.get_template(self.get_template_name(template_name))
            return True
        except TemplateNotFound:
            return False

    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """
        获取模板信息

        Returns:
            包含模板元数据的字典，如果模板包含元数据注释的话
        """
        try:
            template_path = self.template_dir / self.get_template_name(template_name)
            if not template_path.exists():
                return None

            content = template_path.read_text(encoding='utf-8')

            # 尝试从HTML注释中提取元数据
            # 格式: <!-- METADATA: {"name": "...", "description": "..."} -->
            import re
            match = re.search(r'<!--\s*METADATA:\s*({.*?})\s*-->', content, re.DOTALL)
            if match:
                return json.loads(match.group(1))

            return {
                'name': template_name,
                'description': 'No description available'
            }
        except Exception as e:
            logger.error(f"获取模板信息失败: {e}")
            return None


class TemplateManager:
    """模板管理器 - 管理多个HTML Agent的模板"""

    def __init__(self, base_template_dir: Optional[Path] = None):
        """
        初始化模板管理器

        Args:
            base_template_dir: 基础模板目录
        """
        if base_template_dir is None:
            # 默认模板目录
            base_template_dir = Path(__file__).parent.parent.parent.parent / 'templates' / 'html'

        self.base_template_dir = Path(base_template_dir)
        self.registered_templates: Dict[str, Dict] = {}

        # 确保目录存在
        self.base_template_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"模板管理器初始化，基础目录: {self.base_template_dir}")

    def register_template(
        self,
        agent_type: str,
        template_name: str,
        template_file: str,
        metadata: Optional[Dict] = None
    ):
        """
        注册模板

        Args:
            agent_type: Agent类型 (document, fiction, ppt)
            template_name: 模板名称
            template_file: 模板文件路径
            metadata: 模板元数据
        """
        key = f"{agent_type}:{template_name}"
        self.registered_templates[key] = {
            'agent_type': agent_type,
            'template_name': template_name,
            'template_file': template_file,
            'metadata': metadata or {}
        }
        logger.info(f"注册模板: {key}")

    def get_template_path(self, agent_type: str, template_name: str) -> Optional[Path]:
        """获取模板路径"""
        key = f"{agent_type}:{template_name}"
        if key in self.registered_templates:
            return self.base_template_dir / agent_type / self.registered_templates[key]['template_file']
        return None

    def list_templates(self, agent_type: Optional[str] = None) -> Dict[str, List[Dict]]:
        """列出模板"""
        if agent_type:
            return {
                agent_type: [
                    v for k, v in self.registered_templates.items()
                    if v['agent_type'] == agent_type
                ]
            }

        # 按agent_type分组
        result = {}
        for template_info in self.registered_templates.values():
            at = template_info['agent_type']
            if at not in result:
                result[at] = []
            result[at].append(template_info)

        return result

    def get_template_dir(self, agent_type: str) -> Path:
        """获取指定Agent类型的模板目录"""
        dir_path = self.base_template_dir / agent_type
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path


# 全局模板管理器实例
_global_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """获取全局模板管理器实例"""
    global _global_template_manager
    if _global_template_manager is None:
        _global_template_manager = TemplateManager()
    return _global_template_manager
