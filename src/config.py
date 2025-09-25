"""配置管理模块"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class DeepSearchConfig(BaseModel):
    """DeepSearch 配置类"""
    
    # 浏览器配置
    headless: bool = Field(
        default_factory=lambda: os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
        description="是否使用无头浏览器模式"
    )
    
    # 搜索引擎配置
    search_engine: str = Field(
        default="duckduckgo",
        description="搜索引擎类型: duckduckgo, google, bing"
    )
    
    # 搜索结果数量
    topk: int = Field(
        default=5,
        description="抓取搜索结果的数量"
    )
    
    # 截图保存目录
    shots_dir: str = Field(
        default="./results/shots",
        description="截图保存目录"
    )
    
    # 输出文件路径
    output_json_path: Optional[str] = Field(
        default=None,
        description="输出JSON文件路径（可选）"
    )
    
    # 浏览器配置
    browser_timeout: int = Field(
        default=30000,
        description="浏览器超时时间（毫秒）"
    )
    
    # 页面等待时间
    page_wait_time: int = Field(
        default=3000,
        description="页面加载等待时间（毫秒）"
    )
    
    # 用户代理
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description="浏览器用户代理"
    )
    
    class Config:
        env_prefix = "DEEPSEARCH_"
        case_sensitive = False


# 全局配置实例
config = DeepSearchConfig()