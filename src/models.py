""""""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class PageExtract(BaseModel):
    """"""
    
    url: str
    title: str
    text: str
    length: int
    screenshot_path: Optional[str] = None
    og_image_url: Optional[str] = None
    first_image_url: Optional[str] = None
    error: Optional[str] = None


class SearchResult(BaseModel):
    """"""
    
    query: str
    engine: str
    items: List[PageExtract]
    total_found: int
    success_count: int
    error_count: int
    execution_time: float


class SearchLink(BaseModel):
    """"""
    
    url: str
    title: str
    snippet: Optional[str] = None