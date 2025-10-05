# 导出格式

XunLong支持多种导出格式，以适应不同的用例和平台。

## 概览

将您的内容导出为：
- 📝 Markdown (.md)
- 🌐 HTML (.html)
- 📄 PDF (.pdf)
- 📃 DOCX (.docx)
- 📊 PPTX (.pptx)
- 📚 EPUB (.epub)

## 快速开始

```bash
# 导出为单一格式
python xunlong.py export <project-id> --format pdf

# 导出为多种格式
python xunlong.py export <project-id> --format md,html,pdf,docx
```

## Markdown导出

### 功能

- ✅ 简洁、可读的文本
- ✅ 版本控制友好
- ✅ 平台无关
- ✅ 易于编辑
- ✅ GitHub/GitLab兼容

### 使用

```bash
python xunlong.py export <project-id> --format md
```

### 输出结构

```markdown
# 报告标题

## 目录
- [简介](#简介)
- [主要内容](#主要内容)
- [结论](#结论)

## 简介

内容在这里...

## 参考文献

[1] 来源引用
```

### 选项

```bash
# 包含目录
python xunlong.py export <project-id> \
  --format md \
  --include-toc

# 添加元数据
python xunlong.py export <project-id> \
  --format md \
  --include-metadata
```

### 最适合

- 文档
- GitHub仓库
- 版本控制的内容
- 纯文本工作流
- 跨平台分享

## HTML导出

### 功能

- ✅ 专业样式
- ✅ 响应式设计
- ✅ 交互元素
- ✅ 可打印
- ✅ 浏览器兼容

### 使用

```bash
python xunlong.py export <project-id> --format html
```

### 模板

```bash
# 学术模板
python xunlong.py export <project-id> \
  --format html \
  --template academic

# 技术模板
python xunlong.py export <project-id> \
  --format html \
  --template technical

# 小说模板
python xunlong.py export <project-id> \
  --format html \
  --template novel
```

### 主题

```bash
# 浅色主题
python xunlong.py export <project-id> \
  --format html \
  --theme light

# 深色主题
python xunlong.py export <project-id> \
  --format html \
  --theme dark

# 复古主题（用于小说）
python xunlong.py export <project-id> \
  --format html \
  --theme sepia
```

### 功能

**交互式目录：**
- 可点击的章节链接
- 突出显示当前部分
- 平滑滚动

**响应式设计：**
- 移动端友好
- 平板电脑优化
- 桌面端布局

**打印优化：**
- 打印时隐藏导航
- 适当的分页符
- 页眉和页脚

### 最适合

- Web发布
- 在线文档
- 交互式报告
- 演示
- 可打印输出

## PDF导出

### 功能

- ✅ 专业布局
- ✅ 一致的格式
- ✅ 可打印
- ✅ 通用兼容性
- ✅ 嵌入字体

### 使用

```bash
python xunlong.py export <project-id> --format pdf
```

### 页面设置

```bash
# A4页面
python xunlong.py export <project-id> \
  --format pdf \
  --page-size a4

# Letter页面
python xunlong.py export <project-id> \
  --format pdf \
  --page-size letter

# 自定义尺寸
python xunlong.py export <project-id> \
  --format pdf \
  --page-size custom \
  --width 6in \
  --height 9in
```

### 边距

```bash
python xunlong.py export <project-id> \
  --format pdf \
  --margin-top 1in \
  --margin-bottom 1in \
  --margin-left 1in \
  --margin-right 1in
```

### 页眉和页脚

```bash
python xunlong.py export <project-id> \
  --format pdf \
  --header "报告标题" \
  --footer "第{page}页，共{total}页" \
  --page-numbers
```

### 目录

```bash
python xunlong.py export <project-id> \
  --format pdf \
  --include-toc \
  --toc-depth 3
```

### 书签

```bash
python xunlong.py export <project-id> \
  --format pdf \
  --bookmarks  # 基于标题自动创建书签
```

### 最适合

- 正式报告
- 打印文档
- 存档
- 分发
- 专业演示

## DOCX导出

### 功能

- ✅ Microsoft Word兼容
- ✅ 可编辑格式
- ✅ 注释支持
- ✅ 跟踪更改就绪
- ✅ 样式保留

### 使用

```bash
python xunlong.py export <project-id> --format docx
```

### 样式

```bash
# 应用Word样式
python xunlong.py export <project-id> \
  --format docx \
  --style professional

# 使用自定义模板
python xunlong.py export <project-id> \
  --format docx \
  --template custom-template.dotx
```

### 字体

```bash
python xunlong.py export <project-id> \
  --format docx \
  --font-heading "Calibri" \
  --font-body "Arial" \
  --font-size 11
```

### 功能

**文档属性：**
- 标题、作者、主题
- 关键词
- 创建日期
- 修订号

**格式元素：**
- 标题样式（H1-H6）
- 段落样式
- 列表（项目符号和编号）
- 表格
- 图像
- 页面分隔符

**协作：**
- 注释占位符
- 跟踪更改兼容
- 版本历史
- 审阅模式就绪

### 最适合

- 进一步编辑
- 协作
- 企业环境
- 注释和审阅
- Office工作流

## PPTX导出

### 功能

- ✅ PowerPoint兼容
- ✅ 专业布局
- ✅ 母版幻灯片
- ✅ 演示文稿就绪
- ✅ 动画支持

### 使用

```bash
# 从报告/小说自动创建幻灯片
python xunlong.py export <project-id> --format pptx

# 指定幻灯片数量
python xunlong.py export <project-id> \
  --format pptx \
  --slides 15
```

### 主题

```bash
python xunlong.py export <project-id> \
  --format pptx \
  --ppt-theme corporate-blue
```

### 内容分发

**自动分发：**
XunLong智能地将长内容拆分为幻灯片：
- 每个主要部分一张幻灯片
- 要点用于关键信息
- 引用幻灯片用于引文
- 摘要幻灯片

**自定义分发：**
```bash
python xunlong.py export <project-id> \
  --format pptx \
  --sections-per-slide 2
```

### 演讲备注

```bash
python xunlong.py export <project-id> \
  --format pptx \
  --speaker-notes detailed
```

### 最适合

- 演示文稿
- 会议演讲
- 教育讲座
- 商务推介
- 培训材料

## EPUB导出

### 功能

- ✅ 电子书格式
- ✅ 电子阅读器兼容
- ✅ 可调整字体大小
- ✅ 章节导航
- ✅ 元数据丰富

### 使用

```bash
python xunlong.py export <project-id> --format epub
```

### 元数据

```bash
python xunlong.py export <project-id> \
  --format epub \
  --title "我的小说" \
  --author "作者名" \
  --language zh-CN \
  --publisher "出版商" \
  --isbn "978-1234567890"
```

### 封面

```bash
python xunlong.py export <project-id> \
  --format epub \
  --cover cover-image.jpg
```

### 样式

```bash
python xunlong.py export <project-id> \
  --format epub \
  --epub-style modern  # modern, classic, minimal
```

### 功能

**导航：**
- 自动目录
- 章节标记
- 页面列表
- 地标

**兼容性：**
- EPUB3标准
- Kindle（转换后）
- iBooks
- Google Play图书
- Kobo

**可访问性：**
- 屏幕阅读器支持
- 语义HTML
- 替代文本

### 最适合

- 小说和小说
- 电子书出版
- 移动阅读
- 电子阅读器
- 数字发行

## 批量导出

### 导出所有格式

```bash
python xunlong.py export <project-id> --format all
```

生成：
- report.md
- report.html
- report.pdf
- report.docx

### 选择性导出

```bash
# Web格式
python xunlong.py export <project-id> --format html,pdf

# Office格式
python xunlong.py export <project-id> --format docx,pptx

# 发布格式
python xunlong.py export <project-id> --format pdf,epub
```

### 输出目录

```bash
python xunlong.py export <project-id> \
  --format all \
  --output-dir ./exports
```

## 自定义导出

### 自定义模板

```bash
# 使用自定义HTML模板
python xunlong.py export <project-id> \
  --format html \
  --template ./templates/my-template.html

# 使用自定义Word模板
python xunlong.py export <project-id> \
  --format docx \
  --template ./templates/company-template.dotx
```

### CSS样式

```bash
python xunlong.py export <project-id> \
  --format html \
  --custom-css ./styles/custom.css
```

### 后处理

```bash
# 导出后运行脚本
python xunlong.py export <project-id> \
  --format pdf \
  --post-process ./scripts/add-watermark.sh
```

## 导出质量

### 图像处理

```bash
# 高质量图像
python xunlong.py export <project-id> \
  --format pdf \
  --image-quality high \
  --image-dpi 300

# 压缩图像
python xunlong.py export <project-id> \
  --format pdf \
  --compress-images \
  --image-quality medium
```

### 字体嵌入

```bash
python xunlong.py export <project-id> \
  --format pdf \
  --embed-fonts
```

### 优化

```bash
# 针对Web优化
python xunlong.py export <project-id> \
  --format html \
  --optimize-web

# 针对打印优化
python xunlong.py export <project-id> \
  --format pdf \
  --optimize-print
```

## 导出元数据

### 包含生成信息

```bash
python xunlong.py export <project-id> \
  --format all \
  --include-metadata
```

添加：
- 生成日期
- 项目ID
- 版本号
- XunLong版本
- 导出设置

### 文档属性

```bash
python xunlong.py export <project-id> \
  --format pdf \
  --title "报告标题" \
  --author "您的姓名" \
  --subject "主题" \
  --keywords "关键词1,关键词2"
```

## 故障排除

### 问题：PDF字体缺失

**解决方案：**
```bash
python xunlong.py export <project-id> \
  --format pdf \
  --embed-fonts \
  --fallback-font "Arial"
```

### 问题：HTML不显示图像

**解决方案：**
```bash
# 嵌入图像为base64
python xunlong.py export <project-id> \
  --format html \
  --embed-images
```

### 问题：DOCX格式问题

**解决方案：**
```bash
# 使用标准模板
python xunlong.py export <project-id> \
  --format docx \
  --template standard \
  --compatibility-mode
```

### 问题：大文件大小

**解决方案：**
```bash
python xunlong.py export <project-id> \
  --format pdf \
  --compress \
  --compress-images \
  --image-quality medium
```

## 自动化导出

### 导出脚本

```bash
#!/bin/bash
# export-all.sh

PROJECT_ID=$1

# 导出所有格式
python xunlong.py export $PROJECT_ID --format all

# 移到发布目录
mv storage/$PROJECT_ID/exports/* ./publish/

# 创建ZIP存档
cd publish
zip -r ${PROJECT_ID}.zip *
```

### 批处理导出

```bash
# 导出多个项目
for project in project1 project2 project3; do
  python xunlong.py export $project --format pdf,docx
done
```

## API参考

```bash
python xunlong.py export <project-id> [options]
```

| 参数 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| `<project-id>` | str | 必需 | 项目标识符 |
| `--format` | str | `md` | 导出格式（md/html/pdf/docx/pptx/epub/all） |
| `--output-dir` | str | `storage/<id>/exports` | 输出目录 |
| `--template` | str | `default` | 模板名称或路径 |
| `--theme` | str | `light` | 主题（light/dark/sepia） |
| `--include-toc` | flag | `false` | 包含目录 |
| `--include-metadata` | flag | `false` | 包含元数据 |
| `--page-size` | str | `a4` | PDF页面大小 |
| `--embed-fonts` | flag | `false` | 嵌入字体（PDF） |
| `--compress` | flag | `false` | 压缩输出 |

## 示例

### 专业报告包

```bash
python xunlong.py export <report-id> \
  --format pdf,docx \
  --template professional \
  --include-toc \
  --page-numbers \
  --embed-fonts
```

### 电子书发布

```bash
python xunlong.py export <fiction-id> \
  --format epub \
  --title "我的小说" \
  --author "我的名字" \
  --cover cover.jpg \
  --epub-style modern
```

### Web发布

```bash
python xunlong.py export <project-id> \
  --format html \
  --template modern \
  --theme dark \
  --optimize-web \
  --embed-images
```

### 印刷就绪

```bash
python xunlong.py export <project-id> \
  --format pdf \
  --page-size 6x9 \
  --margin-top 0.75in \
  --margin-bottom 0.75in \
  --margin-left 0.5in \
  --margin-right 0.5in \
  --embed-fonts \
  --image-dpi 300
```

## 下一步

- 了解[报告生成](/zh/guide/features/report)
- 探索[小说创作](/zh/guide/features/fiction)
- 查看[PPT制作](/zh/guide/features/ppt)
- 理解[内容迭代](/zh/guide/features/iteration)
