# 混合搜索架构 - MCP + 浏览器

## 设计理念

XunLong 采用**两阶段混合搜索架构**，充分发挥 MCP 服务和浏览器自动化的各自优势：

### 🎯 核心问题

传统搜索方案的痛点：

1. **纯浏览器方案 (DuckDuckGo + Playwright)**
   - ❌ 经常遇到验证码
   - ❌ 启动浏览器慢
   - ❌ 网络波动影响大
   - ❌ 搜索结果被广告污染

2. **纯 MCP 方案**
   - ❌ 只能获取摘要，无法获取完整内容
   - ❌ 无法提取图片
   - ❌ 内容深度不够

### ✅ 混合解决方案

将搜索过程分为两个阶段，各司其职：

```
┌─────────────────────────────────────────────────────────────┐
│                    混合搜索架构                              │
└─────────────────────────────────────────────────────────────┘

阶段一: 搜索阶段（获取URL列表）
┌─────────────────────────────────────────────┐
│  MCP 搜索 (优先) 或 DuckDuckGo (降级)        │
│                                             │
│  ✓ 快速获取搜索结果                          │
│  ✓ 无验证码困扰                              │
│  ✓ 获得: 标题、摘要、URL                     │
└──────────────┬──────────────────────────────┘
               │
               ▼
阶段二: 内容抓取阶段（访问URL获取完整信息）
┌─────────────────────────────────────────────┐
│  Playwright 浏览器自动化                     │
│                                             │
│  ✓ 访问每个URL                              │
│  ✓ 提取完整正文内容                          │
│  ✓ 提取文章中的图片                          │
│  ✓ 获得: full_content + images              │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  最终结果: 包含完整内容和图片的搜索结果       │
│                                             │
│  • title (标题)                             │
│  • url (链接)                               │
│  • snippet (摘要 - 来自MCP)                 │
│  • full_content (完整内容 - 来自浏览器)      │
│  • images[] (图片列表 - 来自浏览器)          │
│  • source (来源标识)                         │
└─────────────────────────────────────────────┘
```

## 技术实现

### 1. WebSearcher 类设计

```python
class WebSearcher:
    def __init__(
        self,
        prefer_mcp: bool = True,      # 优先使用MCP
        extract_content: bool = True,  # 是否抓取完整内容
        extract_images: bool = True    # 是否提取图片
    ):
        self.mcp_manager = get_mcp_manager()
        self.duckduckgo_searcher = DuckDuckGoSearcher()
        # ...

    async def search(self, query: str, max_results: int = 10):
        """
        两阶段搜索流程
        """
        # 阶段一: 获取搜索结果（URL列表）
        results = await self._get_search_results(query, max_results)

        # 阶段二: 抓取完整内容（如果需要）
        if self.extract_content:
            results = await self._fetch_full_content_with_browser(results)

        return results
```

### 2. 阶段一：搜索阶段

**优先级策略**:
1. 如果配置了 MCP (如智谱 Web 搜索)，优先使用 MCP
2. 如果 MCP 失败或未配置，自动降级到 DuckDuckGo
3. 强制使用 DuckDuckGo: 设置 `force_duckduckgo=True`

**输出结果**:
```python
{
    "title": "文章标题",
    "url": "https://example.com/article",
    "snippet": "文章摘要...",
    "source": "zhipu_web_search"  # 或 "duckduckgo"
}
```

### 3. 阶段二：内容抓取阶段

使用 Playwright 无头浏览器访问每个 URL：

#### 内容提取策略

```python
# 优先级选择器列表
content_selectors = [
    "article",           # HTML5 语义化标签
    "main",              # 主要内容区
    "[role='main']",     # ARIA 标识
    ".content",          # 常见类名
    ".article-content",
    ".post-content",
    "#content",
    ".main-content"
]
```

#### 图片提取策略

```python
# 过滤条件
- 最小尺寸: 200x200 像素（过滤小图标）
- 最大数量: 每篇文章最多10张图片
- 跳过 data: URL（base64图片）
- 处理相对路径，转换为绝对URL
```

**输出结果**:
```python
{
    "title": "文章标题",
    "url": "https://example.com/article",
    "snippet": "文章摘要...",
    "source": "zhipu_web_search",

    # 新增字段
    "full_content": "完整正文内容...",
    "has_full_content": True,
    "images": [
        {
            "url": "https://example.com/img1.jpg",
            "alt": "图片描述",
            "width": 800,
            "height": 600
        },
        # ...
    ],
    "image_count": 5
}
```

## 使用场景

### 场景 1: 研究报告生成

```python
searcher = WebSearcher(
    prefer_mcp=True,
    extract_content=True,   # 需要完整内容
    extract_images=True     # 需要配图
)

results = await searcher.search("AI最新进展", max_results=5)

# 结果可以直接用于生成带图片的研究报告
for result in results:
    # 生成报告章节
    report_section = f"""
    ## {result['title']}

    {result['full_content']}

    {"![图片](" + result['images'][0]['url'] + ")" if result['images'] else ""}
    """
```

### 场景 2: 快速搜索（仅需摘要）

```python
searcher = WebSearcher(
    prefer_mcp=True,
    extract_content=False,  # 不需要完整内容
    extract_images=False
)

results = await searcher.search("Python教程", max_results=10)
# 快速返回，只有标题和摘要
```

### 场景 3: 两步式搜索

```python
# 第一步：快速搜索大量候选
quick_searcher = WebSearcher(extract_content=False)
candidates = await quick_searcher.search("机器学习", max_results=20)

# 第二步：用户选择后再抓取完整内容
selected_urls = [candidates[0], candidates[3], candidates[5]]

full_searcher = WebSearcher(extract_content=True, extract_images=True)
detailed = await full_searcher._fetch_full_content_with_browser(selected_urls)
```

## 性能优化

### 1. 搜索阶段优化

- **MCP优先**: API调用，延迟 < 2秒
- **无需浏览器**: 节省资源和时间
- **并发搜索**: 支持多源MCP同时搜索

### 2. 抓取阶段优化

```python
# 使用无头模式
browser = await p.chromium.launch(headless=True)

# 设置合理超时
page.set_default_timeout(30000)  # 30秒

# 等待策略
await page.goto(url, wait_until="domcontentloaded")  # 不等待所有资源
```

### 3. 错误处理

- **优雅降级**: MCP失败 → DuckDuckGo
- **容错机制**: 单个URL抓取失败不影响其他结果
- **保留原始数据**: 即使抓取失败，仍保留摘要信息

## 配置选项

### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prefer_mcp` | bool | True | 是否优先使用MCP搜索 |
| `extract_content` | bool | True | 是否抓取完整内容 |
| `extract_images` | bool | True | 是否提取图片 |

### 搜索参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | str | - | 搜索查询 |
| `max_results` | int | 10 | 最大结果数 |
| `force_duckduckgo` | bool | False | 强制使用DuckDuckGo |
| `fetch_full_content` | bool | None | 覆盖初始化配置 |

## 最佳实践

### ✅ 推荐做法

1. **配置 MCP API Key** - 避免验证码，提升速度
2. **根据需求选择模式** - 不总是需要完整内容
3. **合理设置 max_results** - 内容抓取耗时，不要过多
4. **异步调用** - 充分利用异步特性

### ❌ 避免做法

1. **不配置 MCP 就大量搜索** - 容易触发验证码
2. **总是抓取完整内容** - 如果只需要URL列表，关闭抓取
3. **同步调用** - 会阻塞事件循环
4. **忽略错误** - 检查 `has_full_content` 和 `fetch_error`

## 扩展性

### 添加新的内容提取器

```python
# 可以为特定网站定制内容提取逻辑
def extract_from_medium(page):
    # Medium 特定的选择器
    return await page.query_selector("article").inner_text()

def extract_from_zhihu(page):
    # 知乎特定的选择器
    return await page.query_selector(".Post-RichTextContainer").inner_text()
```

### 支持更多 MCP 服务

只需在 `MCPManager` 中注册新的 MCP 客户端：

```python
# 添加新的 MCP 服务
class OtherMCPClient(BaseMCPClient):
    # 实现接口
    pass

# 在 MCPManager 中注册
manager.register_client("other_mcp", OtherMCPClient(api_key))
```

## 总结

混合搜索架构通过两阶段设计，完美结合了 MCP 和浏览器自动化的优势：

| 特性 | MCP 搜索 | 浏览器抓取 | 混合方案 |
|------|----------|-----------|---------|
| 速度 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| 内容完整性 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 图片支持 | ❌ | ✅ | ✅ |
| 验证码风险 | ✅ | ❌ | ✅ |
| 资源消耗 | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**最终效果**: ⭐⭐⭐⭐⭐ 既快又全！
