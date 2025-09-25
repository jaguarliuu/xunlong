# DeepSearch MVP-1 功能开发说明书

## 目标功能
实现 DeepSearch 工具的第一部分：  
**使用 Playwright 打开搜索引擎 → 抓取前 5 条结果 → 抽取正文 + 首图 + 截图**。

## 功能要求
1. **可配置运行模式**
   - 前台模式（有头浏览器，方便观察调试）
   - 后台模式（无头浏览器，适合服务端运行）
   - 模式由配置项或环境变量控制，例如：
     - `BROWSER_HEADLESS=true` → 无头模式
     - `BROWSER_HEADLESS=false` → 有头模式

2. **搜索引擎可配置**
   - 默认：DuckDuckGo
   - 预留扩展：Google、Bing
   - 搜索器应设计为可插拔模块，便于扩展

3. **处理流程**
   - 输入用户的查询词 `query`
   - 在指定搜索引擎执行搜索
   - 抓取前 5 条（可配置 Top-K）
   - 对每条结果执行：
     - 打开页面
     - 抽取正文（去掉导航/广告，保留主体内容）
     - 提取首图（优先 `og:image`，其次首个 `<img>` 标签）
     - 保存首屏截图到本地 `./shots`
     - 返回标题 + URL + 正文摘要 + 图像信息

4. **输出**
   - 结构化 JSON 数据
   - 字段示例：
     ```json
     {
       "query": "El Niño 2023 impacts Asia",
       "engine": "duckduckgo",
       "items": [
         {
           "url": "https://example.com/article",
           "title": "Climate Impacts of El Niño",
           "text": "正文摘要...",
           "length": 1234,
           "screenshot_path": "shots/abc123.png",
           "og_image_url": "https://example.com/img.png",
           "first_image_url": "https://example.com/img2.png"
         }
       ]
     }
     ```

5. **可扩展性**
   - 模块化设计：`config / searcher / browser / extractor / pipeline`
   - 为后续加入 rerank、图片理解、多模态搜索预留接口

---

## 技术栈

### Python 版本
- Python 3.10+

### 依赖库（固定版本号）
```txt
playwright==1.47.0
trafilatura==1.8.0
beautifulsoup4==4.12.3
pydantic==2.8.2
loguru==0.7.2
typer==0.12.3       # 可选，用于 CLI
fastapi==0.115.0    # 可选，用于 REST API
uvicorn==0.30.0     # 可选，用于启动服务
tenacity==8.3.0     # 可选，用于重试机制

## 实现方案

### 模块设计
1. 配置管理

使用 pydantic.BaseModel 定义配置类

支持环境变量、默认值、命令行参数

核心配置项：

headless: bool → 控制是否显示浏览器

search_engine: str → duckduckgo / google / bing

topk: int → 默认 5

shots_dir: str → 截图保存目录

output_json_path: str → 输出文件路径（可选）

2. 搜索器模块

定义抽象基类 BaseSearcher

实现 DuckDuckGoSearcher，通过 Playwright 抓取搜索结果链接

预留 GoogleSearcher、BingSearcher

3. 浏览器控制模块

封装 Playwright 上下文管理：

打开浏览器（headless/headful）

设置代理（可选）

执行滚动加载 & 等待网络空闲

截图（保存到 ./shots）

4. 内容抽取模块

使用 BeautifulSoup 提取标题、og:image、首图

使用 trafilatura 提取正文主体

返回统一数据结构（Pydantic 模型）

5. 主流程（Pipeline）

输入 query → 搜索器获取前 K 条链接

对每个链接：

打开页面

抽取正文、首图、截图

生成 PageExtract 对象

汇总为 SearchResult JSON 输出

可选：写入文件 / 返回 API 响应

6. 输出结果

默认返回 JSON

CLI 模式：支持 --out 参数保存到文件

API 模式：提供 /search?q=xxx&k=5 接口返回 JSON