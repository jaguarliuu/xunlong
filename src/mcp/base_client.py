"""
MCP

MCP
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger
import httpx
import json


@dataclass
class MCPClientConfig:
    """MCP"""
    name: str
    description: str
    url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30
    enabled: bool = True
    extra_config: Optional[Dict[str, Any]] = None


class BaseMCPClient(ABC):
    """MCP"""

    def __init__(self, config: MCPClientConfig):
        """
        MCP

        Args:
            config: MCP
        """
        self.config = config
        self.name = config.name
        self.enabled = config.enabled

        if not self.enabled:
            logger.info(f"[{self.name}] MCP")
            return

        logger.info(f"[{self.name}] MCP")

    @abstractmethod
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        MCP

        Args:
            tool_name: 
            arguments: 

        Returns:
            
        """
        pass

    @abstractmethod
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        

        Returns:
            name, description, parameters
        """
        pass

    @abstractmethod
    def get_prompt_instruction(self, tool_name: str, **kwargs) -> str:
        """
        LLM

        Args:
            tool_name: 
            **kwargs: 

        Returns:
            
        """
        pass

    def is_enabled(self) -> bool:
        """TODO: Add docstring."""
        return self.enabled

    async def _make_sse_request(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        SSE

        Args:
            url: URL
            data: 
            headers: 

        Returns:
            SSE
        """
        events = []

        try:
            logger.info(f"[{self.name}] SSE: {'POST' if data else 'GET'} {url[:100]}...")

            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                async with client.stream(
                    'POST' if data else 'GET',
                    url,
                    json=data,
                    headers=headers or {}
                ) as response:
                    logger.info(f"[{self.name}] SSE: {response.status_code}")
                    logger.info(f"[{self.name}] SSE: {dict(response.headers)}")

                    response.raise_for_status()

                    line_count = 0
                    async for line in response.aiter_lines():
                        line_count += 1
                        if not line:
                            continue

                        logger.debug(f"[{self.name}] SSE {line_count}: {line[:200]}")

                        # SSE
                        if line.startswith('data: '):
                            data_str = line[6:].strip()

                            # 
                            if data_str in ['[DONE]', '']:
                                logger.debug(f"[{self.name}] : {data_str}")
                                continue

                            try:
                                event_data = json.loads(data_str)
                                events.append(event_data)
                                logger.debug(f"[{self.name}] : {len(events)} ")
                            except json.JSONDecodeError as je:
                                logger.warning(f"[{self.name}] SSE: {data_str[:200]}")
                                logger.warning(f"[{self.name}] JSON: {je}")
                        else:
                            # event:id:SSE
                            logger.debug(f"[{self.name}] SSE: {line[:200]}")

                    logger.info(f"[{self.name}] SSE {line_count}  {len(events)} ")

        except httpx.HTTPError as e:
            logger.error(f"[{self.name}] SSE: {e}")
            logger.error(f"[{self.name}] : {type(e).__name__}")
            logger.error(f"[{self.name}] : {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"[{self.name}] : {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
                logger.error(f"[{self.name}] : {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
            raise
        except Exception as e:
            logger.error(f"[{self.name}] SSE: {e}")
            logger.error(f"[{self.name}] : {type(e).__name__}")
            import traceback
            logger.error(f"[{self.name}] :\n{traceback.format_exc()}")
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
        HTTP

        Args:
            method: HTTP
            url: URL
            data: 
            headers: 

        Returns:
            
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
            logger.error(f"[{self.name}] HTTP: {e}")
            raise
