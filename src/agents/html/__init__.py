"""
HTML转换智能体模块

提供Markdown到HTML的转换功能，支持多种输出格式：
- 文档（Document）
- 小说（Fiction）
- PPT演示（PPT）
"""

from .base_html_agent import BaseHTMLAgent, TemplateManager, get_template_manager
from .document_html_agent import DocumentHTMLAgent
from .fiction_html_agent import FictionHTMLAgent
from .ppt_html_agent import PPTHTMLAgent
from .template_registry import (
    TemplateRegistry,
    TemplateInfo,
    ThemeInfo,
    get_template_registry
)

__all__ = [
    'BaseHTMLAgent',
    'TemplateManager',
    'get_template_manager',
    'DocumentHTMLAgent',
    'FictionHTMLAgent',
    'PPTHTMLAgent',
    'TemplateRegistry',
    'TemplateInfo',
    'ThemeInfo',
    'get_template_registry',
]
