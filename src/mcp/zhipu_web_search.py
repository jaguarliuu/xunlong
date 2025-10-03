"""
智谱Web搜索MCP客户端

通过SSE协议与智谱Web搜索MCP服务器通信
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import json

from .base_client import BaseMCPClient, MCPClientConfig


class ZhipuWebSearchClient(BaseMCPClient):
    """智谱Web搜索MCP客户端"""

    TOOL_NAME = "zhipu_web_search"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        初始化智谱Web搜索客户端

        Args:
            api_key: 智谱API密钥
            base_url: 基础URL（可选，默认使用智谱提供的URL）
        """
        # 构建完整的URL
        if base_url is None:
            base_url = f"https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={api_key}"

        config = MCPClientConfig(
            name="智谱Web搜索",
            description="通过智谱AI提供的Web搜索服务获取实时网络信息",
            url=base_url,
            api_key=api_key,
            timeout=60,  # 搜索可能需要较长时间
            enabled=True
        )

        super().__init__(config)

        logger.info(f"[{self.name}] 智谱Web搜索MCP客户端初始化完成")

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用智谱Web搜索工具（标准MCP协议）

        MCP协议流程:
        1. 连接SSE端点，获取endpoint和sessionId
        2. 通过endpoint发送工具调用请求
        3. 接收工具返回结果

        Args:
            tool_name: 工具名称（应为"web_search"）
            arguments: 搜索参数，包含:
                - query: 搜索查询词
                - max_results: 最大结果数（可选）

        Returns:
            搜索结果
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "智谱Web搜索客户端未启用",
                "results": []
            }

        try:
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 10)

            if not query:
                return {
                    "status": "error",
                    "message": "搜索查询不能为空",
                    "results": []
                }

            logger.info(f"[{self.name}] 搜索查询: {query}, 最大结果数: {max_results}")

            # 第一步：连接SSE端点，获取endpoint和sessionId
            endpoint, session_id = await self._establish_session()

            if not endpoint or not session_id:
                return {
                    "status": "error",
                    "message": "无法建立MCP会话",
                    "results": []
                }

            logger.info(f"[{self.name}] 会话已建立: {session_id}")

            # 第二步：通过endpoint调用工具
            results = await self._call_tool_via_endpoint(
                endpoint, session_id, query, max_results
            )

            logger.info(f"[{self.name}] 搜索完成，获得 {len(results)} 个结果")

            return {
                "status": "success",
                "query": query,
                "results": results,
                "source": "zhipu_web_search"
            }

        except Exception as e:
            logger.error(f"[{self.name}] 搜索失败: {e}")
            import traceback
            logger.error(f"[{self.name}] 堆栈:\n{traceback.format_exc()}")
            return {
                "status": "error",
                "message": str(e),
                "query": arguments.get("query", ""),
                "results": []
            }

    async def _establish_session(self) -> tuple[Optional[str], Optional[str]]:
        """
        建立MCP会话，获取endpoint和sessionId

        Returns:
            (endpoint, session_id) 元组
        """
        try:
            import httpx

            logger.info(f"[{self.name}] 建立MCP会话...")

            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    'GET',
                    self.config.url,
                    headers={
                        "Accept": "text/event-stream",
                        "User-Agent": "XunLong MCP Client/1.0"
                    }
                ) as response:
                    response.raise_for_status()

                    endpoint = None
                    session_id = None

                    # 读取SSE流，获取endpoint信息
                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        logger.debug(f"[{self.name}] SSE: {line}")

                        # 查找endpoint信息
                        if line.startswith('data:'):
                            data = line[5:].strip()
                            if data.startswith('/api/mcp/web_search/message'):
                                endpoint = data
                                # 从endpoint中提取sessionId
                                if 'sessionId=' in data:
                                    session_id = data.split('sessionId=')[1].split('&')[0]
                                logger.info(f"[{self.name}] 获取endpoint: {endpoint}")
                                # 获取到endpoint后即可断开
                                break

                    return endpoint, session_id

        except Exception as e:
            logger.error(f"[{self.name}] 建立会话失败: {e}")
            return None, None

    async def _call_tool_via_endpoint(
        self,
        endpoint: str,
        session_id: str,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        通过MCP endpoint调用工具

        Args:
            endpoint: MCP endpoint路径
            session_id: 会话ID
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        import httpx
        from urllib.parse import urlparse

        # 构建完整的endpoint URL
        parsed = urlparse(self.config.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        full_endpoint = f"{base_url}{endpoint}"

        logger.info(f"[{self.name}] 调用工具: {full_endpoint[:100]}...")

        # 构建MCP工具调用请求
        tool_request = {
            "method": "tools/call",
            "params": {
                "name": "web_search",
                "arguments": {
                    "query": query,
                    "count": max_results
                }
            }
        }

        results = []

        try:
            # 将Authorization添加到endpoint URL（如果还没有）
            if 'Authorization=' not in full_endpoint and self.config.api_key:
                separator = "&" if "?" in full_endpoint else "?"
                full_endpoint = f"{full_endpoint}{separator}Authorization={self.config.api_key}"

            logger.info(f"[{self.name}] 完整endpoint: {full_endpoint[:100]}...")

            async with httpx.AsyncClient(timeout=60.0) as client:
                # 发送POST请求到endpoint
                response = await client.post(
                    full_endpoint,
                    json=tool_request,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )

                logger.info(f"[{self.name}] 响应状态: {response.status_code}")
                logger.info(f"[{self.name}] 响应头: {dict(response.headers)}")
                logger.info(f"[{self.name}] 响应内容类型: {response.headers.get('content-type')}")

                response.raise_for_status()

                # 检查响应内容
                response_text = response.text
                logger.info(f"[{self.name}] 响应文本长度: {len(response_text)}")
                logger.info(f"[{self.name}] 响应文本预览: {response_text[:500]}")

                # 如果是空响应，可能需要等待SSE流
                if not response_text.strip():
                    logger.warning(f"[{self.name}] 收到空响应，可能需要使用SSE流式接收")
                    # TODO: 实现SSE流式接收
                    return []

                result_data = response.json()

                logger.info(f"[{self.name}] 工具返回: {str(result_data)[:200]}...")

                # 解析结果
                results = self._parse_tool_response(result_data)

        except json.JSONDecodeError as je:
            logger.error(f"[{self.name}] JSON解析失败: {je}")
            logger.error(f"[{self.name}] 响应可能不是JSON格式，尝试SSE流式接收...")
            # 重新尝试使用SSE流式接收
            results = await self._call_tool_via_sse(full_endpoint, tool_request)
        except Exception as e:
            logger.error(f"[{self.name}] 调用工具失败: {e}")
            import traceback
            logger.error(f"[{self.name}] 堆栈:\n{traceback.format_exc()}")

        return results

    async def _call_tool_via_sse(
        self,
        endpoint: str,
        tool_request: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        通过SSE流式接收工具调用结果

        Args:
            endpoint: endpoint URL
            tool_request: 工具调用请求

        Returns:
            搜索结果列表
        """
        import httpx

        logger.info(f"[{self.name}] 使用SSE流式接收工具结果...")

        results = []

        try:
            # 将Authorization添加到endpoint URL（如果还没有）
            if 'Authorization=' not in endpoint and self.config.api_key:
                separator = "&" if "?" in endpoint else "?"
                endpoint = f"{endpoint}{separator}Authorization={self.config.api_key}"

            logger.info(f"[{self.name}] SSE endpoint: {endpoint[:100]}...")

            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    'POST',
                    endpoint,
                    json=tool_request,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream"
                    }
                ) as response:
                    logger.info(f"[{self.name}] SSE流响应状态: {response.status_code}")

                    response.raise_for_status()

                    # 读取SSE事件流
                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        logger.debug(f"[{self.name}] SSE行: {line[:200]}")

                        if line.startswith('data: '):
                            data_str = line[6:].strip()

                            if data_str in ['[DONE]', '']:
                                continue

                            try:
                                event_data = json.loads(data_str)
                                logger.info(f"[{self.name}] SSE事件: {str(event_data)[:200]}")

                                # 解析事件中的搜索结果
                                event_results = self._parse_tool_response(event_data)
                                if event_results:
                                    results.extend(event_results)

                            except json.JSONDecodeError as je:
                                logger.warning(f"[{self.name}] 无法解析SSE事件: {data_str[:200]}")

                    logger.info(f"[{self.name}] SSE流结束，共获得 {len(results)} 个结果")

        except Exception as e:
            logger.error(f"[{self.name}] SSE流式接收失败: {e}")
            import traceback
            logger.error(f"[{self.name}] 堆栈:\n{traceback.format_exc()}")

        return results

    def _parse_tool_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析MCP工具响应

        Args:
            response_data: MCP工具返回的数据

        Returns:
            格式化的搜索结果列表
        """
        results = []

        try:
            # MCP协议的结果可能在content字段中
            if "content" in response_data:
                content = response_data["content"]

                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            results.append(self._format_result_item(item))
                elif isinstance(content, dict):
                    results.append(self._format_result_item(content))
                elif isinstance(content, str):
                    # 可能是JSON字符串
                    try:
                        parsed = json.loads(content)
                        if isinstance(parsed, list):
                            for item in parsed:
                                results.append(self._format_result_item(item))
                    except:
                        pass

            # 或者直接在results字段中
            elif "results" in response_data:
                for item in response_data["results"]:
                    results.append(self._format_result_item(item))

        except Exception as e:
            logger.error(f"[{self.name}] 解析响应失败: {e}")

        return results

    def _parse_search_results(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        解析SSE事件流中的搜索结果

        Args:
            events: SSE事件列表

        Returns:
            格式化的搜索结果列表
        """
        results = []

        for event in events:
            # 根据MCP协议解析结果
            if "result" in event:
                result_data = event["result"]

                # 处理内容字段
                if "content" in result_data:
                    content = result_data["content"]

                    # 如果content是列表
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                # 提取文本内容
                                if "text" in item:
                                    results.append(self._format_result_item(item))
                                # 处理其他格式
                                elif "type" in item and item["type"] == "text":
                                    results.append(self._format_result_item(item))
                    # 如果content是字符串
                    elif isinstance(content, str):
                        try:
                            # 尝试解析JSON
                            content_data = json.loads(content)
                            if isinstance(content_data, list):
                                for item in content_data:
                                    results.append(self._format_result_item(item))
                        except json.JSONDecodeError:
                            # 如果不是JSON，作为纯文本处理
                            results.append({
                                "title": "搜索结果",
                                "url": "",
                                "snippet": content,
                                "source": "zhipu_web_search"
                            })

        return results

    def _format_result_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化单个搜索结果

        Args:
            item: 原始结果项

        Returns:
            格式化的结果
        """
        return {
            "title": item.get("title", item.get("text", "")[:50]),
            "url": item.get("url", item.get("link", "")),
            "snippet": item.get("snippet", item.get("text", item.get("content", ""))),
            "source": "zhipu_web_search",
            "metadata": {
                k: v for k, v in item.items()
                if k not in ["title", "url", "snippet", "text", "link", "content"]
            }
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        获取可用工具列表

        Returns:
            工具列表
        """
        return [
            {
                "name": "web_search",
                "description": "使用智谱AI的Web搜索服务搜索实时网络信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询词"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "最大结果数",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    def get_prompt_instruction(self, tool_name: str = "web_search", **kwargs) -> str:
        """
        获取提示词指令

        Args:
            tool_name: 工具名称
            **kwargs: 额外参数，可包含:
                - query: 搜索查询（可选）
                - max_results: 最大结果数（可选）

        Returns:
            提示词指令
        """
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 10)

        if query:
            return f"请使用 zhipu web search 工具搜索「{query}」，获取最新的网络信息"
        else:
            return "如果需要搜索网络信息，请使用 zhipu web search 工具"

    async def search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        便捷搜索方法

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        result = await self.call_tool(
            "web_search",
            {
                "query": query,
                "max_results": max_results
            }
        )

        return result.get("results", [])
