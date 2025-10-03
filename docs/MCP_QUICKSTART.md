# MCP 搜索服务快速开始

## 一分钟快速配置

### 1. 获取 API Key

访问 [智谱开放平台](https://open.bigmodel.cn/)，注册并获取 API Key

### 2. 配置环境变量

在项目根目录的 `.env` 文件中添加：

```bash
ZHIPU_MCP_API_KEY=your_api_key_here
```

### 3. 开始使用

```python
from src.tools.web_searcher import WebSearcher
import asyncio

async def search():
    # 初始化搜索器
    # prefer_mcp=True: 优先使用MCP搜索
    # extract_content=True: 使用浏览器抓取完整内容
    # extract_images=True: 提取图片
    searcher = WebSearcher(
        prefer_mcp=True,
        extract_content=True,
        extract_images=True
    )

    results = await searcher.search("2025年AI最新进展", max_results=5)

    for result in results:
        print(f"{result['title']} (来源: {result['source']})")
        print(f"完整内容: {result['full_content'][:200]}...")
        print(f"图片数量: {result['image_count']}")
        for img in result['images'][:3]:  # 显示前3张图片
            print(f"  - {img['url']}")

asyncio.run(search())
```

## 工作流程

系统采用 **MCP + 浏览器** 的混合方案，充分发挥两者优势：

```
第一步: MCP搜索获取URL列表
   ↓
   MCP快速搜索 → 获得标题、摘要、URL
   (无验证码、速度快)
   ↓
第二步: 浏览器访问获取完整内容
   ↓
   Playwright访问每个URL → 提取正文 + 图片
   (完整内容、支持图片)
   ↓
最终结果: 包含完整内容和图片的搜索结果
```

这种方案：
- ✅ **MCP**: 解决搜索阶段的验证码、速度问题
- ✅ **浏览器**: 解决内容抓取、图片获取问题
- ✅ **两者互补**: 既快又全

## 运行示例

```bash
# 运行使用示例
python examples/mcp_search_example.py

# 运行测试
python tests/test_mcp_search.py
```

## 核心优势

✅ **混合方案** - MCP搜索 + 浏览器抓取，优势互补
✅ **避免验证码** - MCP搜索阶段无验证码困扰
✅ **完整内容** - 浏览器访问获取完整正文
✅ **支持图片** - 自动提取文章中的图片
✅ **自动降级** - MCP 失败时自动切换到 DuckDuckGo
✅ **灵活配置** - 可选择是否抓取完整内容和图片

## 常见问题

**Q: 如果不配置 API Key 会怎样？**
A: 系统会自动使用 DuckDuckGo 进行搜索，然后用浏览器抓取完整内容，功能完全正常。

**Q: 可以只要搜索结果，不要完整内容吗？**
A: 可以，初始化时设置 `extract_content=False`，这样只获取标题和摘要，速度更快。

**Q: 图片会下载到本地吗？**
A: 不会，只提取图片URL，在生成报告时可以引用这些URL或选择下载。

**Q: 如何强制使用 DuckDuckGo？**
A: 在搜索时设置 `force_duckduckgo=True`

**Q: 支持哪些 MCP 服务？**
A: 目前支持智谱 Web 搜索，架构支持轻松扩展其他 MCP 服务。

## 详细文档

查看 [MCP 集成完整指南](./MCP_INTEGRATION_GUIDE.md) 了解更多高级功能。

## 技术架构

```
                   WebSearcher (统一搜索接口)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   第一步:搜索        第二步:抓取         结果合并
        │                 │                 │
    ┌───▼───┐         ┌───▼────┐       ┌───▼────┐
    │  MCP  │         │Playlist│       │完整内容│
    │  or   │  ────▶  │Browser │ ────▶ │+ 图片  │
    │DuckGo │         │        │       │        │
    └───┬───┘         └────────┘       └────────┘
        │
    快速获取URL        访问URL抓取        生成报告
   (无验证码)         (完整内容+图片)
```

**两阶段设计**:
1. **搜索阶段** (MCP/DuckDuckGo): 快速获取URL列表
2. **抓取阶段** (Playwright): 访问URL获取完整内容和图片

## 扩展新的 MCP 服务

只需三步：

1. 继承 `BaseMCPClient` 创建新客户端
2. 在 `MCPManager._initialize_clients()` 中注册
3. 在 `.env` 中添加配置

详见[集成指南](./MCP_INTEGRATION_GUIDE.md#mcp-服务扩展)。
