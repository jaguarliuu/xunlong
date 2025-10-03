"""
MCP (Model Context Protocol) 客户端模块

支持多种MCP服务器集成，提供统一的接口
"""

from .base_client import BaseMCPClient, MCPClientConfig
from .zhipu_web_search import ZhipuWebSearchClient
from .mcp_manager import MCPManager

__all__ = [
    'BaseMCPClient',
    'MCPClientConfig',
    'ZhipuWebSearchClient',
    'MCPManager'
]
