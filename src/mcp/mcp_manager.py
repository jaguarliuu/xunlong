"""
MCP

MCP
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import os

from .base_client import BaseMCPClient
from .zhipu_web_search import ZhipuWebSearchClient


class MCPManager:
    """MCP - MCP"""

    def __init__(self):
        """MCP"""
        self.clients: Dict[str, BaseMCPClient] = {}
        self._initialize_clients()

    def _initialize_clients(self):
        """MCP"""
        # Web
        zhipu_mcp_key = os.getenv("ZHIPU_MCP_API_KEY")
        if zhipu_mcp_key:
            try:
                client = ZhipuWebSearchClient(api_key=zhipu_mcp_key)
                self.register_client("zhipu_web_search", client)
                logger.info("WebMCP")
            except Exception as e:
                logger.error(f"WebMCP: {e}")
        else:
            logger.info("ZHIPU_MCP_API_KEYWebMCP")

        # MCP
        # 
        # other_mcp_key = os.getenv("OTHER_MCP_API_KEY")
        # if other_mcp_key:
        #     client = OtherMCPClient(api_key=other_mcp_key)
        #     self.register_client("other_mcp", client)

    def register_client(self, name: str, client: BaseMCPClient):
        """
        MCP

        Args:
            name: 
            client: MCP
        """
        self.clients[name] = client
        logger.info(f"MCP: {name}")

    def get_client(self, name: str) -> Optional[BaseMCPClient]:
        """
        MCP

        Args:
            name: 

        Returns:
            MCPNone
        """
        return self.clients.get(name)

    def list_clients(self) -> List[str]:
        """
        MCP

        Returns:
            
        """
        return list(self.clients.keys())

    def list_enabled_clients(self) -> List[str]:
        """
        MCP

        Returns:
            
        """
        return [
            name for name, client in self.clients.items()
            if client.is_enabled()
        ]

    def has_enabled_clients(self) -> bool:
        """
        MCP

        Returns:
            True
        """
        return len(self.list_enabled_clients()) > 0

    async def search(
        self,
        query: str,
        max_results: int = 10,
        preferred_client: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        MCP

        Args:
            query: 
            max_results: 
            preferred_client: 

        Returns:
            
        """
        # 
        if preferred_client and preferred_client in self.clients:
            client = self.clients[preferred_client]
            if client.is_enabled():
                logger.info(f"MCP: {preferred_client}")
                return await client.call_tool(
                    "web_search",
                    {"query": query, "max_results": max_results}
                )

        # 
        enabled_clients = self.list_enabled_clients()
        if not enabled_clients:
            logger.warning("MCP")
            return {
                "status": "error",
                "message": "MCP",
                "results": []
            }

        # 
        client_name = enabled_clients[0]
        client = self.clients[client_name]
        logger.info(f"MCP: {client_name}")

        return await client.call_tool(
            "web_search",
            {"query": query, "max_results": max_results}
        )

    async def multi_source_search(
        self,
        query: str,
        max_results: int = 10,
        clients: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        MCP

        Args:
            query: 
            max_results: 
            clients: None

        Returns:
            
        """
        if clients is None:
            clients = self.list_enabled_clients()

        if not clients:
            return {
                "status": "error",
                "message": "MCP",
                "results": []
            }

        all_results = []
        source_stats = {}

        # 
        import asyncio
        tasks = []
        for client_name in clients:
            client = self.clients.get(client_name)
            if client and client.is_enabled():
                tasks.append(self._search_with_client(client_name, query, max_results))

        # 
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f" {clients[i]} : {result}")
                continue

            if result.get("status") == "success":
                client_results = result.get("results", [])
                all_results.extend(client_results)
                source_stats[result.get("source", clients[i])] = len(client_results)

        logger.info(f" {len(all_results)} ")

        return {
            "status": "success",
            "query": query,
            "results": all_results,
            "source_stats": source_stats,
            "total_results": len(all_results)
        }

    async def _search_with_client(
        self,
        client_name: str,
        query: str,
        max_results: int
    ) -> Dict[str, Any]:
        """
        

        Args:
            client_name: 
            query: 
            max_results: 

        Returns:
            
        """
        client = self.clients.get(client_name)
        if not client:
            return {
                "status": "error",
                "message": f" {client_name} ",
                "results": []
            }

        return await client.call_tool(
            "web_search",
            {"query": query, "max_results": max_results}
        )

    def get_search_prompt_instruction(
        self,
        query: str,
        client_name: Optional[str] = None
    ) -> str:
        """
        

        Args:
            query: 
            client_name: None

        Returns:
            
        """
        if client_name and client_name in self.clients:
            client = self.clients[client_name]
            if client.is_enabled():
                return client.get_prompt_instruction("web_search", query=query)

        # 
        enabled_clients = self.list_enabled_clients()
        if enabled_clients:
            client = self.clients[enabled_clients[0]]
            return client.get_prompt_instruction("web_search", query=query)

        return f"{query}"


# MCP
_global_mcp_manager: Optional[MCPManager] = None


def get_mcp_manager() -> MCPManager:
    """MCP"""
    global _global_mcp_manager
    if _global_mcp_manager is None:
        _global_mcp_manager = MCPManager()
    return _global_mcp_manager
