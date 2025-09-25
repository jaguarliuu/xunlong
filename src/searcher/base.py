"""搜索器基类"""

from abc import ABC, abstractmethod
from typing import List
from playwright.async_api import Page

from ..models import SearchLink


class BaseSearcher(ABC):
    """搜索器抽象基类"""
    
    def __init__(self, topk: int = 5):
        self.topk = topk
    
    @abstractmethod
    async def search(self, page: Page, query: str) -> List[SearchLink]:
        """
        执行搜索并返回结果链接
        
        Args:
            page: Playwright页面对象
            query: 搜索查询词
            
        Returns:
            搜索结果链接列表
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """搜索引擎名称"""
        pass