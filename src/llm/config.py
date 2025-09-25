"""LLM配置管理"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class LLMProvider(str, Enum):
    """支持的LLM提供商"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


class LLMConfig(BaseModel):
    """LLM配置类"""
    
    # 基础配置
    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM提供商"
    )
    
    model_name: str = Field(
        default="gpt-4o-mini",
        description="模型名称"
    )
    
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("LLM_API_KEY"),
        description="API密钥"
    )
    
    base_url: Optional[str] = Field(
        default_factory=lambda: os.getenv("LLM_BASE_URL"),
        description="API基础URL"
    )
    
    # 生成参数
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成温度"
    )
    
    max_tokens: int = Field(
        default=4000,
        gt=0,
        description="最大生成token数"
    )
    
    top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Top-p采样参数"
    )
    
    # Azure OpenAI 特有配置
    azure_deployment: Optional[str] = Field(
        default_factory=lambda: os.getenv("AZURE_DEPLOYMENT"),
        description="Azure部署名称"
    )
    
    azure_api_version: str = Field(
        default="2024-02-15-preview",
        description="Azure API版本"
    )
    
    # 请求配置
    timeout: int = Field(
        default=60,
        gt=0,
        description="请求超时时间（秒）"
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        description="最大重试次数"
    )
    
    # 流式输出
    stream: bool = Field(
        default=False,
        description="是否使用流式输出"
    )
    
    class Config:
        env_prefix = "LLM_"
        case_sensitive = False


# 预定义配置
PROVIDER_CONFIGS = {
    LLMProvider.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o-mini"
    },
    LLMProvider.AZURE_OPENAI: {
        "model_name": "gpt-4"
    },
    LLMProvider.ANTHROPIC: {
        "base_url": "https://api.anthropic.com",
        "model_name": "claude-3-sonnet-20240229"
    },
    LLMProvider.ZHIPU: {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_name": "glm-4"
    },
    LLMProvider.QWEN: {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_name": "qwen-turbo"
    },
    LLMProvider.DEEPSEEK: {
        "base_url": "https://api.deepseek.com/v1",
        "model_name": "deepseek-chat"
    },
    LLMProvider.OLLAMA: {
        "base_url": "http://localhost:11434/v1",
        "model_name": "llama3"
    }
}


def create_llm_config(
    provider: LLMProvider,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs
) -> LLMConfig:
    """创建LLM配置"""
    
    # 获取预定义配置
    provider_config = PROVIDER_CONFIGS.get(provider, {})
    
    # 合并配置
    config_data = {
        "provider": provider,
        **provider_config,
        **kwargs
    }
    
    if api_key:
        config_data["api_key"] = api_key
    
    if model_name:
        config_data["model_name"] = model_name
    
    return LLMConfig(**config_data)


# 全局默认配置
default_llm_config = LLMConfig()