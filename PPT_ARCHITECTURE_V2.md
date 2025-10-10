# XunLong PPT生成系统 - 多页HTML架构设计 v2.0

## 一、架构概述

### 1.1 核心理念
**从"单HTML全内容"转向"多HTML页面 + 导航系统"**

- **旧架构**：一个巨大的HTML包含所有幻灯片，通过JavaScript控制显示
- **新架构**：每页独立HTML，通过导航系统串联，类似真实PPT

### 1.2 优势分析

#### 技术优势
- ✅ **页面独立性**：每页可单独生成、修改、导出
- ✅ **加载性能**：按需加载，不需要一次性加载所有内容
- ✅ **容错能力**：单页失败不影响其他页面
- ✅ **并行生成**：可并发生成多个页面
- ✅ **灵活布局**：每页可使用不同布局模板
- ✅ **易于调试**：单页问题易于定位

#### 用户体验优势
- ✅ **快速预览**：可快速跳转到任意页
- ✅ **独立分享**：可分享单个幻灯片
- ✅ **打印友好**：每页独立打印
- ✅ **PDF导出**：易于转换为PDF

#### 开发维护优势
- ✅ **模板复用**：每种页面类型有专门模板
- ✅ **版本控制**：页面级别的版本管理
- ✅ **A/B测试**：可测试不同页面布局

---

## 二、文件组织结构

### 2.1 目录结构
```
storage/{project_id}/
├── ppt/
│   ├── index.html                 # 导航入口页（可选）
│   ├── slides/
│   │   ├── slide_01_cover.html    # 封面页
│   │   ├── slide_02_toc.html      # 目录页
│   │   ├── slide_03_content.html  # 内容页1
│   │   ├── slide_04_content.html  # 内容页2
│   │   ├── slide_05_chart.html    # 图表页
│   │   ├── slide_06_comparison.html # 对比页
│   │   └── slide_XX_summary.html  # 总结页
│   ├── assets/
│   │   ├── styles/
│   │   │   └── common.css        # 通用样式
│   │   ├── scripts/
│   │   │   └── navigation.js     # 导航逻辑
│   │   └── images/               # 图片资源
│   ├── data/
│   │   └── slides_metadata.json  # 幻灯片元数据
│   └── manifest.json             # PPT配置文件
```

### 2.2 文件命名规范
```
slide_{序号}_{类型}.html

序号：01, 02, 03... (两位数字，方便排序)
类型：
  - cover      封面
  - toc        目录
  - content    内容页
  - chart      图表页
  - comparison 对比页
  - timeline   时间线
  - summary    总结页
```

---

## 三、核心组件设计

### 3.1 幻灯片基础模板

#### 3.1.1 标准页面结构
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{slide_title}</title>

    <!-- 外部依赖 -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet"/>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

    <!-- 内联样式 -->
    <style>
        /* PPT标准尺寸 */
        body {
            position: relative;
            width: 1280px;
            height: 720px;
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .slide-container {
            width: 100%;
            height: 100%;
            position: relative;
        }

        /* 页面特定样式 */
        {custom_styles}
    </style>

    <!-- AIGC元数据 -->
    <meta name="UserComment" content='{aigc_metadata}' />
    <!-- PPT页面元数据 -->
    <meta name="slide-index" content="{slide_number}">
    <meta name="slide-type" content="{slide_type}">
    <meta name="total-slides" content="{total_slides}">
</head>
<body>
    <div class="slide-container">
        <!-- 页面内容 -->
        {slide_content}

        <!-- 页码指示器 -->
        <div class="slide-footer">
            <span class="page-number">{current_page} / {total_pages}</span>
        </div>

        <!-- AI水印 -->
        <div class="ai-watermark">XunLong AI 生成</div>

        <!-- 导航控制（可选） -->
        <div class="navigation-controls" style="display: none;">
            <button id="prev-slide" class="nav-btn">←</button>
            <button id="next-slide" class="nav-btn">→</button>
        </div>
    </div>

    <!-- 页面脚本 -->
    <script>
        {page_script}

        // 导航功能
        const slideMetadata = {
            current: {slide_number},
            total: {total_slides},
            prev: '{prev_slide_path}',
            next: '{next_slide_path}'
        };

        // 键盘导航
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' && slideMetadata.prev) {
                window.location.href = slideMetadata.prev;
            } else if (e.key === 'ArrowRight' && slideMetadata.next) {
                window.location.href = slideMetadata.next;
            }
        });
    </script>
</body>
</html>
```

### 3.2 页面类型模板

#### A. 封面页模板 (cover)
```python
{
    "layout": "centered",
    "elements": {
        "title": "主标题",
        "subtitle": "副标题",
        "author": "作者/机构",
        "date": "日期",
        "decorations": ["icons", "gradient_background"]
    }
}
```

#### B. 目录页模板 (toc)
```python
{
    "layout": "list",
    "elements": {
        "title": "目录",
        "sections": [
            {"number": "01", "title": "章节1", "slide_link": "slide_03"},
            {"number": "02", "title": "章节2", "slide_link": "slide_05"}
        ]
    }
}
```

#### C. 内容页模板 (content)
```python
{
    "layout": "title_and_content",
    "elements": {
        "title": "页面标题",
        "content_type": "bullet_points | paragraph | two_columns",
        "content": {...}
    }
}
```

#### D. 图表页模板 (chart)
```python
{
    "layout": "chart_focused",
    "elements": {
        "title": "图表标题",
        "chart_type": "bar | line | pie | dual_axis",
        "chart_data": {...},
        "insights": ["洞察1", "洞察2"]
    }
}
```

---

## 四、导航系统设计

### 4.1 导航入口页 (index.html)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>PPT导航 - {ppt_title}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .slide-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .slide-card {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .slide-card:hover {
            border-color: #2E8B57;
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .slide-preview {
            width: 100%;
            height: 150px;
            background: #f5f5f5;
            border-radius: 4px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>{ppt_title}</h1>
    <p>总计 {total_slides} 页 | 生成时间: {generation_time}</p>

    <div class="slide-grid">
        <!-- 动态生成幻灯片卡片 -->
        {slide_cards}
    </div>

    <div class="controls">
        <button onclick="window.location.href='slides/slide_01_cover.html'">
            开始演示
        </button>
        <button onclick="exportAllSlides()">导出PDF</button>
    </div>

    <script>
        function exportAllSlides() {
            // TODO: 实现PDF导出
            alert('PDF导出功能待实现');
        }
    </script>
</body>
</html>
```

### 4.2 全屏演示模式

创建一个 `presenter.html` 支持全屏演示：

```html
<!DOCTYPE html>
<html>
<head>
    <title>演示模式</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: black;
        }

        iframe {
            width: 100vw;
            height: 100vh;
            border: none;
        }

        .presenter-controls {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            display: flex;
            gap: 10px;
        }

        .presenter-controls button {
            padding: 10px 20px;
            background: rgba(255,255,255,0.9);
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <iframe id="slide-frame" src="slides/slide_01_cover.html"></iframe>

    <div class="presenter-controls">
        <button onclick="prevSlide()">← 上一页</button>
        <span id="slide-counter">1 / 15</span>
        <button onclick="nextSlide()">下一页 →</button>
        <button onclick="toggleFullscreen()">全屏</button>
    </div>

    <script src="assets/scripts/presenter.js"></script>
</body>
</html>
```

---

## 五、数据结构设计

### 5.1 幻灯片元数据 (slides_metadata.json)

```json
{
  "ppt_title": "AI技术发展报告",
  "total_slides": 15,
  "generation_time": "2025-10-09 22:00:00",
  "theme": "business",
  "color_scheme": {
    "primary": "#2E8B57",
    "secondary": "#FF8C00",
    "accent": "#E6E6FA"
  },
  "slides": [
    {
      "slide_id": "slide_01",
      "slide_number": 1,
      "file_name": "slide_01_cover.html",
      "type": "cover",
      "title": "封面 - AI技术发展报告",
      "template": "cover_modern",
      "prev": null,
      "next": "slide_02_toc.html"
    },
    {
      "slide_id": "slide_02",
      "slide_number": 2,
      "file_name": "slide_02_toc.html",
      "type": "toc",
      "title": "目录",
      "template": "toc_standard",
      "prev": "slide_01_cover.html",
      "next": "slide_03_content.html"
    },
    {
      "slide_id": "slide_03",
      "slide_number": 3,
      "file_name": "slide_03_content.html",
      "type": "content",
      "title": "AI技术概述",
      "template": "content_bullet_points",
      "section": "第一章",
      "prev": "slide_02_toc.html",
      "next": "slide_04_chart.html"
    }
  ]
}
```

### 5.2 PPT配置文件 (manifest.json)

```json
{
  "version": "2.0",
  "generator": "XunLong AI",
  "format": "multi-html-slides",
  "output_config": {
    "slide_size": {
      "width": 1280,
      "height": 720,
      "aspect_ratio": "16:9"
    },
    "navigation": {
      "keyboard_enabled": true,
      "touch_enabled": true,
      "auto_play": false
    },
    "export_formats": ["html", "pdf"],
    "accessibility": {
      "screen_reader": true,
      "high_contrast": false
    }
  },
  "dependencies": {
    "tailwind": "https://cdn.tailwindcss.com",
    "fontawesome": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
    "d3": "https://d3js.org/d3.v7.min.js",
    "echarts": "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"
  }
}
```

---

## 六、生成流程设计

### 6.1 PPT生成工作流

```
1. 任务分解
   ↓
2. 内容收集与分析
   ↓
3. 生成PPT大纲
   ├─ 确定幻灯片数量
   ├─ 分配章节页数
   └─ 确定每页类型
   ↓
4. 并行生成幻灯片
   ├─ slide_01 (封面)
   ├─ slide_02 (目录)
   ├─ slide_03-14 (内容)
   └─ slide_15 (总结)
   ↓
5. 生成导航文件
   ├─ index.html
   ├─ presenter.html
   └─ slides_metadata.json
   ↓
6. 资源整合
   └─ 复制通用资源到assets/
   ↓
7. 质量检查
   ├─ 验证所有页面可访问
   ├─ 检查导航链接
   └─ 测试图表渲染
   ↓
8. 输出完整PPT包
```

### 6.2 单页生成逻辑

```python
async def generate_single_slide(
    slide_config: Dict,
    template: str,
    content: Dict,
    metadata: Dict
) -> str:
    """
    生成单个幻灯片页面

    Args:
        slide_config: 幻灯片配置 (序号、类型等)
        template: 模板名称
        content: 页面内容数据
        metadata: 元数据 (总页数、导航链接等)

    Returns:
        生成的HTML字符串
    """
    # 1. 选择模板
    template_engine = get_slide_template(template)

    # 2. 处理内容
    processed_content = process_slide_content(content, slide_config['type'])

    # 3. 生成图表 (如果需要)
    if slide_config['type'] == 'chart':
        chart_code = generate_chart_code(processed_content['chart_data'])
        processed_content['chart_script'] = chart_code

    # 4. 注入导航信息
    navigation = {
        'current': slide_config['slide_number'],
        'total': metadata['total_slides'],
        'prev': slide_config.get('prev'),
        'next': slide_config.get('next')
    }

    # 5. 渲染模板
    html = template_engine.render(
        content=processed_content,
        navigation=navigation,
        theme=metadata['theme'],
        aigc_metadata=generate_aigc_metadata()
    )

    return html
```

---

## 七、模板系统设计

### 7.1 模板目录结构

```
src/agents/html/templates/ppt/
├── layouts/
│   ├── cover.html           # 封面布局
│   ├── toc.html             # 目录布局
│   ├── content.html         # 标准内容布局
│   ├── chart.html           # 图表布局
│   ├── comparison.html      # 对比布局
│   └── summary.html         # 总结布局
├── components/
│   ├── header.html          # 页头组件
│   ├── footer.html          # 页脚组件
│   ├── navigation.html      # 导航组件
│   └── watermark.html       # 水印组件
├── themes/
│   ├── business.css         # 商务主题
│   ├── academic.css         # 学术主题
│   ├── creative.css         # 创意主题
│   └── minimal.css          # 简约主题
└── base.html                # 基础模板
```

### 7.2 模板继承示例

**base.html (基础模板)**
```jinja2
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}{{ slide_title }}{% endblock %}</title>

    {% include 'components/dependencies.html' %}

    <style>
        {% include 'themes/' + theme + '.css' %}
        {% block custom_styles %}{% endblock %}
    </style>

    {% include 'components/metadata.html' %}
</head>
<body>
    <div class="slide-container">
        {% block content %}{% endblock %}

        {% include 'components/footer.html' %}
        {% include 'components/watermark.html' %}
        {% include 'components/navigation.html' %}
    </div>

    <script>
        {% block scripts %}{% endblock %}
        {% include 'components/navigation.js' %}
    </script>
</body>
</html>
```

**cover.html (封面模板)**
```jinja2
{% extends "base.html" %}

{% block custom_styles %}
.cover-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    background: linear-gradient(135deg, {{ theme.primary }} 0%, {{ theme.secondary }} 100%);
}
{% endblock %}

{% block content %}
<div class="cover-container">
    <h1 class="main-title">{{ content.title }}</h1>
    <p class="subtitle">{{ content.subtitle }}</p>
    <div class="author-info">
        <span>{{ content.author }}</span>
        <span>{{ content.date }}</span>
    </div>
</div>
{% endblock %}
```

---

## 八、实现计划

### Phase 1: 核心架构 (Week 1-2)
- [ ] 设计多页HTML生成引擎
- [ ] 实现基础模板系统
- [ ] 创建幻灯片元数据管理

### Phase 2: 模板库 (Week 3-4)
- [ ] 开发6种基础布局模板
- [ ] 实现3种主题样式
- [ ] 集成图表组件

### Phase 3: 导航系统 (Week 5)
- [ ] 实现导航入口页
- [ ] 开发演示模式
- [ ] 添加键盘/触摸导航

### Phase 4: 增强功能 (Week 6)
- [ ] PDF导出功能
- [ ] 幻灯片预览缩略图
- [ ] 自动化测试

### Phase 5: 优化与发布 (Week 7-8)
- [ ] 性能优化
- [ ] 文档完善
- [ ] 用户测试

---

## 九、技术优势对比

| 特性 | 旧架构 (单HTML) | 新架构 (多HTML) |
|------|---------------|---------------|
| 文件大小 | 大 (>1MB) | 小 (每页<200KB) |
| 加载速度 | 慢 (一次性) | 快 (按需) |
| 内存占用 | 高 | 低 |
| 调试难度 | 难 | 易 |
| 并行生成 | 否 | 是 |
| 独立导出 | 难 | 易 |
| 模板复用 | 低 | 高 |
| 可扩展性 | 一般 | 优秀 |

---

## 十、最佳实践

### 10.1 性能优化
1. **懒加载图表**: 仅在需要时初始化D3/ECharts
2. **资源CDN**: 使用CDN加速库文件加载
3. **CSS内联**: 关键样式内联，减少请求
4. **图片优化**: 压缩图片，使用WebP格式

### 10.2 可访问性
1. **语义化HTML**: 使用正确的标签结构
2. **键盘导航**: 支持Tab/方向键
3. **屏幕阅读器**: 添加ARIA标签
4. **高对比度模式**: 提供可选主题

### 10.3 开发规范
1. **命名约定**: 统一的文件和类名规范
2. **代码注释**: 每个模板添加用途说明
3. **版本控制**: 使用语义化版本号
4. **单元测试**: 测试每个模板渲染

---

## 十一、示例使用

```python
from src.agents.ppt import MultiSlidePPTCoordinator

# 初始化PPT生成器
ppt_gen = MultiSlidePPTCoordinator(
    llm_manager=llm_manager,
    prompt_manager=prompt_manager
)

# 生成PPT
result = await ppt_gen.generate_ppt_v3(
    topic="AI技术发展趋势",
    search_results=search_results,
    config={
        "slide_count": 15,
        "theme": "business",
        "include_charts": True,
        "navigation_mode": "full"  # full | minimal | none
    }
)

# 输出结构
# storage/{project_id}/ppt/
#   ├── index.html
#   ├── presenter.html
#   ├── slides/
#   │   ├── slide_01_cover.html
#   │   └── ... (15 pages)
#   └── slides_metadata.json
```

---

## 十二、总结

**新架构的核心价值：**

1. **模块化** - 每页独立，易于维护
2. **高性能** - 按需加载，响应迅速
3. **可扩展** - 轻松添加新模板和功能
4. **专业级** - 接近真实PPT的体验
5. **AI友好** - 便于并行生成和质量控制

这个架构参考了行业最佳实践，结合了Web技术和PPT设计理念，能够生成真正专业级的演示文稿。
