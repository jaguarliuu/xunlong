# HTML转换系统使用指南

## 📖 概述

XunLong HTML转换系统提供了强大的Markdown到HTML转换功能，支持三种主要输出格式：

- **文档（Document）** - 研究报告、技术文档、学术论文
- **小说（Fiction）** - 小说、故事、文学作品
- **PPT（Presentation）** - 演示文稿、培训材料、报告展示

## 🌟 核心特性

### 1. 多模板支持

每种输出格式都提供了多个精美模板：

- **文档模板**：`academic`（学术）、`technical`（技术）、`simple`（简洁）
- **小说模板**：`novel`（小说）、`ebook`（电子书）、`magazine`（杂志）
- **PPT模板**：基于 Reveal.js、Impress.js 等主流框架

### 2. 主题系统

支持多种配色主题：
- `light` - 浅色主题（适合白天阅读）
- `dark` - 深色主题（护眼模式）
- `sepia` - 复古主题（温暖纸张效果）
- 自定义主题

### 3. 智能特性

- **自动章节提取** - 智能识别文档结构
- **目录生成** - 自动生成可跳转的目录
- **统计信息** - 字数、章节数等统计
- **响应式设计** - 适配各种屏幕尺寸
- **打印优化** - 支持高质量打印输出

### 4. PPT特有功能

- **智能分页** - 自动将长内容分成合适的幻灯片
- **布局优化** - 根据内容类型自动选择最佳布局
- **转场效果** - 支持多种过渡动画
- **多框架支持** - Reveal.js、Impress.js、Remark.js

## 🚀 快速开始

### 基础用法

```python
from src.agents.html import DocumentHTMLAgent

# 创建转换智能体
agent = DocumentHTMLAgent()

# 转换内容
html = agent.convert_to_html(
    content="# 我的文档\n\n这是内容...",
    metadata={'title': '我的文档', 'author': '张三'},
    template='academic',
    theme='light',
    output_path='output/my_document.html'
)
```

### 文档转换示例

```python
from src.agents.html import DocumentHTMLAgent
from pathlib import Path

# 创建智能体
agent = DocumentHTMLAgent()

# 准备内容
content = """
# 研究报告

## 摘要
本文介绍了...

## 1. 引言
研究背景...

## 2. 方法
我们采用了...
"""

# 元数据
metadata = {
    'title': '研究报告',
    'author': '研究团队',
    'date': '2025-10-02',
    'keywords': ['研究', '分析']
}

# 转换
html = agent.convert_to_html(
    content=content,
    metadata=metadata,
    template='academic',  # 使用学术模板
    theme='light',
    output_path=Path('output/report.html')
)
```

### 小说转换示例

```python
from src.agents.html import FictionHTMLAgent

# 创建智能体
agent = FictionHTMLAgent()

# 小说内容
content = """
# 推理小说标题

## 第一章 开始

故事从这里开始...

## 第二章 转折

意外发生了...
"""

# 转换
html = agent.convert_to_html(
    content=content,
    metadata={
        'title': '推理小说',
        'author': '作者名',
        'genre': '推理',
        'synopsis': '这是一个悬疑推理故事...'
    },
    template='novel',
    theme='sepia',  # 使用复古主题
    output_path='output/novel.html'
)
```

### PPT转换示例

```python
from src.agents.html import PPTHTMLAgent

# 创建智能体（指定框架）
agent = PPTHTMLAgent(framework='reveal')

# PPT内容（使用 --- 分隔幻灯片）
content = """
# 演示标题

---

## 第一页

- 要点1
- 要点2
- 要点3

---

## 第二页

这是内容...
"""

# 转换
html = agent.convert_to_html(
    content=content,
    metadata={
        'title': '我的演示',
        'author': '演讲者'
    },
    template='default',
    theme='sky',  # Reveal.js主题
    output_path='output/presentation.html'
)
```

## 🎨 模板和主题管理

### 使用模板注册中心

```python
from src.agents.html import get_template_registry

# 获取注册中心
registry = get_template_registry()

# 列出所有文档模板
templates = registry.list_templates('document')
for t in templates:
    print(f"{t.name}: {t.description}")

# 列出所有主题
themes = registry.list_themes('document')
for t in themes:
    print(f"{t.name}: {t.display_name}")

# 获取推荐模板
recommended = registry.recommend_template(
    agent_type='document',
    content='研究论文内容...',
    metadata={'type': 'academic'}
)
```

### 自定义模板

创建自定义模板文件 `templates/html/document/my_template.html`：

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        /* 自定义样式 */
        body { font-family: Arial; }
        {{ custom_css }}
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    {% for section in sections %}
    <section>
        <h2>{{ section.title }}</h2>
        <div>{{ section.content | markdown | safe }}</div>
    </section>
    {% endfor %}
</body>
</html>
```

注册模板：

```python
from src.agents.html import TemplateInfo, get_template_registry

registry = get_template_registry()

# 注册自定义模板
template = TemplateInfo(
    name="my_template",
    agent_type="document",
    file_path="my_template.html",
    description="我的自定义模板",
    supports_themes=['light', 'dark']
)
registry.register_template(template)
```

### 自定义主题

```python
from src.agents.html import ThemeInfo, get_template_registry

registry = get_template_registry()

# 创建自定义主题
theme = ThemeInfo(
    name="ocean",
    display_name="海洋主题",
    description="清新的海洋配色",
    css_vars={
        "--bg-color": "#e8f4f8",
        "--text-color": "#1e3a5f",
        "--primary-color": "#0077be",
        "--secondary-color": "#00a8cc"
    },
    applies_to=['document', 'fiction']
)
registry.register_theme(theme)

# 保存配置
registry.save_config()
```

## 🎯 高级功能

### 文档特有功能

```python
from src.agents.html import DocumentHTMLAgent

agent = DocumentHTMLAgent()

# 添加引用
content_with_citations = agent.add_citation(
    content=content,
    citations=[
        {
            'title': '论文标题',
            'author': '作者',
            'year': '2025',
            'url': 'https://...'
        }
    ]
)

# 添加附录
content_with_appendix = agent.add_appendix(
    content=content,
    appendices=[
        {
            'title': '数据表',
            'content': '附录内容...'
        }
    ]
)
```

### 小说特有功能

```python
from src.agents.html import FictionHTMLAgent

agent = FictionHTMLAgent()

# 分页（用于生成电子书）
pages = agent.split_into_pages(
    content=long_content,
    chars_per_page=1000
)

# 添加封面
metadata = agent.add_book_cover(
    metadata={'title': '小说'},
    cover_url='https://example.com/cover.jpg'
)
```

### PPT特有功能

```python
from src.agents.html import PPTHTMLAgent

agent = PPTHTMLAgent(framework='reveal')

# 解析内容
parsed = agent.parse_content(content, metadata)

# 添加转场效果
slides = agent.add_transition(
    slides=parsed['slides'],
    transition='zoom'
)

# 添加背景
slides = agent.add_background(
    slides=slides,
    background='#ff0000',
    slide_numbers=[1, 2, 3]  # 只为前三页添加
)

# 生成目录页
outline = agent.generate_outline_slide(slides)

# 重新生成HTML
html = agent.convert_to_html(content, metadata)
```

## 📋 模板变量参考

### 文档模板可用变量

- `{{ title }}` - 文档标题
- `{{ author }}` - 作者
- `{{ date }}` - 日期
- `{{ abstract }}` - 摘要
- `{{ keywords }}` - 关键词列表
- `{{ sections }}` - 章节列表
- `{{ toc }}` - 目录
- `{{ stats }}` - 统计信息
- `{{ theme }}` - 主题名称
- `{{ custom_css }}` - 自定义CSS

### 小说模板可用变量

- `{{ title }}` - 书名
- `{{ author }}` - 作者
- `{{ genre }}` - 类型
- `{{ synopsis }}` - 简介
- `{{ chapters }}` - 章节列表
- `{{ stats }}` - 统计信息

### PPT模板可用变量

- `{{ title }}` - 演示标题
- `{{ author }}` - 作者
- `{{ date }}` - 日期
- `{{ slides }}` - 幻灯片列表
- `{{ framework }}` - 使用的框架

## 🔧 与XunLong系统集成

### 在报告生成中使用

```python
from src.agents.report.report_coordinator import CollaborativeReportCoordinator
from src.agents.html import DocumentHTMLAgent

# 生成报告
coordinator = CollaborativeReportCoordinator(...)
report_md = await coordinator.generate_report(query)

# 转换为HTML
html_agent = DocumentHTMLAgent()
html = html_agent.convert_to_html(
    content=report_md,
    metadata={'title': query},
    template='academic',
    output_path='output/report.html'
)
```

### 在小说创作中使用

```python
from src.agents.fiction.fiction_outline_generator import FictionOutlineGenerator
from src.agents.html import FictionHTMLAgent

# 生成小说
# ... 小说创作代码 ...

# 转换为HTML
html_agent = FictionHTMLAgent()
html = html_agent.convert_to_html(
    content=fiction_content,
    metadata={
        'title': '小说标题',
        'author': 'AI作家'
    },
    template='novel',
    theme='sepia',
    output_path='output/novel.html'
)
```

## 💡 最佳实践

### 1. 选择合适的模板

- 学术论文、研究报告 → `academic` 模板
- 技术文档、API文档 → `technical` 模板
- 小说、故事 → `novel` 模板
- 商务演示 → `business` PPT模板

### 2. 主题选择建议

- 白天阅读 → `light` 主题
- 夜间阅读 → `dark` 主题
- 长时间阅读 → `sepia` 主题

### 3. 内容组织

**文档**：
- 使用明确的标题层级（# ## ###）
- 添加摘要和关键词
- 合理使用列表和代码块

**小说**：
- 使用 `##` 标记章节
- 保持段落适中长度
- 添加章节标题

**PPT**：
- 使用 `---` 分隔幻灯片
- 每页内容简洁（不超过5个要点）
- 合理使用图片和代码

### 4. 性能优化

- 大文档考虑分章节生成
- PPT幻灯片数量建议不超过50页
- 图片使用外链而非嵌入

## 🐛 故障排除

### 模板未找到

```python
# 检查模板是否存在
agent = DocumentHTMLAgent()
is_valid = agent.validate_template('academic')
print(f"模板有效: {is_valid}")

# 列出可用模板
templates = agent.list_available_templates()
print(f"可用模板: {templates}")
```

### 中文乱码

确保：
1. 源文件使用UTF-8编码
2. HTML模板包含 `<meta charset="UTF-8">`

### Markdown渲染问题

需要安装markdown库：
```bash
pip install markdown
```

## 📚 参考资源

- [Jinja2模板文档](https://jinja.palletsprojects.com/)
- [Reveal.js文档](https://revealjs.com/)
- [Markdown语法](https://www.markdownguide.org/)

## 🔄 更新日志

### v1.0.0 (2025-10-02)
- ✅ 实现基础HTML转换功能
- ✅ 支持文档、小说、PPT三种格式
- ✅ 模板和主题系统
- ✅ 智能模板推荐
- ✅ PPT智能分页

---

*本文档最后更新：2025-10-02*
