"""搜索器模块"""

from .base import BaseSearcher
from .duckduckgo import DuckDuckGoSearcher

__all__ = ["BaseSearcher", "DuckDuckGoSearcher"]