# 第 1 章 · 使用 Playwright 驱动 DuckDuckGo

本章开启“XunLong 内部拆解”系列教程，主要讲解项目目前的搜索流程，以及为什么选择控制浏览器而不是调用爬虫类 API。

---

## 1. 为什么选择无头浏览器？

XunLong 的搜索栈基于 Playwright（参考 `src/tools/web_searcher.py`）。协调器会通过 `src/browser.py` 启动 Chromium，自动化 DuckDuckGo 搜索，再复用同一浏览器访问每个结果页面。

我们选择通过浏览器控制的主要原因有以下三点：

1. **动态内容无处不在**  
   大量站点会在初始请求后再异步加载正文，或者通过脚本隐藏关键内容。无头浏览器会等待网络空闲并滚动页面（`BrowserManager.wait_for_page_load`），确保 DOM 中包含写作智能体需要的完整文本。

2. **更一致的提取与截图体验**  
   我们采集到的 HTML 会用于生成 Markdown/HTML/PDF，有时还需要截图。使用同一个 Chromium 实例完成搜索与内容提取，可以保证渲染环境一致，并通过 `browser.py:take_screenshot` 拿到高质量截图。

3. **服务限制与覆盖范围**  
   Firecrawl 等第三方聚合接口虽然很好用，但也存在一些限制：
   - 只能覆盖公共网络的一部分；
   - 需要额外的厂商依赖，并受请求额度限制；
   - 对于内嵌媒体或轻度付费墙内容，Playwright 模拟真实用户更容易获取。

我们自己控制 DuckDuckGo 的自动化流程，可以灵活调整限速、缓存与降级策略，同时不依赖额外的 API Key。

---

## 2. XunLong 的搜索流程概览

整体搜索流程由多个专门模块串联而成：

| 步骤 | 代码位置 | 职责 |
| ---- | ---- | -------------- |
| **1. 任务规划** | `src/agents/task_decomposer.py` | 将用户查询（包含上传的文档上下文）拆解为更聚焦的子任务。 |
| **2. 浏览器管控** | `src/browser.py` | 启动 Playwright，配置有头/无头模式，并加入常用反检测设置。 |
| **3. DuckDuckGo 自动化** | `src/tools/web_searcher.py` | 提交查询、应用日期过滤、抓取结果卡片，并按需截图。 |
| **4. 页面内容提取** | `src/pipeline.py` + `src/tools/web_searcher.py::_fetch_full_content_with_browser` | 访问每个结果，等待脚本加载，提取正文、图片和元数据。 |
| **5. 排序与去重** | `src/agents/deep_searcher.py` | 合并结果、优先考虑用户上传的文档、去重并按相关度/时间排序。 |
| **6. 存储与复用** | `src/storage/search_storage.py` | 持久化中间 JSON、可读摘要及截图，供迭代与导出使用。 |

由于整个流程复用同一个 Playwright 会话，DuckDuckGo 与目标站点的 User-Agent、语言环境、Cookie 状态保持一致。

---

## 3. 最小化示例 (`chapter1_playwright_duckduckgo.py`)

The tutorial branch includes a self-contained example at:

```
examples/tutorial/chapter1_playwright_duckduckgo.py
```

This script shows the bare minimum needed to drive DuckDuckGo, grab result titles & URLs, and close the browser politely.

### Prerequisites

```bash
pip install playwright
playwright install chromium
```

### Run the demo

```bash
python examples/tutorial/chapter1_playwright_duckduckgo.py "AI industry trends"
```

You should see the top results printed to the console.

---

## 4. 下一步计划

Chapter 2 will dive deeper into the extraction step—waiting for lazy-loaded content, handling paywall stubs, and piping everything into XunLong’s storage layer. 敬请期待！

