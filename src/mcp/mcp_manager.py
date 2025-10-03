"""
MCP管理器

管理多个MCP客户端，提供统一的搜索接口
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import os

from .base_client import BaseMCPClient
from .zhipu_web_search import ZhipuWebSearchClient


class MCPManager:
    """MCP管理器 - 管理多个MCP客户端"""

    def __init__(self):
        """初始化MCP管理器"""
        self.clients: Dict[str, BaseMCPClient] = {}
        self._initialize_clients()

    def _initialize_clients(self):
        """从环境变量初始化MCP客户端"""
        # 智谱Web搜索
        zhipu_mcp_key = os.getenv("ZHIPU_MCP_API_KEY")
        if zhipu_mcp_key:
            try:
                client = ZhipuWebSearchClient(api_key=zhipu_mcp_key)
                self.register_client("zhipu_web_search", client)
                logger.info("智谱Web搜索MCP客户端已启用")
            except Exception as e:
                logger.error(f"智谱Web搜索MCP客户端初始化失败: {e}")
        else:
            logger.info("未配置ZHIPU_MCP_API_KEY，智谱Web搜索MCP客户端未启用")

        # 这里可以继续添加其他MCP客户端
        # 例如：
        # other_mcp_key = os.getenv("OTHER_MCP_API_KEY")
        # if other_mcp_key:
        #     client = OtherMCPClient(api_key=other_mcp_key)
        #     self.register_client("other_mcp", client)

    def register_client(self, name: str, client: BaseMCPClient):
        """
        注册MCP客户端

        Args:
            name: 客户端名称
            client: MCP客户端实例
        """
        self.clients[name] = client
        logger.info(f"已注册MCP客户端: {name}")

    def get_client(self, name: str) -> Optional[BaseMCPClient]:
        """
        获取指定的MCP客户端

        Args:
            name: 客户端名称

        Returns:
            MCP客户端实例，如果不存在则返回None
        """
        return self.clients.get(name)

    def list_clients(self) -> List[str]:
        """
        列出所有已注册的MCP客户端

        Returns:
            客户端名称列表
        """
        return list(self.clients.keys())

    def list_enabled_clients(self) -> List[str]:
        """
        列出所有已启用的MCP客户端

        Returns:
            已启用的客户端名称列表
        """
        return [
            name for name, client in self.clients.items()
            if client.is_enabled()
        ]

    def has_enabled_clients(self) -> bool:
        """
        检查是否有已启用的MCP客户端

        Returns:
            如果有已启用的客户端则返回True
        """
        return len(self.list_enabled_clients()) > 0

    async def search(
        self,
        query: str,
        max_results: int = 10,
        preferred_client: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        使用MCP客户端搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数
            preferred_client: 优先使用的客户端名称

        Returns:
            搜索结果
        """
        # 如果指定了优先客户端，尝试使用它
        if preferred_client and preferred_client in self.clients:
            client = self.clients[preferred_client]
            if client.is_enabled():
                logger.info(f"使用指定的MCP客户端进行搜索: {preferred_client}")
                return await client.call_tool(
                    "web_search",
                    {"query": query, "max_results": max_results}
                )

        # 否则使用第一个可用的客户端
        enabled_clients = self.list_enabled_clients()
        if not enabled_clients:
            logger.warning("没有可用的MCP客户端")
            return {
                "status": "error",
                "message": "没有可用的MCP客户端",
                "results": []
            }

        # 使用第一个可用的客户端
        client_name = enabled_clients[0]
        client = self.clients[client_name]
        logger.info(f"使用MCP客户端进行搜索: {client_name}")

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
        使用多个MCP客户端进行搜索并合并结果

        Args:
            query: 搜索查询
            max_results: 每个客户端的最大结果数
            clients: 要使用的客户端列表，如果为None则使用所有已启用的客户端

        Returns:
            合并的搜索结果
        """
        if clients is None:
            clients = self.list_enabled_clients()

        if not clients:
            return {
                "status": "error",
                "message": "没有可用的MCP客户端",
                "results": []
            }

        all_results = []
        source_stats = {}

        # 并发搜索所有客户端
        import asyncio
        tasks = []
        for client_name in clients:
            client = self.clients.get(client_name)
            if client and client.is_enabled():
                tasks.append(self._search_with_client(client_name, query, max_results))

        # 等待所有搜索完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"客户端 {clients[i]} 搜索失败: {result}")
                continue

            if result.get("status") == "success":
                client_results = result.get("results", [])
                all_results.extend(client_results)
                source_stats[result.get("source", clients[i])] = len(client_results)

        logger.info(f"多源搜索完成，共获得 {len(all_results)} 个结果")

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
        使用指定客户端搜索

        Args:
            client_name: 客户端名称
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果
        """
        client = self.clients.get(client_name)
        if not client:
            return {
                "status": "error",
                "message": f"客户端 {client_name} 不存在",
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
        获取搜索提示词指令

        Args:
            query: 搜索查询
            client_name: 客户端名称，如果为None则使用第一个可用的客户端

        Returns:
            提示词指令
        """
        if client_name and client_name in self.clients:
            client = self.clients[client_name]
            if client.is_enabled():
                return client.get_prompt_instruction("web_search", query=query)

        # 使用第一个可用的客户端
        enabled_clients = self.list_enabled_clients()
        if enabled_clients:
            client = self.clients[enabled_clients[0]]
            return client.get_prompt_instruction("web_search", query=query)

        return f"搜索「{query}」的相关信息"


# 全局MCP管理器实例
_global_mcp_manager: Optional[MCPManager] = None


def get_mcp_manager() -> MCPManager:
    """获取全局MCP管理器实例"""
    global _global_mcp_manager
    if _global_mcp_manager is None:
        _global_mcp_manager = MCPManager()
    return _global_mcp_manager
