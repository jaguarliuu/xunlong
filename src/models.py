"""数据模型定义"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class PageExtract(BaseModel):
    """单个页面抽取结果"""
    
    url: str
    title: str
    text: str
    length: int
    screenshot_path: Optional[str] = None
    og_image_url: Optional[str] = None
    first_image_url: Optional[str] = None
    error: Optional[str] = None


class SearchResult(BaseModel):
    """搜索结果汇总"""
    
    query: str
    engine: str
    items: List[PageExtract]
    total_found: int
    success_count: int
    error_count: int
    execution_time: float


class SearchLink(BaseModel):
    """搜索链接信息"""
    
    url: str
    title: str
    snippet: Optional[str] = None