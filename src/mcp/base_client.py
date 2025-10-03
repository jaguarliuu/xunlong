"""
MCP客户端基类

提供MCP服务器的基础接口和功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger
import httpx
import json


@dataclass
class MCPClientConfig:
    """MCP客户端配置"""
    name: str
    description: str
    url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30
    enabled: bool = True
    extra_config: Optional[Dict[str, Any]] = None


class BaseMCPClient(ABC):
    """MCP客户端基类"""

    def __init__(self, config: MCPClientConfig):
        """
        初始化MCP客户端

        Args:
            config: MCP客户端配置
        """
        self.config = config
        self.name = config.name
        self.enabled = config.enabled

        if not self.enabled:
            logger.info(f"[{self.name}] MCP客户端已禁用")
            return

        logger.info(f"[{self.name}] MCP客户端初始化完成")

    @abstractmethod
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用MCP工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具调用结果
        """
        pass

    @abstractmethod
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        获取可用工具列表

        Returns:
            工具列表，每个工具包含name, description, parameters等信息
        """
        pass

    @abstractmethod
    def get_prompt_instruction(self, tool_name: str, **kwargs) -> str:
        """
        获取提示词指令，用于指导LLM调用此工具

        Args:
            tool_name: 工具名称
            **kwargs: 额外参数

        Returns:
            提示词指令
        """
        pass

    def is_enabled(self) -> bool:
        """检查客户端是否启用"""
        return self.enabled

    async def _make_sse_request(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        发送SSE请求并解析响应

        Args:
            url: 请求URL
            data: 请求数据
            headers: 请求头

        Returns:
            SSE事件列表
        """
        events = []

        try:
            logger.info(f"[{self.name}] 发起SSE请求: {'POST' if data else 'GET'} {url[:100]}...")

            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                async with client.stream(
                    'POST' if data else 'GET',
                    url,
                    json=data,
                    headers=headers or {}
                ) as response:
                    logger.info(f"[{self.name}] SSE响应状态: {response.status_code}")
                    logger.info(f"[{self.name}] SSE响应头: {dict(response.headers)}")

                    response.raise_for_status()

                    line_count = 0
                    async for line in response.aiter_lines():
                        line_count += 1
                        if not line:
                            continue

                        logger.debug(f"[{self.name}] SSE行 {line_count}: {line[:200]}")

                        # 解析SSE格式
                        if line.startswith('data: '):
                            data_str = line[6:].strip()

                            # 跳过特殊标记
                            if data_str in ['[DONE]', '']:
                                logger.debug(f"[{self.name}] 跳过特殊标记: {data_str}")
                                continue

                            try:
                                event_data = json.loads(data_str)
                                events.append(event_data)
                                logger.debug(f"[{self.name}] 解析事件成功: {len(events)} 个事件")
                            except json.JSONDecodeError as je:
                                logger.warning(f"[{self.name}] 无法解析SSE数据: {data_str[:200]}")
                                logger.warning(f"[{self.name}] JSON错误: {je}")
                        else:
                            # 可能是event:、id:等其他SSE字段
                            logger.debug(f"[{self.name}] SSE其他字段: {line[:200]}")

                    logger.info(f"[{self.name}] SSE流结束，共接收 {line_count} 行，解析 {len(events)} 个事件")

        except httpx.HTTPError as e:
            logger.error(f"[{self.name}] SSE请求失败: {e}")
            logger.error(f"[{self.name}] 错误类型: {type(e).__name__}")
            logger.error(f"[{self.name}] 错误详情: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"[{self.name}] 响应状态: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
                logger.error(f"[{self.name}] 响应内容: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
            raise
        except Exception as e:
            logger.error(f"[{self.name}] SSE请求异常: {e}")
            logger.error(f"[{self.name}] 异常类型: {type(e).__name__}")
            import traceback
            logger.error(f"[{self.name}] 堆栈跟踪:\n{traceback.format_exc()}")
            raise

        return events

    async def _make_http_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求

        Args:
            method: HTTP方法
            url: 请求URL
            data: 请求数据
            headers: 请求头

        Returns:
            响应数据
        """
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.request(
                    method,
                    url,
                    json=data,
                    headers=headers or {}
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"[{self.name}] HTTP请求失败: {e}")
            raise
