"""
WebMCP

SSEWebMCP
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import json

from .base_client import BaseMCPClient, MCPClientConfig


class ZhipuWebSearchClient(BaseMCPClient):
    """WebMCP"""

    TOOL_NAME = "zhipu_web_search"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Web

        Args:
            api_key: API
            base_url: URLURL
        """
        # URL
        if base_url is None:
            base_url = f"https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={api_key}"

        config = MCPClientConfig(
            name="Web",
            description="AIWeb",
            url=base_url,
            api_key=api_key,
            timeout=60,  # 
            enabled=True
        )

        super().__init__(config)

        logger.info(f"[{self.name}] WebMCP")

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        WebMCP

        MCP:
        1. SSEendpointsessionId
        2. endpoint
        3. 

        Args:
            tool_name: "web_search"
            arguments: :
                - query: 
                - max_results: 

        Returns:
            
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "Web",
                "results": []
            }

        try:
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 10)

            if not query:
                return {
                    "status": "error",
                    "message": "",
                    "results": []
                }

            logger.info(f"[{self.name}] : {query}, : {max_results}")

            # SSEendpointsessionId
            endpoint, session_id = await self._establish_session()

            if not endpoint or not session_id:
                return {
                    "status": "error",
                    "message": "MCP",
                    "results": []
                }

            logger.info(f"[{self.name}] : {session_id}")

            # endpoint
            results = await self._call_tool_via_endpoint(
                endpoint, session_id, query, max_results
            )

            logger.info(f"[{self.name}]  {len(results)} ")

            return {
                "status": "success",
                "query": query,
                "results": results,
                "source": "zhipu_web_search"
            }

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            import traceback
            logger.error(f"[{self.name}] :\n{traceback.format_exc()}")
            return {
                "status": "error",
                "message": str(e),
                "query": arguments.get("query", ""),
                "results": []
            }

    async def _establish_session(self) -> tuple[Optional[str], Optional[str]]:
        """
        MCPendpointsessionId

        Returns:
            (endpoint, session_id) 
        """
        try:
            import httpx

            logger.info(f"[{self.name}] MCP...")

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

                    # SSEendpoint
                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        logger.debug(f"[{self.name}] SSE: {line}")

                        # endpoint
                        if line.startswith('data:'):
                            data = line[5:].strip()
                            if data.startswith('/api/mcp/web_search/message'):
                                endpoint = data
                                # endpointsessionId
                                if 'sessionId=' in data:
                                    session_id = data.split('sessionId=')[1].split('&')[0]
                                logger.info(f"[{self.name}] endpoint: {endpoint}")
                                # endpoint
                                break

                    return endpoint, session_id

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return None, None

    async def _call_tool_via_endpoint(
        self,
        endpoint: str,
        session_id: str,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        MCP endpoint

        Args:
            endpoint: MCP endpoint
            session_id: ID
            query: 
            max_results: 

        Returns:
            
        """
        import httpx
        from urllib.parse import urlparse

        # endpoint URL
        parsed = urlparse(self.config.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        full_endpoint = f"{base_url}{endpoint}"

        logger.info(f"[{self.name}] : {full_endpoint[:100]}...")

        # MCP
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
            # Authorizationendpoint URL
            if 'Authorization=' not in full_endpoint and self.config.api_key:
                separator = "&" if "?" in full_endpoint else "?"
                full_endpoint = f"{full_endpoint}{separator}Authorization={self.config.api_key}"

            logger.info(f"[{self.name}] endpoint: {full_endpoint[:100]}...")

            async with httpx.AsyncClient(timeout=60.0) as client:
                # POSTendpoint
                response = await client.post(
                    full_endpoint,
                    json=tool_request,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )

                logger.info(f"[{self.name}] : {response.status_code}")
                logger.info(f"[{self.name}] : {dict(response.headers)}")
                logger.info(f"[{self.name}] : {response.headers.get('content-type')}")

                response.raise_for_status()

                # 
                response_text = response.text
                logger.info(f"[{self.name}] : {len(response_text)}")
                logger.info(f"[{self.name}] : {response_text[:500]}")

                # SSE
                if not response_text.strip():
                    logger.warning(f"[{self.name}] SSE")
                    # TODO: SSE
                    return []

                result_data = response.json()

                logger.info(f"[{self.name}] : {str(result_data)[:200]}...")

                # 
                results = self._parse_tool_response(result_data)

        except json.JSONDecodeError as je:
            logger.error(f"[{self.name}] JSON: {je}")
            logger.error(f"[{self.name}] JSONSSE...")
            # SSE
            results = await self._call_tool_via_sse(full_endpoint, tool_request)
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            import traceback
            logger.error(f"[{self.name}] :\n{traceback.format_exc()}")

        return results

    async def _call_tool_via_sse(
        self,
        endpoint: str,
        tool_request: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        SSE

        Args:
            endpoint: endpoint URL
            tool_request: 

        Returns:
            
        """
        import httpx

        logger.info(f"[{self.name}] SSE...")

        results = []

        try:
            # Authorizationendpoint URL
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
                    logger.info(f"[{self.name}] SSE: {response.status_code}")

                    response.raise_for_status()

                    # SSE
                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        logger.debug(f"[{self.name}] SSE: {line[:200]}")

                        if line.startswith('data: '):
                            data_str = line[6:].strip()

                            if data_str in ['[DONE]', '']:
                                continue

                            try:
                                event_data = json.loads(data_str)
                                logger.info(f"[{self.name}] SSE: {str(event_data)[:200]}")

                                # 
                                event_results = self._parse_tool_response(event_data)
                                if event_results:
                                    results.extend(event_results)

                            except json.JSONDecodeError as je:
                                logger.warning(f"[{self.name}] SSE: {data_str[:200]}")

                    logger.info(f"[{self.name}] SSE {len(results)} ")

        except Exception as e:
            logger.error(f"[{self.name}] SSE: {e}")
            import traceback
            logger.error(f"[{self.name}] :\n{traceback.format_exc()}")

        return results

    def _parse_tool_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        MCP

        Args:
            response_data: MCP

        Returns:
            
        """
        results = []

        try:
            # MCPcontent
            if "content" in response_data:
                content = response_data["content"]

                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            results.append(self._format_result_item(item))
                elif isinstance(content, dict):
                    results.append(self._format_result_item(content))
                elif isinstance(content, str):
                    # JSON
                    try:
                        parsed = json.loads(content)
                        if isinstance(parsed, list):
                            for item in parsed:
                                results.append(self._format_result_item(item))
                    except:
                        pass

            # results
            elif "results" in response_data:
                for item in response_data["results"]:
                    results.append(self._format_result_item(item))

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")

        return results

    def _parse_search_results(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        SSE

        Args:
            events: SSE

        Returns:
            
        """
        results = []

        for event in events:
            # MCP
            if "result" in event:
                result_data = event["result"]

                # 
                if "content" in result_data:
                    content = result_data["content"]

                    # content
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                # 
                                if "text" in item:
                                    results.append(self._format_result_item(item))
                                # 
                                elif "type" in item and item["type"] == "text":
                                    results.append(self._format_result_item(item))
                    # content
                    elif isinstance(content, str):
                        try:
                            # JSON
                            content_data = json.loads(content)
                            if isinstance(content_data, list):
                                for item in content_data:
                                    results.append(self._format_result_item(item))
                        except json.JSONDecodeError:
                            # JSON
                            results.append({
                                "title": "",
                                "url": "",
                                "snippet": content,
                                "source": "zhipu_web_search"
                            })

        return results

    def _format_result_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        

        Args:
            item: 

        Returns:
            
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
        

        Returns:
            
        """
        return [
            {
                "name": "web_search",
                "description": "AIWeb",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": ""
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    def get_prompt_instruction(self, tool_name: str = "web_search", **kwargs) -> str:
        """
        

        Args:
            tool_name: 
            **kwargs: :
                - query: 
                - max_results: 

        Returns:
            
        """
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 10)

        if query:
            return f" zhipu web search {query}"
        else:
            return " zhipu web search "

    async def search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        

        Args:
            query: 
            max_results: 

        Returns:
            
        """
        result = await self.call_tool(
            "web_search",
            {
                "query": query,
                "max_results": max_results
            }
        )

        return result.get("results", [])
