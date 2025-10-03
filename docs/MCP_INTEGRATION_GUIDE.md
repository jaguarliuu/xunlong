# MCP 搜索服务集成指南

## 概述

XunLong 现已支持 MCP (Model Context Protocol) 搜索服务集成，提供多源搜索能力。目前支持智谱 Web 搜索 MCP 服务，未来可扩展支持更多 MCP 服务。

## 架构设计

### 核心组件

1. **BaseMCPClient** (`src/mcp/base_client.py`)
   - MCP 客户端抽象基类
   - 提供 SSE/HTTP 请求支持
   - 定义标准的工具调用接口

2. **ZhipuWebSearchClient** (`src/mcp/zhipu_web_search.py`)
   - 智谱 Web 搜索 MCP 客户端实现
   - 支持 SSE 协议通信
   - 自动解析和格式化搜索结果

3. **MCPManager** (`src/mcp/mcp_manager.py`)
   - MCP 客户端管理器
   - 支持多客户端注册和管理
   - 提供统一的搜索接口
   - 支持多源搜索和结果合并

4. **WebSearcher** (`src/tools/web_searcher.py`)
   - 集成 MCP 搜索的 Web 搜索器
   - 优先使用 MCP 服务
   - 自动降级到 DuckDuckGo

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# 智谱 Web 搜索 MCP 服务
ZHIPU_MCP_API_KEY=your_api_key_here
```

**获取 API Key:**
- 访问 [智谱开放平台](https://open.bigmodel.cn/)
- 注册账号并创建应用
- 获取 API Key（支持 API Key 或 AK.SK 格式）

### 配置优先级

1. 如果配置了 `ZHIPU_MCP_API_KEY`，系统将优先使用智谱 Web 搜索
2. 如果 MCP 搜索失败或未配置，自动降级到 DuckDuckGo
3. 可通过 `force_duckduckgo=True` 强制使用 DuckDuckGo

## 使用方法

### 1. 基础搜索

```python
from src.tools.web_searcher import WebSearcher
import asyncio

async def search_example():
    # 创建搜索器（优先使用 MCP）
    searcher = WebSearcher(prefer_mcp=True)

    # 执行搜索
    results = await searcher.search(
        query="2025年10月3日 AIGC领域新闻",
        max_results=10
    )

    # 处理结果
    for result in results:
        print(f"标题: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"来源: {result['source']}")  # 'zhipu_web_search' 或 'duckduckgo'
        print()

asyncio.run(search_example())
```

### 2. 强制使用特定搜索源

```python
# 强制使用 DuckDuckGo
results = await searcher.search(
    query="搜索查询",
    force_duckduckgo=True
)
```

### 3. 直接使用 MCP Manager

```python
from src.mcp.mcp_manager import get_mcp_manager

async def mcp_search_example():
    manager = get_mcp_manager()

    # 检查是否有启用的客户端
    if manager.has_enabled_clients():
        # 执行搜索
        result = await manager.search(
            query="搜索查询",
            max_results=10
        )

        print(f"状态: {result['status']}")
        print(f"结果数: {len(result['results'])}")
```

### 4. 多源搜索（高级功能）

```python
async def multi_source_search():
    manager = get_mcp_manager()

    # 使用所有已启用的客户端搜索
    result = await manager.multi_source_search(
        query="搜索查询",
        max_results=5
    )

    # 查看来源统计
    print(f"总结果数: {result['total_results']}")
    print(f"来源统计: {result['source_stats']}")

    # 结果已自动合并
    for item in result['results']:
        print(f"{item['title']} (来源: {item['source']})")
```

### 5. 获取提示词指令（用于 LLM）

```python
# 生成给 LLM 的搜索指令
instruction = manager.get_search_prompt_instruction(
    query="2025年10月3日 AIGC领域新闻"
)
print(instruction)
# 输出: "请使用 zhipu web search 工具搜索「2025年10月3日 AIGC领域新闻」，获取最新的网络信息"
```

## MCP 服务扩展

### 添加新的 MCP 客户端

1. **创建客户端类**

```python
# src/mcp/your_mcp_client.py
from .base_client import BaseMCPClient, MCPClientConfig
from typing import Dict, Any, List

class YourMCPClient(BaseMCPClient):
    def __init__(self, api_key: str):
        config = MCPClientConfig(
            name="Your MCP Service",
            description="Your service description",
            url=f"https://your-service.com/mcp?key={api_key}",
            api_key=api_key,
            enabled=True
        )
        super().__init__(config)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # 实现工具调用逻辑
        pass

    def get_available_tools(self) -> List[Dict[str, Any]]:
        # 返回可用工具列表
        return [...]

    def get_prompt_instruction(self, tool_name: str, **kwargs) -> str:
        # 返回提示词指令
        return "..."
```

2. **注册到 MCP Manager**

```python
# src/mcp/mcp_manager.py
def _initialize_clients(self):
    # ... 现有代码 ...

    # 添加新的 MCP 客户端
    your_mcp_key = os.getenv("YOUR_MCP_API_KEY")
    if your_mcp_key:
        from .your_mcp_client import YourMCPClient
        client = YourMCPClient(api_key=your_mcp_key)
        self.register_client("your_mcp", client)
```

3. **更新环境变量配置**

在 `.env.example` 中添加：

```bash
# Your MCP Service
YOUR_MCP_API_KEY=your_api_key_here
```

## 测试

### 运行测试脚本

```bash
# 确保已配置环境变量
python tests/test_mcp_search.py
```

### 测试内容

1. MCP 管理器初始化
2. 智谱 Web 搜索功能
3. 集成的 Web 搜索器
4. 提示词指令生成

## 优势

### 相比 DuckDuckGo 的优势

1. **无需浏览器** - 不需要启动 Playwright/Chromium
2. **更快速度** - API 直接返回，无需渲染网页
3. **更稳定** - 避免验证码、网络波动等问题
4. **更准确** - MCP 服务通常提供结构化的搜索结果
5. **成本可控** - API 调用可计费，避免浏览器资源消耗

### 架构优势

1. **可扩展** - 轻松添加新的 MCP 服务
2. **可降级** - MCP 失败时自动切换到 DuckDuckGo
3. **统一接口** - 无需修改上层调用代码
4. **多源支持** - 可同时使用多个搜索源并合并结果

## 常见问题

### Q: MCP 搜索失败怎么办？

A: 系统会自动降级到 DuckDuckGo，确保搜索功能始终可用。

### Q: 如何选择使用哪个搜索源？

A: 默认优先使用 MCP，也可以：
- 设置 `prefer_mcp=False` 优先使用 DuckDuckGo
- 设置 `force_duckduckgo=True` 强制使用 DuckDuckGo

### Q: 如何禁用 MCP 搜索？

A: 不配置 `ZHIPU_MCP_API_KEY` 即可，系统会自动使用 DuckDuckGo。

### Q: 支持哪些 MCP 服务？

A: 目前支持：
- 智谱 Web 搜索 (SSE)

未来计划支持：
- 其他厂商的 MCP 搜索服务
- 自定义 MCP 服务

## 技术细节

### SSE 协议支持

智谱 MCP 使用 SSE (Server-Sent Events) 协议：

```python
# 自动处理 SSE 流
events = await self._make_sse_request(
    url=self.config.url,
    data=request_data,
    headers={"Accept": "text/event-stream"}
)
```

### 结果格式化

所有搜索结果统一格式化为：

```python
{
    "title": "结果标题",
    "url": "结果URL",
    "snippet": "结果摘要",
    "source": "来源标识 (zhipu_web_search/duckduckgo)",
    "metadata": {}  # 额外元数据（可选）
}
```

## 更新日志

### v1.0.0 (2025-10-03)
- ✅ 实现 MCP 客户端基础架构
- ✅ 集成智谱 Web 搜索 MCP 服务
- ✅ 实现 MCP Manager 多源管理
- ✅ 集成到现有 WebSearcher
- ✅ 添加自动降级机制
- ✅ 提供完整测试脚本

## 贡献

欢迎贡献新的 MCP 客户端实现！请遵循以下步骤：

1. Fork 项目
2. 创建 MCP 客户端类（继承 `BaseMCPClient`）
3. 注册到 `MCPManager`
4. 添加测试用例
5. 更新文档
6. 提交 Pull Request
