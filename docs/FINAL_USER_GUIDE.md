# DeepSearch 用户使用指南

## 🎉 欢迎使用 DeepSearch！

DeepSearch 是一个智能搜索与内容抽取工具，能够自动搜索网页、抽取正文内容、提取图片信息并生成截图。

## 🚀 快速开始

### 1. 安装和设置
```bash
# 一键安装（推荐）
python quick_start.py

# 或手动安装
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. 基础测试
```bash
# 测试安装是否成功
python basic_test.py
```

### 3. 第一次搜索
```bash
# 简单搜索
python main.py search "Python"

# 查看详细过程
python main.py search "Python" --verbose
```

## 💻 CLI 使用方法

### 基本命令
```bash
# 基本搜索
python main.py search "查询词"

# 指定结果数量
python main.py search "机器学习" --topk 5

# 保存结果到文件
python main.py search "AI" --output results.json

# 显示详细日志
python main.py search "Python" --verbose
```

### 高级选项
```bash
# 使用无头模式（后台运行，不显示浏览器）
python main.py search "查询词" --headless

# 自定义截图目录
python main.py search "查询词" --shots-dir ./my_screenshots

# 组合使用
python main.py search "深度学习" \
  --topk 10 \
  --output deep_learning.json \
  --shots-dir ./dl_shots \
  --verbose
```

### 参数说明
- `query`: 搜索查询词（必需）
- `--topk, -k`: 抓取结果数量（默认: 5）
- `--headless/--no-headless`: 浏览器模式（默认: 显示浏览器）
- `--output, -o`: 输出JSON文件路径
- `--shots-dir`: 截图保存目录（默认: ./shots）
- `--engine, -e`: 搜索引擎（默认: duckduckgo）
- `--verbose, -v`: 显示详细日志

## 🌐 API 使用方法

### 启动API服务
```bash
python run_api.py
```
服务将在 `http://localhost:8000` 启动

### API 端点

#### 搜索接口
```http
GET /search?q=查询词&k=5&engine=duckduckgo&headless=false
```

**参数**：
- `q`: 搜索查询词（必需）
- `k`: 抓取数量（1-20，默认: 5）
- `engine`: 搜索引擎（默认: duckduckgo）
- `headless`: 是否无头模式（默认: false）

**示例**：
```bash
# 基本搜索
curl "http://localhost:8000/search?q=Python&k=3"

# 中文搜索
curl "http://localhost:8000/search?q=人工智能&k=2"

# 无头模式搜索
curl "http://localhost:8000/search?q=机器学习&k=5&headless=true"
```

#### 其他接口
```bash
# 健康检查
curl "http://localhost:8000/health"

# 获取配置
curl "http://localhost:8000/config"

# 服务信息
curl "http://localhost:8000/"
```

### API 文档
访问 `http://localhost:8000/docs` 查看完整的API文档

## 📊 输出格式

### JSON 结构
```json
{
  "query": "Python",
  "engine": "duckduckgo",
  "items": [
    {
      "url": "https://www.python.org/",
      "title": "Welcome to Python.org",
      "text": "正文内容...",
      "length": 1413,
      "screenshot_path": "./shots/6bd7e4a1b937.png",
      "og_image_url": "https://www.python.org/static/opengraph-icon-200x200.png",
      "first_image_url": "https://www.python.org/static/img/python-logo.png",
      "error": null
    }
  ],
  "total_found": 1,
  "success_count": 1,
  "error_count": 0,
  "execution_time": 20.33
}
```

### 字段说明
- `query`: 搜索查询词
- `engine`: 使用的搜索引擎
- `items`: 搜索结果列表
  - `url`: 页面URL
  - `title`: 页面标题
  - `text`: 抽取的正文内容
  - `length`: 正文字符数
  - `screenshot_path`: 截图文件路径
  - `og_image_url`: Open Graph 图片URL
  - `first_image_url`: 页面首个图片URL
  - `error`: 错误信息（如果有）
- `total_found`: 找到的结果总数
- `success_count`: 成功处理的数量
- `error_count`: 处理失败的数量
- `execution_time`: 执行时间（秒）

## ⚙️ 配置选项

### 环境变量
```bash
# 浏览器模式
export BROWSER_HEADLESS=false         # true=无头模式, false=显示浏览器

# 搜索配置
export DEEPSEARCH_TOPK=5              # 默认抓取数量
export DEEPSEARCH_SEARCH_ENGINE=duckduckgo  # 搜索引擎
export DEEPSEARCH_SHOTS_DIR=./shots   # 截图保存目录

# 性能配置
export DEEPSEARCH_BROWSER_TIMEOUT=30000      # 浏览器超时(毫秒)
export DEEPSEARCH_PAGE_WAIT_TIME=3000        # 页面等待时间(毫秒)
```

### 配置文件
修改 `src/config.py` 中的默认值来自定义配置。

## 📝 使用示例

### 1. 学术研究
```bash
# 搜索学术论文相关内容
python main.py search "machine learning papers 2024" --topk 10 --output research.json
```

### 2. 技术学习
```bash
# 搜索编程教程
python main.py search "Python web development tutorial" --topk 5 --verbose
```

### 3. 新闻资讯
```bash
# 搜索最新新闻
python main.py search "AI news today" --topk 8 --shots-dir ./news_shots
```

### 4. 中文内容
```bash
# 中文搜索
python main.py search "人工智能发展趋势" --topk 6 --output ai_trends.json
```

## 🔧 故障排除

### 常见问题

#### 1. 搜索结果为空
**原因**: 网络问题或DuckDuckGo访问受限
**解决**: 
- 检查网络连接
- 尝试使用有头模式: `--no-headless`
- 检查防火墙设置

#### 2. 浏览器启动失败
**原因**: Playwright浏览器未安装
**解决**: 
```bash
python -m playwright install chromium
```

#### 3. 权限错误
**原因**: 截图目录权限不足
**解决**: 
```bash
mkdir shots
chmod 755 shots
```

#### 4. 内存不足
**原因**: 系统内存不够
**解决**: 
- 减少抓取数量: `--topk 3`
- 使用无头模式: `--headless`
- 关闭其他程序

### 调试方法

#### 启用详细日志
```bash
python main.py search "查询词" --verbose
```

#### 使用有头模式观察
```bash
python main.py search "查询词" --no-headless
```

#### 运行测试脚本
```bash
python basic_test.py
python test_fixed_search.py
```

## 🚀 高级用法

### 批量搜索
```python
# 使用Python脚本批量搜索
import asyncio
from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline

async def batch_search():
    config = DeepSearchConfig(topk=3)
    pipeline = DeepSearchPipeline(config)
    
    queries = ["Python", "JavaScript", "Go"]
    for query in queries:
        result = await pipeline.search(query)
        print(f"{query}: {result.success_count} 个结果")

asyncio.run(batch_search())
```

### API 客户端
```python
import requests

def search_api(query, topk=5):
    response = requests.get(
        "http://localhost:8000/search",
        params={"q": query, "k": topk}
    )
    return response.json()

result = search_api("Python tutorial", 3)
print(f"找到 {result['total_found']} 个结果")
```

## 📞 获取帮助

### 命令行帮助
```bash
python main.py --help
python main.py search --help
```

### 在线文档
- 项目README: `README.md`
- 部署指南: `DEPLOYMENT_GUIDE.md`
- 项目总结: `PROJECT_SUMMARY.md`

### 测试和验证
```bash
python basic_test.py          # 基础功能测试
python test_fixed_search.py   # 搜索功能测试
python examples/basic_usage.py  # 使用示例
```

## 🎯 最佳实践

1. **首次使用**: 先运行 `python basic_test.py` 确保环境正常
2. **调试问题**: 使用 `--verbose` 和 `--no-headless` 参数
3. **批量处理**: 适当控制 `--topk` 数量避免过载
4. **结果保存**: 使用 `--output` 参数保存重要搜索结果
5. **网络环境**: 确保能正常访问DuckDuckGo网站

---

## 🎉 开始使用吧！

现在您已经掌握了DeepSearch的使用方法，开始您的智能搜索之旅吧！

```bash
# 立即开始
python main.py search "您感兴趣的话题" --verbose
```

如有问题，请参考故障排除部分或运行测试脚本进行诊断。