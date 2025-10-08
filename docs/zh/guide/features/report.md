# 报告生成

XunLong擅长在最少输入的情况下生成全面、研究充分的报告。

## 概览

报告生成功能自动完成：
- 🔍 跨网络研究您的主题
- 📊 逻辑化组织研究发现
- ✍️ 撰写专业内容
- 📚 引用所有来源
- 📄 导出为多种格式

### 最新架构更新（2025）

- **章节级智能体**：每个大纲节点都会启动独立写作者与评估者，章节内容并行生成并保持上下文连贯。
- **内置可视化判断**：数据可视化智能体会为包含结构化信息的章节生成表格或图表，输出可直接嵌入HTML。
- **时间感知检索**：深度搜索自动识别“日报”“今天”“2025-03-01”等时间提示，并向DuckDuckGo传递日期过滤参数，仅保留最新结果。
- **更稳定的HTML渲染**：标题先行去重、Markdown提前归一，模板直接消费预渲染片段，避免重复标题及样式漂移。

## 快速开始

```bash
python xunlong.py report "2025年AI行业趋势"
```

就这么简单！XunLong会处理其余的一切。

## 报告风格

XunLong支持三种专业报告风格：

### 商务风格 💼

**最适合：** 市场分析、行业报告、商业智能

**特点：**
- 包含关键要点的执行摘要
- 数据驱动的洞察
- 专业语调
- 图表和表格
- 关注ROI和指标

**示例：**
```bash
python xunlong.py report "电动汽车市场分析" \
  --style business \
  --depth comprehensive
```

**样本输出结构：**
```
├── 执行摘要
├── 市场概览
│   ├── 市场规模与增长
│   └── 主要参与者
├── 趋势分析
├── 竞争格局
├── 机遇与挑战
└── 建议
```

### 学术风格 🎓

**最适合：** 研究摘要、文献综述、学术论文

**特点：**
- 摘要和引言
- 严格引用
- 方法论途径
- 文献综述章节
- 正式学术语调

**示例：**
```bash
python xunlong.py report "机器学习在医疗保健中的应用" \
  --style academic \
  --depth comprehensive
```

**样本输出结构：**
```
├── 摘要
├── 引言
├── 文献综述
├── 研究方法
├── 研究发现
├── 讨论
├── 结论
└── 参考文献
```

### 技术风格 🔧

**最适合：** 技术深度剖析、API文档、技术规范

**特点：**
- 技术准确性
- 代码示例
- 架构图
- 实现细节
- 最佳实践

**示例：**
```bash
python xunlong.py report "GraphQL vs REST API对比" \
  --style technical \
  --depth comprehensive
```

**样本输出结构：**
```
├── 概述
├── 技术架构
├── 核心概念
├── 实现指南
├── 代码示例
├── 性能分析
└── 最佳实践
```

## 深度级别

使用`--depth`参数控制详细程度：

| 深度 | 时间 | 字数 | 最适合 |
|------|------|------|--------|
| **overview** | 约5分钟 | 1,500-2,000 | 快速摘要、初步研究 |
| **standard** | 约10分钟 | 3,000-4,000 | 大多数用例、平衡详细 |
| **comprehensive** | 约20分钟 | 6,000-8,000 | 深度分析、演示文稿 |

**示例：**

```bash
# 快速概览
python xunlong.py report "量子计算" --depth overview

# 平衡报告（默认）
python xunlong.py report "量子计算" --depth standard

# 深度剖析
python xunlong.py report "量子计算" --depth comprehensive
```

## 高级功能

### 分章节流水线

1. **大纲规划**：协调器生成包含编号、标题、要求、字数的结构化大纲。
2. **章节写作智能体并行启动**：每个章节独立撰写，并知晓前后章节要求以保持衔接。
3. **自动可视化判断**：如检测到可结构化的数据，将调用可视化智能体输出表格或图表HTML片段。
4. **质量评估与改写循环**：评估器对章节打分，未达标的段落会按建议重写直至通过或达到迭代上限。
5. **HTML 组装**：最终装配器直接使用预渲染HTML片段构建整份报告，标题、目录与可视化稳定可靠。

由于所有阶段异步执行，即使是综合版或日报类报告也能显著缩短生成时间。

### 自定义章节

精确指定您想要的章节：

```bash
python xunlong.py report "AI伦理" \
  --sections "引言,当前挑战,案例研究,未来展望"
```

### 时间限定研究

- 查询包含“日报”“今天”“昨日”等提示时，系统会自动限定到对应日期并为 DuckDuckGo 设置 `df=` 参数。
- 指定精确日期（如 `2025-03-01`）时，同样只保留目标时段内的结果。

仍可手动覆盖默认窗口：

```bash
python xunlong.py report "新冠疫苗" \
  --time-range "last-6-months"
```

### 语言支持

生成多语言报告：

```bash
python xunlong.py report "气候变化影响" --language zh-CN
python xunlong.py report "Climate Change Impact" --language en-US
```

### 来源过滤

控制使用什么来源：

```bash
# 仅学术来源
python xunlong.py report "暗物质" \
  --sources academic

# 仅新闻来源
python xunlong.py report "科技行业裁员" \
  --sources news

# 所有来源（默认）
python xunlong.py report "AI趋势" \
  --sources all
```

## 输出格式

### Markdown（默认）

```bash
python xunlong.py report "主题" --format md
```

**特点：**
- 干净、可读的文本
- 易于编辑
- 版本控制友好
- 可移植

### HTML

```bash
python xunlong.py report "主题" --format html
```

**特点：**
- 专业样式
- 目录
- 响应式设计
- 打印就绪

### PDF

```bash
python xunlong.py report "主题" --format pdf
```

**特点：**
- 专业布局
- 页码
- 页眉/页脚
- 即时分享

### DOCX

```bash
python xunlong.py report "主题" --format docx
```

**特点：**
- Microsoft Word兼容
- 可编辑格式
- 支持评论
- 准备好跟踪更改

### 多种格式

```bash
python xunlong.py report "主题" --format md,html,pdf,docx
```

所有格式同时生成。

## 报告质量

### 引用

每个事实都有引用：
- 来源URL
- 发布日期
- 作者（如果可用）
- 访问日期

**引用示例：**
```markdown
根据最近的研究，AI采用率增长了67% [1]。

## 参考文献
[1] 张三 (2025). "企业中的AI。" 科技评论。
    https://example.com/ai-enterprise
    访问时间: 2025-10-05
```

### 质量指标

XunLong追踪：
- **引用覆盖率**: 引用声明的百分比（目标: >80%）
- **来源多样性**: 独特来源数量（目标: >10）
- **可读性分数**: Flesch易读性（目标: 60-70）
- **连贯性分数**: 逻辑流畅度评级（目标: >0.85）

查看指标：
```bash
python xunlong.py stats <project-id>
```

### 事实核查

报告经过自动事实核查：
- ✅ 日期验证
- ✅ 统计一致性
- ✅ 来源可信度检查
- ✅ 声明交叉引用

## 示例工作流

### 1. 生成初始报告

```bash
python xunlong.py report "2025年可再生能源趋势" \
  --style business \
  --depth standard \
  --format md,pdf
```

**输出：**
```
✅ 报告生成成功！

📊 统计信息：
   - 耗时: 8分34秒
   - 字数: 3,847
   - 引用: 23个来源
   - 质量分数: 0.89

📁 文件：
   - storage/20251005_143022_renewable_energy/reports/FINAL_REPORT.md
   - storage/20251005_143022_renewable_energy/exports/report.pdf

🔗 项目ID: 20251005_143022
```

### 2. 审核内容

```bash
cat storage/20251005_143022_renewable_energy/reports/FINAL_REPORT.md
```

### 3. 请求修改

```bash
python xunlong.py iterate 20251005_143022 \
  "添加关于太阳能成本的章节并扩展风能章节"
```

### 4. 导出其他格式

```bash
python xunlong.py export 20251005_143022 --format docx,html
```

## 最佳实践

### 📝 撰写有效查询

**好的：**
- "自动驾驶汽车中的AI伦理挑战"
- "2025年远程工作对生产力的影响"
- "Python vs JavaScript在Web开发中的比较"

**效果较差：**
- "AI"（太宽泛）
- "关于工作的东西"（太模糊）
- "告诉我关于编程的一切"（不聚焦）

### 🎯 选择正确的风格

| 您的目标 | 推荐风格 |
|---------|---------|
| 投资者演示 | 商务 |
| 研究论文 | 学术 |
| 内部技术文档 | 技术 |
| 博客文章 | 商务（较轻松语调） |
| 白皮书 | 学术或商务 |

### ⚡ 优化生成时间

**快速（约5分钟）：**
```bash
python xunlong.py report "主题" \
  --depth overview \
  --model gpt-3.5-turbo
```

**平衡（约10分钟）：**
```bash
python xunlong.py report "主题" \
  --depth standard \
  --model gpt-4o-mini
```

**高质量（约20分钟）：**
```bash
python xunlong.py report "主题" \
  --depth comprehensive \
  --model gpt-4o
```

## 故障排除

### 问题："未找到相关来源"

**解决方案：**
- 使查询更具体
- 检查网络连接
- 尝试不同的搜索词
- 验证主题是否可搜索

### 问题：报告太短

**解决方案：**
- 增加深度：`--depth comprehensive`
- 添加更多章节：`--sections "章节1,章节2,..."`
- 使用更强大的模型：`--model gpt-4o`

### 问题：缺少引用

**解决方案：**
- 启用严格引用：`--strict-citations`
- 增加来源数量：`--min-sources 15`
- 检查搜索结果质量

### 问题：生成中途失败

**解决方案：**
```bash
# 从检查点恢复
python xunlong.py resume <project-id>

# 检查错误日志
cat storage/<project-id>/logs/generation.log
```

## 下一步

- 了解[小说创作](/zh/guide/features/fiction)
- 探索[PPT制作](/zh/guide/features/ppt)
- 理解[内容迭代](/zh/guide/features/iteration)
- 查看[导出格式](/zh/guide/features/export)
