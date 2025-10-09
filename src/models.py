"""TODO: Add docstring."""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class PageExtract(BaseModel):
    """TODO: Add docstring."""
    
    url: str
    title: str
    text: str
    length: int
    screenshot_path: Optional[str] = None
    og_image_url: Optional[str] = None
    first_image_url: Optional[str] = None
    error: Optional[str] = None


class SearchResult(BaseModel):
    """TODO: Add docstring."""
    
    query: str
    engine: str
    items: List[PageExtract]
    total_found: int
    success_count: int
    error_count: int
    execution_time: float


class SearchLink(BaseModel):
    """TODO: Add docstring."""
    
    url: str
    title: str
    snippet: Optional[str] = None