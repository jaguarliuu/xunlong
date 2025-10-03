# 图片处理指南

## 概述

XunLong 现在支持从网页中提取图片，并智能地将图片插入到 Markdown 内容中。

## 图片处理流程

```
1. 浏览器访问URL
   ↓
2. 提取图片 (>=200x200, 最多10张/页)
   ↓
3. 智能插入到内容中
   ↓
4. 生成包含图片的Markdown报告
```

## 图片插入模式

### 1. Smart 模式（推荐，默认）

根据图片的 `alt` 文本和内容相关性智能插入：

```python
searcher = WebSearcher(image_insert_mode="smart")
```

**工作原理**:
- 提取图片 alt 中的关键词
- 在包含相关关键词的段落后插入图片
- 未匹配的图片放在末尾"其他相关图片"部分

**示例**:
```markdown
这是一段关于人工智能的文字...

![AI技术架构图](https://example.com/ai.png)
*图片尺寸: 800x600*

这是另一段文字...

## 其他相关图片
### 1. 深度学习
![深度学习](https://example.com/dl.png)
```

### 2. Bottom 模式（附录）

所有图片放在内容末尾：

```python
searcher = WebSearcher(image_insert_mode="bottom")
```

**适用场景**: 学术报告、正式文档

**效果**:
```markdown
正文内容...

## 相关图片
### 1. 图片1
![图片1](url1)
*尺寸: 800x600*

### 2. 图片2
![图片2](url2)
*尺寸: 1024x768*
```

### 3. Top 模式

所有图片放在开头：

```python
searcher = WebSearcher(image_insert_mode="top")
```

**适用场景**: 快速浏览、图片为主的内容

### 4. Distribute 模式

图片均匀分布在段落之间：

```python
searcher = WebSearcher(image_insert_mode="distribute")
```

**适用场景**: 图文并茂的文章

### 5. None 模式

不插入图片，但保留图片数据：

```python
searcher = WebSearcher(image_insert_mode="none")
```

**适用场景**: 只需要图片URL列表，手动处理

## 使用示例

### 基础使用

```python
from src.tools.web_searcher import WebSearcher
import asyncio

async def search_with_images():
    searcher = WebSearcher(
        extract_content=True,
        extract_images=True,
        image_insert_mode="smart"  # 智能插入
    )

    results = await searcher.search("人工智能发展", max_results=5)

    for result in results:
        print(f"标题: {result['title']}")
        print(f"图片数: {result['image_count']}")
        print(f"图片已插入: {result.get('images_inserted', False)}")
        print(f"内容预览:\n{result['full_content'][:500]}\n")

asyncio.run(search_with_images())
```

### 自定义处理

```python
from src.utils.image_processor import ImageProcessor

# 手动处理图片插入
content = "原始内容..."
images = [
    {"url": "...", "alt": "图片1", "width": 800, "height": 600},
    {"url": "...", "alt": "图片2", "width": 1024, "height": 768}
]

# 使用不同模式
enhanced_content = ImageProcessor.insert_images_to_content(
    content,
    images,
    mode="smart"
)
```

## 图片数据结构

每张图片包含以下信息：

```python
{
    "url": "https://example.com/image.jpg",  # 图片URL
    "alt": "图片描述",                        # alt文本
    "width": 800,                            # 宽度
    "height": 600                            # 高度
}
```

## 图片过滤规则

为了保证质量，系统会自动过滤：

1. **尺寸过小**: 小于 200x200 的图片（通常是图标）
2. **Base64图片**: `data:` 开头的内嵌图片
3. **数量限制**: 每篇文章最多 10 张图片

## 最佳实践

### 1. 根据场景选择模式

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| 研究报告 | `smart` | 图片与内容自动关联 |
| 学术论文 | `bottom` | 图片作为附录更正式 |
| 新闻稿 | `distribute` | 图文并茂 |
| 快速浏览 | `top` | 图片优先展示 |

### 2. 处理图片加载失败

生成 HTML 时，图片 URL 可能失效。建议：

```python
# 选项1: 下载图片到本地（TODO）
# 选项2: 使用图片代理服务
# 选项3: 在 HTML 中添加 onerror 处理
```

### 3. 优化图片显示

在 HTML 模板中可以添加：

```html
<style>
img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
```

## 常见问题

**Q: 为什么有些网页没有提取到图片？**
A: 可能原因：
1. 网页使用懒加载（需要滚动才加载）
2. 图片太小被过滤了
3. 图片是通过 JavaScript 动态生成的

**Q: 如何下载图片到本地？**
A: 目前只提取 URL，可以使用以下代码下载：

```python
import httpx
from pathlib import Path

async def download_image(url: str, save_path: Path):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        save_path.write_bytes(response.content)
```

**Q: 图片 URL 过期怎么办？**
A: 建议在生成报告时立即下载图片或使用图片代理服务。

## 技术实现

### 图片提取

使用 Playwright 的 JavaScript 执行：

```javascript
const images = Array.from(document.querySelectorAll('img'));
return images
    .filter(img => {
        const width = img.naturalWidth || img.width;
        const height = img.naturalHeight || img.height;
        return width >= 200 && height >= 200;
    })
    .map(img => ({
        src: img.src,
        alt: img.alt || '',
        width: img.naturalWidth || img.width,
        height: img.naturalHeight || img.height
    }))
    .slice(0, 10);
```

### 智能插入算法

```python
# 1. 提取图片 alt 中的关键词
keywords = [w for w in re.findall(r'\w+', alt) if len(w) > 2]

# 2. 检查段落是否包含关键词
if any(kw.lower() in para_lower for kw in keywords):
    # 插入图片
    insert_image()
```

## 未来优化

- [ ] 支持图片去重
- [ ] 支持图片下载到本地
- [ ] 支持图片压缩和优化
- [ ] 支持 OCR 提取图片中的文字
- [ ] 使用 LLM 进行更智能的图片-内容匹配
- [ ] 支持图片标注和高亮

## 总结

图片处理功能让 XunLong 生成的报告更加丰富和专业。通过智能插入算法，图片能够自动关联到相关内容，提升报告的可读性和信息密度。
