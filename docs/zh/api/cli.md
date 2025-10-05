# CLI 参考

XunLong提供全面的命令行界面，用于所有内容生成任务。

## 安装

```bash
# 安装XunLong
pip install -r requirements.txt

# 验证安装
python xunlong.py --version
```

## 全局选项

```bash
python xunlong.py [命令] [选项]
```

| 选项 | 说明 |
|------|------|
| `--version` | 显示版本并退出 |
| `--help` | 显示帮助信息 |

## 命令概览

| 命令 | 用途 | 快速示例 |
|------|------|----------|
| [`report`](#report-命令) | 生成研究报告 | `xunlong.py report "AI趋势"` |
| [`fiction`](#fiction-命令) | 创作小说 | `xunlong.py fiction "推理小说"` |
| [`ppt`](#ppt-命令) | 生成演示文稿 | `xunlong.py ppt "产品发布"` |
| [`export`](#export-命令) | 导出为不同格式 | `xunlong.py export <id> --type pdf` |
| [`iterate`](#iterate-命令) | 优化已有内容 | `xunlong.py iterate <id> "添加示例"` |
| [`ask`](#ask-命令) | 快速问答（实验性） | `xunlong.py ask "什么是AI？"` |
| [`status`](#status-命令) | 检查系统状态 | `xunlong.py status` |

---

## `report` 命令

生成全面的研究报告。

### 语法

```bash
python xunlong.py report 查询内容 [选项]
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `查询内容` | 是 | 研究主题或问题 |

### 选项

| 选项 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--type` | `-t` | 选择 | `comprehensive` | 报告类型 |
| `--depth` | `-d` | 选择 | `deep` | 搜索深度 |
| `--max-results` | `-m` | 整数 | `20` | 最大搜索结果数 |
| `--output-format` | `-o` | 选择 | `html` | 输出格式 |
| `--html-template` | | 字符串 | `academic` | HTML模板 |
| `--html-theme` | | 字符串 | `light` | HTML主题 |
| `--verbose` | `-v` | 标志 | `false` | 显示详细过程 |

### 报告类型

| 值 | 说明 | 最适合 |
|----|------|--------|
| `comprehensive` | 全面详细报告 | 深度分析 |
| `daily` | 日报格式 | 快速更新 |
| `analysis` | 分析报告 | 数据分析 |
| `research` | 学术研究 | 研究论文 |

### 搜索深度

| 值 | 速度 | 结果 | 最适合 |
|----|------|------|--------|
| `surface` | 快速 | 5-10条 | 快速概览 |
| `medium` | 中等 | 10-15条 | 标准报告 |
| `deep` | 较慢 | 15-20+条 | 全面研究 |

### 输出格式

| 值 | 扩展名 | 说明 |
|----|--------|------|
| `html` | `.html` | 样式化网页 |
| `md` / `markdown` | `.md` | 纯Markdown |

### HTML模板

| 值 | 风格 | 最适合 |
|----|------|--------|
| `academic` | 正式、结构化 | 研究报告 |
| `technical` | 代码友好 | 技术文档 |

### HTML主题

| 值 | 风格 |
|----|------|
| `light` | 浅色背景 |
| `dark` | 深色背景 |

### 示例

**基础用法：**
```bash
python xunlong.py report "2025年人工智能趋势"
```

**自定义深度和结果数：**
```bash
python xunlong.py report "区块链技术" \
  --type analysis \
  --depth deep \
  --max-results 30
```

**Markdown输出：**
```bash
python xunlong.py report "量子计算" \
  -o md \
  -v
```

**技术报告with深色主题：**
```bash
python xunlong.py report "Kubernetes最佳实践" \
  --type research \
  --html-template technical \
  --html-theme dark
```

---

## `fiction` 命令

创作虚构故事和小说。

### 语法

```bash
python xunlong.py fiction 查询内容 [选项]
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `查询内容` | 是 | 故事设定或描述 |

### 选项

| 选项 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--genre` | `-g` | 选择 | `mystery` | 小说类型 |
| `--length` | `-l` | 选择 | `short` | 篇幅长度 |
| `--viewpoint` | `-vp` | 选择 | `first` | 叙事视角 |
| `--constraint` | `-c` | 字符串 | 无 | 特殊约束（可多次） |
| `--output-format` | `-o` | 选择 | `html` | 输出格式 |
| `--html-template` | | 字符串 | `novel` | HTML模板 |
| `--html-theme` | | 字符串 | `sepia` | HTML主题 |
| `--verbose` | `-v` | 标志 | `false` | 显示详情 |

### 类型

| 值 | 说明 | 特点 |
|----|------|------|
| `mystery` | 推理/侦探 | 解谜、线索 |
| `scifi` | 科幻 | 未来、科技 |
| `fantasy` | 奇幻 | 魔法、神话 |
| `horror` | 恐怖 | 悬疑、恐惧 |
| `romance` | 爱情 | 感情故事 |
| `wuxia` | 武侠 | 武功、江湖 |

### 篇幅长度

| 值 | 章节 | 字数 | 阅读时间 |
|----|------|------|----------|
| `short` | 5章 | 1-1.5万字 | 1-2小时 |
| `medium` | 12章 | 3-5万字 | 3-5小时 |
| `long` | 30章 | 8-12万字 | 8-12小时 |

### 视角

| 值 | 说明 | 示例 |
|----|------|------|
| `first` | 第一人称 | "我走进房间..." |
| `third` | 第三人称 | "她走进房间..." |
| `omniscient` | 全知视角 | "她不知道，危险正潜伏..." |

### 约束

使用`-c`多次添加约束：

```bash
-c "密室" -c "暴风雪" -c "时间限制"
```

### 示例

**基础推理故事：**
```bash
python xunlong.py fiction "侦探调查密室杀人案"
```

**科幻中篇：**
```bash
python xunlong.py fiction "与外星人首次接触" \
  --genre scifi \
  --length medium \
  --viewpoint third
```

**有约束的推理：**
```bash
python xunlong.py fiction "别墅谋杀案" \
  --genre mystery \
  -c "暴风雪孤立" \
  -c "8个嫌疑人" \
  -o html \
  -v
```

**长篇奇幻史诗：**
```bash
python xunlong.py fiction "少年英雄拯救王国" \
  --genre fantasy \
  --length long \
  --viewpoint omniscient \
  --html-template ebook
```

---

## `ppt` 命令

生成PowerPoint风格的演示文稿。

### 语法

```bash
python xunlong.py ppt 主题 [选项]
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `主题` | 是 | 演示文稿主题 |

### 选项

| 选项 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--style` | `-s` | 选择 | `business` | PPT风格 |
| `--slides` | `-n` | 整数 | `10` | 幻灯片数量 |
| `--depth` | `-d` | 选择 | `medium` | 内容深度 |
| `--theme` | | 字符串 | `default` | 配色主题 |
| `--speech-notes` | | 字符串 | 无 | 生成演说稿 |
| `--verbose` | `-v` | 标志 | `false` | 显示详情 |

### PPT风格

| 值 | 说明 | 最适合 |
|----|------|--------|
| `red` | RED极简风 | 简洁、聚焦 |
| `business` | 商务详细 | 企业汇报 |
| `academic` | 学术风格 | 学术演讲 |
| `creative` | 创意设计 | 营销推广 |
| `simple` | 极简设计 | 技术分享 |

### 页数建议

| 页数 | 时长 | 最适合 |
|------|------|--------|
| 5-7 | 5-10分钟 | 快速展示 |
| 10-15 | 15-20分钟 | 标准演示 |
| 20-30 | 30-45分钟 | 详细讲解 |
| 40+ | 60+分钟 | 工作坊/培训 |

### 深度级别

| 值 | 详细度 | 每页内容 |
|----|--------|----------|
| `surface` | 简要 | 3-5个要点 |
| `medium` | 均衡 | 5-7个要点 |
| `deep` | 详细 | 7-10个要点 |

### 配色主题

| 值 | 颜色 | 最适合 |
|----|------|--------|
| `default` | 中性色 | 通用 |
| `blue` | 蓝色调 | 企业 |
| `red` | 红色强调 | 有力陈述 |
| `green` | 绿色调 | 环保主题 |
| `purple` | 紫色系 | 创意 |

### 演说稿

提供场景描述以生成演讲稿：

```bash
--speech-notes "面向投资人的种子轮路演"
```

这将为每页生成详细的演讲要点。

### 示例

**基础演示：**
```bash
python xunlong.py ppt "人工智能概述"
```

**商务演示：**
```bash
python xunlong.py ppt "第四季度销售业绩" \
  --style business \
  --slides 15 \
  --theme blue
```

**学术报告：**
```bash
python xunlong.py ppt "机器学习研究" \
  --style academic \
  --depth deep \
  --slides 25
```

**投资路演with演说稿：**
```bash
python xunlong.py ppt "创业种子轮融资" \
  --style red \
  --slides 10 \
  --speech-notes "向风险投资人展示" \
  -v
```

---

## `export` 命令

将项目导出为不同格式。

### 语法

```bash
python xunlong.py export 项目ID --type 格式 [选项]
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `项目ID` | 是 | 项目标识符（来自生成输出） |

### 选项

| 选项 | 简写 | 类型 | 必需 | 说明 |
|------|------|------|------|------|
| `--type` | `-t` | 选择 | 是 | 导出格式 |
| `--output` | `-o` | 字符串 | 否 | 自定义输出路径 |
| `--verbose` | `-v` | 标志 | 否 | 显示详情 |

### 导出格式

| 值 | 扩展名 | 说明 | 依赖 |
|----|--------|------|------|
| `pptx` | `.pptx` | PowerPoint文件 | `python-pptx` |
| `pdf` | `.pdf` | PDF文档 | `weasyprint` |
| `docx` | `.docx` | Word文档 | `python-docx` |
| `md` | `.md` | Markdown文件 | 内置 |

### 示例

**导出为PowerPoint：**
```bash
python xunlong.py export 20251005_143022_ai趋势 --type pptx
```

**导出为PDF with自定义路径：**
```bash
python xunlong.py export 20251005_180344_报告 \
  --type pdf \
  --output ~/桌面/我的报告.pdf
```

**导出为Word：**
```bash
python xunlong.py export 20251005_215421_小说 \
  --type docx \
  -v
```

### 安装导出依赖

```bash
# PPTX导出
pip install python-pptx

# PDF导出
pip install weasyprint

# DOCX导出
pip install python-docx

# 全部安装
pip install python-pptx python-docx markdown2 weasyprint
```

---

## `iterate` 命令

优化和修改已有项目。

### 语法

```bash
python xunlong.py iterate 项目ID 需求描述 [选项]
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `项目ID` | 是 | 项目标识符 |
| `需求描述` | 是 | 修改请求 |

### 选项

| 选项 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--verbose` | `-v` | 标志 | `false` | 显示详情 |

### 修改示例

**报告：**
```bash
# 添加内容
python xunlong.py iterate 20251005_143022 "添加未来趋势章节"

# 更新数据
python xunlong.py iterate 20251005_143022 "用2025年数据更新统计"

# 提高清晰度
python xunlong.py iterate 20251005_143022 "简化技术解释"
```

**小说：**
```bash
# 角色发展
python xunlong.py iterate 20251005_180344 "让第3章的主角更纠结"

# 情节增强
python xunlong.py iterate 20251005_180344 "在第5章添加伏笔"

# 节奏调整
python xunlong.py iterate 20251005_180344 "放慢高潮场景的节奏"
```

**PPT：**
```bash
# 添加页面
python xunlong.py iterate 20251005_215421 "在第5页后添加2页市场分析"

# 修改内容
python xunlong.py iterate 20251005_215421 "将第3页图表改为饼图"

# 重新排序
python xunlong.py iterate 20251005_215421 "将总结页移到问答页之前"
```

---

## `ask` 命令

快速问答，无需深度研究（实验性）。

### 语法

```bash
python xunlong.py ask 问题 [选项]
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `问题` | 是 | 您的问题 |

### 选项

| 选项 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--model` | `-m` | 选择 | `balanced` | 模型选择 |
| `--verbose` | `-v` | 标志 | `false` | 显示详情 |

### 模型选项

| 值 | 速度 | 质量 | 最适合 |
|----|------|------|--------|
| `fast` | 最快 | 基础 | 快速回答 |
| `balanced` | 中等 | 良好 | 一般问答 |
| `quality` | 较慢 | 最佳 | 复杂问题 |

### 示例

```bash
# 基础问题
python xunlong.py ask "什么是量子计算？"

# 高质量回答
python xunlong.py ask "解释机器学习" --model quality -v
```

**注意：** 此功能目前正在开发中。

---

## `status` 命令

检查系统状态和配置。

### 语法

```bash
python xunlong.py status
```

### 输出信息

- 系统状态
- LLM配置数量
- 可用提供商
- 提供商状态

### 示例

```bash
python xunlong.py status
```

**输出：**
```
=== XunLong 系统状态 ===

系统: XunLong v1.0.0
状态: ✓ 运行中

LLM配置: 3个

可用提供商:
  • OpenAI: 可用
  • Anthropic: 可用
  • Local: 未配置
```

---

## 常用工作流

### 1. 生成报告 → 导出为PDF

```bash
# 步骤1: 生成报告
python xunlong.py report "2025年AI行业分析" \
  --type comprehensive \
  --depth deep \
  -o md

# 步骤2: 从输出获取项目ID
# (例如: 20251005_143022_ai_industry_analysis)

# 步骤3: 导出为PDF
python xunlong.py export 20251005_143022_ai_industry_analysis --type pdf
```

### 2. 创作小说 → 迭代 → 导出

```bash
# 步骤1: 生成故事
python xunlong.py fiction "侦探推理" \
  --genre mystery \
  --length medium

# 步骤2: 优化
python xunlong.py iterate 20251005_180344_侦探推理 \
  "在第3章添加更多线索"

# 步骤3: 导出为DOCX
python xunlong.py export 20251005_180344_侦探推理 --type docx
```

### 3. 创建PPT → 添加页面 → 导出

```bash
# 步骤1: 生成PPT
python xunlong.py ppt "2025产品发布" \
  --style business \
  --slides 12

# 步骤2: 添加页面
python xunlong.py iterate 20251005_215421_产品发布 \
  "添加3页定价策略内容"

# 步骤3: 导出为PowerPoint
python xunlong.py export 20251005_215421_产品发布 --type pptx
```

---

## 环境变量

通过环境变量配置XunLong行为：

```bash
# LLM API密钥
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# LangFuse追踪（可选）
export LANGFUSE_SECRET_KEY="your-key"
export LANGFUSE_PUBLIC_KEY="your-key"
export LANGFUSE_HOST="https://cloud.langfuse.com"

# 默认设置
export XUNLONG_DEFAULT_DEPTH="deep"
export XUNLONG_DEFAULT_FORMAT="html"
```

---

## 提示与最佳实践

### 1. 使用详细模式调试

```bash
python xunlong.py report "主题" -v
```

显示详细执行步骤。

### 2. 保存项目ID

导出和迭代需要项目ID：

```bash
# 良好实践: 保存到变量
PROJECT_ID=$(python xunlong.py report "主题" | grep "项目ID" | cut -d: -f2)
python xunlong.py export $PROJECT_ID --type pdf
```

### 3. 组合格式

同时生成HTML和Markdown：

```bash
# 生成HTML
python xunlong.py report "主题" -o html

# 导出相同项目为Markdown
python xunlong.py export <project-id> --type md
```

### 4. 迭代优化

不要追求一次完美：

```bash
# 1. 快速生成
python xunlong.py report "主题" --depth surface

# 2. 审核输出
# 3. 迭代改进
python xunlong.py iterate <id> "添加更多示例"
```

### 5. 使用适当深度

| 任务 | 推荐深度 |
|------|----------|
| 快速概览 | `surface` |
| 标准报告 | `medium` |
| 研究论文 | `deep` |
| 博客文章 | `surface` 或 `medium` |

---

## 故障排除

### 命令未找到

```bash
# 明确使用python
python xunlong.py --help

# 或设置可执行
chmod +x xunlong.py
./xunlong.py --help
```

### 缺少依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 安装导出依赖
pip install python-pptx python-docx markdown2 weasyprint
```

### API密钥问题

```bash
# 检查API密钥是否设置
echo $OPENAI_API_KEY

# 设置API密钥
export OPENAI_API_KEY="sk-..."
```

### 项目未找到

```bash
# 列出项目
ls storage/

# 使用完整项目ID（包括时间戳）
python xunlong.py export 20251005_143022_完整名称 --type pdf
```

---

## 下一步

- 了解[配置](/zh/api/configuration)
- 探索[报告生成](/zh/guide/features/report)
- 尝试[小说创作](/zh/guide/features/fiction)
- 查看[PPT制作](/zh/guide/features/ppt)
