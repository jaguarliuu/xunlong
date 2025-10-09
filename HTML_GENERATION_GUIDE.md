# HTML Report Generation - Enhanced System Guide

## Overview

XunLong's enhanced HTML generation system provides professional, commercial-grade report output with:

- **Modern responsive design** with elegant typography
- **Automatic data visualization** using ECharts
- **Smart table detection** and chart generation
- **Professional reference system** with hover effects
- **AIGC watermark** and metadata compliance
- **Multi-template support** for different use cases

## Quick Start

### Basic Usage

```python
from src.agents.html.document_html_agent import DocumentHTMLAgent

# Initialize the agent
html_agent = DocumentHTMLAgent()

# Convert Markdown to HTML
markdown_content = """
# AI Technology Report

## Introduction
Artificial Intelligence has evolved significantly over the past decades...

## Market Data

| Year | Market Size (Billion USD) | Growth Rate |
|------|---------------------------|-------------|
| 2020 | 50.1 | 15.2% |
| 2021 | 62.5 | 24.8% |
| 2022 | 85.3 | 36.5% |
| 2023 | 119.8 | 40.4% |
"""

metadata = {
    'title': 'AI Technology Report 2023',
    'author': 'XunLong AI',
    'date': '2025-01-15',
    'references': [
        {
            'title': 'Global AI Market Report',
            'url': 'https://example.com/ai-market'
        }
    ]
}

# Generate HTML
html = html_agent.convert_to_html(
    content=markdown_content,
    metadata=metadata,
    output_path='output/report.html'
)
```

## Key Features

### 1. Automatic Chart Generation

The system automatically detects Markdown tables and creates appropriate visualizations:

#### Bar Charts (≤7 categories)
For small datasets, the system generates bar charts:

```markdown
| Product | Sales |
|---------|-------|
| A       | 120   |
| B       | 85    |
| C       | 150   |
```

→ Generates a bar chart with 3 bars

#### Line Charts (>7 categories)
For larger datasets or time series:

```markdown
| Month | Revenue |
|-------|---------|
| Jan   | 100000  |
| Feb   | 110000  |
| Mar   | 115000  |
| Apr   | 125000  |
| May   | 140000  |
| Jun   | 155000  |
| Jul   | 160000  |
| Aug   | 170000  |
```

→ Generates a line chart showing trends

#### Dual-Axis Charts
When tables have 3+ columns with numeric data:

```markdown
| Quarter | Revenue | Profit Margin |
|---------|---------|---------------|
| Q1      | 500000  | 12.5          |
| Q2      | 650000  | 15.2          |
| Q3      | 720000  | 18.3          |
| Q4      | 890000  | 21.7          |
```

→ Generates both a single-axis chart AND a dual-axis comparison chart

### 2. Manual Chart Creation

For more control, use the EChartsGenerator directly:

```python
from src.agents.html.echarts_generator import EChartsGenerator

chart_gen = EChartsGenerator()

# Create a pie chart
chart_gen.add_pie_chart(
    chart_id='market_share',
    title='市场份额分布',
    data=[
        {'name': '公司A', 'value': 35.5},
        {'name': '公司B', 'value': 28.2},
        {'name': '公司C', 'value': 18.9},
        {'name': '其他', 'value': 17.4}
    ]
)

# Create a heatmap
chart_gen.add_heatmap(
    chart_id='correlation',
    title='Feature Correlation Matrix',
    x_categories=['Feature1', 'Feature2', 'Feature3'],
    y_categories=['Target1', 'Target2', 'Target3'],
    data=[
        [0, 0, 0.85], [0, 1, 0.72], [0, 2, 0.43],
        [1, 0, 0.62], [1, 1, 0.91], [1, 2, 0.38],
        [2, 0, 0.41], [2, 1, 0.55], [2, 2, 0.78]
    ]
)

# Get all chart configurations
charts = chart_gen.get_all_charts()

# Pass to HTML agent
metadata['charts'] = charts
```

### 3. Reference System

Add professional citations:

```python
metadata = {
    'references': [
        {
            'title': 'Attention Is All You Need',
            'url': 'https://arxiv.org/abs/1706.03762'
        },
        {
            'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
            'url': 'https://arxiv.org/abs/1810.04805'
        }
    ]
}
```

References appear at the bottom with:
- Hover effects
- Numbered list
- Clickable URLs
- Clean formatting

### 4. Template Selection

Choose from available templates:

```python
# Enhanced professional (default) - Modern commercial design
html_agent = DocumentHTMLAgent(default_template='enhanced_professional')

# Academic - Traditional research paper style
html_agent = DocumentHTMLAgent(default_template='academic')

# Technical - Code-focused documentation
html_agent = DocumentHTMLAgent(default_template='technical')

# Simple - Minimalist clean design
html_agent = DocumentHTMLAgent(default_template='simple')
```

### 5. Custom Styling

Override styles with custom CSS:

```python
custom_css = """
h1 { color: #2c3e50; }
.container { max-width: 1200px; }
"""

html = html_agent.convert_to_html(
    content=markdown_content,
    custom_css=custom_css
)
```

## Template Structure

### enhanced_professional.html

**Design Principles:**
- **Container**: 900px max-width, centered with elegant shadow
- **Colors**:
  - Primary: `#1a237e` (headers)
  - Accent: `#c62828` (strong emphasis)
  - Links: `#1e88e5` (blue)
- **Typography**: Line-height 1.8-1.9 for excellent readability
- **Charts**: 450px height containers with borders
- **Responsive**: Adapts to mobile (768px breakpoint)

**Sections:**
1. Document metadata (title, author, date)
2. Table of contents with gradient background
3. Main content with Markdown rendering
4. Chart containers (auto-generated)
5. Reference section
6. AI watermark

## Chart Types Reference

### Bar Chart
```python
chart_gen.add_bar_chart(
    chart_id='sales',
    title='2023年销售业绩',
    categories=['Q1', 'Q2', 'Q3', 'Q4'],
    data=[125, 145, 168, 192],
    y_axis_name='销售额(万元)',
    color='#5470c6',
    subtitle='季度对比'
)
```

### Line Chart
```python
chart_gen.add_line_chart(
    chart_id='trend',
    title='用户增长趋势',
    categories=['1月', '2月', '3月', '4月', '5月', '6月'],
    data=[1200, 1450, 1580, 1820, 2100, 2350],
    y_axis_name='用户数',
    smooth=True,     # Smooth curve
    area=True        # Show area under line
)
```

### Pie Chart
```python
chart_gen.add_pie_chart(
    chart_id='distribution',
    title='用户来源分布',
    data=[
        {'name': '搜索引擎', 'value': 335},
        {'name': '直接访问', 'value': 310},
        {'name': '社交媒体', 'value': 234},
        {'name': '广告推广', 'value': 135}
    ]
)
```

### Dual-Axis Chart
```python
chart_gen.add_dual_axis_chart(
    chart_id='comparison',
    title='营收与利润对比',
    categories=['1月', '2月', '3月', '4月'],
    bar_data=[320, 332, 301, 334],
    line_data=[120, 132, 101, 134],
    bar_name='营收',
    line_name='利润',
    bar_y_axis_name='营收(万元)',
    line_y_axis_name='利润(万元)'
)
```

### Heatmap
```python
chart_gen.add_heatmap(
    chart_id='heatmap',
    title='周销售热力图',
    x_categories=['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    y_categories=['上午', '下午', '晚上'],
    data=[
        [0, 0, 5], [0, 1, 1], [0, 2, 0],
        [1, 0, 1], [1, 1, 3], [1, 2, 0],
        # ... [x_index, y_index, value]
    ]
)
```

### Graph/Network Chart
```python
chart_gen.add_graph_chart(
    chart_id='knowledge_graph',
    title='知识图谱',
    nodes=[
        {'name': 'AI', 'x': 300, 'y': 300, 'symbolSize': 100},
        {'name': 'NLP', 'x': 500, 'y': 200, 'symbolSize': 80},
        {'name': 'CV', 'x': 500, 'y': 400, 'symbolSize': 80}
    ],
    links=[
        {'source': 'AI', 'target': 'NLP'},
        {'source': 'AI', 'target': 'CV'}
    ]
)
```

## Advanced Usage

### Disable Auto Chart Generation

```python
metadata = {
    'enable_charts': False  # Disable automatic chart detection
}
```

### Access Chart Data

```python
# After conversion, access generated charts
parsed_data = html_agent.parse_content(content, metadata)
charts = parsed_data['charts']

for chart in charts:
    print(f"Chart ID: {chart['id']}")
    print(f"Title: {chart['title']}")
    print(f"Config: {chart['option']}")
```

### Custom Project ID

```python
metadata = {
    'project_id': 'proj_12345'  # Custom ID for AIGC metadata
}
```

## Integration with Report Coordinator

The DocumentHTMLAgent integrates seamlessly with the report generation pipeline:

```python
from src.agents.report.report_coordinator import ReportCoordinator

coordinator = ReportCoordinator()

# Generate report with refined subtasks
report = await coordinator.generate_report(
    query="AI技术发展趋势",
    refined_subtasks=refined_subtasks,
    search_results=search_results,
    output_format='html'
)

# The coordinator automatically:
# 1. Generates Markdown content
# 2. Extracts data tables
# 3. Creates visualizations
# 4. Renders to professional HTML
```

## Best Practices

### 1. Table Formatting
Ensure Markdown tables are properly formatted:
```markdown
| Header1 | Header2 | Header3 |
|---------|---------|---------|
| Value1  | 123     | 45.6    |
| Value2  | 456     | 78.9    |
```

### 2. Numeric Data
- Remove thousand separators or use commas: `1,234` works
- Percentage signs are handled: `15.5%` → `15.5`
- Non-numeric data in value columns skips chart generation

### 3. Chart Placement
Charts are inserted after their corresponding section. Structure content to place data tables where you want visualizations.

### 4. Performance
- Charts use `animation: false` for faster rendering
- Large datasets (>50 rows) automatically trigger line charts
- Heatmaps limited to reasonable grid sizes

### 5. Accessibility
- All charts have descriptive titles
- Data is also available in table form
- Color schemes tested for readability

## Troubleshooting

### Charts Not Appearing
1. Check table format (must have header + separator + data rows)
2. Verify numeric data in value columns
3. Ensure `enable_charts` is not `False` in metadata
4. Check browser console for JavaScript errors

### Template Not Found
```python
# Verify template directory
html_agent = DocumentHTMLAgent(
    template_dir=Path('/path/to/templates')
)
```

### Styling Issues
- Check for conflicting custom CSS
- Verify template variables are passed correctly
- Test with default template first

## Examples

Complete example with all features:

```python
from src.agents.html.document_html_agent import DocumentHTMLAgent
from pathlib import Path

markdown = """
# 2023年度AI市场分析报告

## 执行摘要
本报告分析了2023年人工智能市场的主要趋势和发展...

## 市场规模

| 年份 | 市场规模(亿美元) | 增长率 |
|------|------------------|--------|
| 2020 | 501             | 15.2%  |
| 2021 | 625             | 24.8%  |
| 2022 | 853             | 36.5%  |
| 2023 | 1198            | 40.4%  |

## 主要应用领域

| 领域     | 市场份额 |
|----------|----------|
| 金融科技 | 28.5%    |
| 医疗健康 | 22.3%    |
| 自动驾驶 | 18.7%    |
| 智能制造 | 15.2%    |
| 其他     | 15.3%    |

## 结论
AI技术正在快速发展，预计未来五年将继续保持高速增长...
"""

metadata = {
    'title': '2023年度AI市场分析报告',
    'author': 'XunLong AI Research',
    'date': '2025-01-15',
    'keywords': ['人工智能', '市场分析', '趋势预测'],
    'references': [
        {'title': 'Gartner AI Market Report 2023', 'url': 'https://www.gartner.com/ai'},
        {'title': 'IDC AI Spending Guide', 'url': 'https://www.idc.com/ai'}
    ]
}

html_agent = DocumentHTMLAgent()
html = html_agent.convert_to_html(
    content=markdown,
    metadata=metadata,
    output_path=Path('output/ai_report_2023.html')
)

print(f"Report generated successfully!")
print(f"Charts created: {len(html_agent.chart_generator.get_all_charts())}")
```

## Summary

The enhanced HTML generation system provides:

✅ **Automatic intelligence** - Detects and visualizes data
✅ **Professional design** - Commercial-grade aesthetics
✅ **Flexibility** - Manual control when needed
✅ **Integration** - Works seamlessly with XunLong pipeline
✅ **Compliance** - AIGC metadata and watermarks

For advanced customization, refer to the template source code and EChartsGenerator implementation.
