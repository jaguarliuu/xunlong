"""
API Configuration Management

Centralized configuration using Pydantic Settings for environment-based configuration.
"""

from functools import lru_cache
from typing import Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # Allow extra fields from .env
    )

    # Application
    app_name: str = "XunLong API"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, description="Enable debug mode")

    # Server
    host: str = Field(default="0.0.0.0", description="API server host")
    port: int = Field(default=8000, description="API server port")
    reload: bool = Field(default=False, description="Enable auto-reload for development")

    # CORS
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # API
    api_v1_prefix: str = "/api/v1"

    # Task Management
    task_storage_dir: str = Field(
        default="tasks",
        description="Directory for storing task metadata"
    )
    max_concurrent_tasks: int = Field(
        default=10,
        description="Maximum number of concurrent tasks"
    )
    task_timeout_seconds: int = Field(
        default=3600,
        description="Default task timeout in seconds"
    )

    # Worker
    worker_poll_interval: float = Field(
        default=2.0,
        description="Worker polling interval in seconds"
    )
    worker_max_retries: int = Field(
        default=3,
        description="Maximum number of task retry attempts"
    )

    # Storage
    storage_dir: str = Field(
        default="storage",
        description="Directory for storing generated content"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Loguru log format"
    )

    # Security (placeholder for future authentication)
    secret_key: Optional[str] = Field(
        default=None,
        description="Secret key for JWT token generation"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )

    # LLM Provider API Keys (optional - loaded from .env)
    langfuse_secret_key: Optional[str] = None
    langfuse_pub_key: Optional[str] = None
    langfuse_host: Optional[str] = "https://cloud.langfuse.com"

    dashscope_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    zhipu_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None

    # MCP Services
    zhipu_mcp_api_key: Optional[str] = None

    # Image Services
    unsplash_access_key: Optional[str] = None
    pexels_api_key: Optional[str] = None
    enable_document_images: bool = False
    images_per_section: int = 2
    image_insert_mode: str = "smart"

    # Default LLM Configuration
    default_llm_provider: str = "deepseek"
    default_llm_model: str = "deepseek-chat"
    default_llm_temperature: float = 0.7
    default_llm_max_tokens: int = 4000

    # Legacy project settings (for compatibility)
    project_name: Optional[str] = None
    project_version: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Convenience access
settings = get_settings()
