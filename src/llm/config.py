"""LLM"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class LLMProvider(str, Enum):
    """LLM"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


class LLMConfig(BaseModel):
    """LLM"""
    
    # 
    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM"
    )
    
    model_name: str = Field(
        default="gpt-4o-mini",
        description=""
    )
    
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("LLM_API_KEY"),
        description="API"
    )
    
    base_url: Optional[str] = Field(
        default_factory=lambda: os.getenv("LLM_BASE_URL"),
        description="APIURL"
    )
    
    # 
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description=""
    )
    
    max_tokens: int = Field(
        default=4000,
        gt=0,
        description="token"
    )
    
    top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Top-p"
    )
    
    # Azure OpenAI 
    azure_deployment: Optional[str] = Field(
        default_factory=lambda: os.getenv("AZURE_DEPLOYMENT"),
        description="Azure"
    )
    
    azure_api_version: str = Field(
        default="2025-02-15-preview",
        description="Azure API"
    )
    
    # 
    timeout: int = Field(
        default=60,
        gt=0,
        description=""
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        description=""
    )
    
    # 
    stream: bool = Field(
        default=False,
        description=""
    )
    
    class Config:
        env_prefix = "LLM_"
        case_sensitive = False


# 
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
        "model_name": "claude-3-sonnet-20250229"
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
    """LLM"""
    
    # 
    provider_config = PROVIDER_CONFIGS.get(provider, {})
    
    # 
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


# 
default_llm_config = LLMConfig()