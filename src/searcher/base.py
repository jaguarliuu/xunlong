"""TODO: Add docstring."""

from abc import ABC, abstractmethod
from typing import List
from playwright.async_api import Page

from ..models import SearchLink


class BaseSearcher(ABC):
    """TODO: Add docstring."""
    
    def __init__(self, topk: int = 5):
        self.topk = topk
    
    @abstractmethod
    async def search(self, page: Page, query: str) -> List[SearchLink]:
        """
        
        
        Args:
            page: Playwright
            query: 
            
        Returns:
            
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """TODO: Add docstring."""
        pass