"""TODO: Add docstring."""

import os
from typing import Optional
from pydantic import BaseModel, Field


class DeepSearchConfig(BaseModel):
    """DeepSearch """
    
    # 
    headless: bool = Field(
        default_factory=lambda: os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
        description=""
    )
    
    # 
    search_engine: str = Field(
        default="duckduckgo",
        description=": duckduckgo, google, bing"
    )
    
    # 
    topk: int = Field(
        default=5,
        description=""
    )
    
    # 
    shots_dir: str = Field(
        default="./results/shots",
        description=""
    )
    
    # 
    output_json_path: Optional[str] = Field(
        default=None,
        description="JSON"
    )
    
    # 
    browser_timeout: int = Field(
        default=30000,
        description=""
    )
    
    # 
    page_wait_time: int = Field(
        default=3000,
        description=""
    )
    
    # 
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description=""
    )
    
    class Config:
        env_prefix = "DEEPSEARCH_"
        case_sensitive = False


# 
config = DeepSearchConfig()