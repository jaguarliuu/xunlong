# 内容迭代

XunLong的迭代系统允许您精炼和修改生成的内容，而无需从头开始。

## 概览

迭代功能：
- 🔄 智能修改现有内容
- 💾 保留上下文和风格
- 📝 针对特定部分或全局更改
- 🗂️ 维护版本历史
- ⚡ 比重新生成更快

## 快速开始

```bash
# 生成初始内容
python xunlong.py report "AI趋势" --depth standard

# 迭代修改
python xunlong.py iterate <project-id> "在结论中添加更多示例"
```

## 修改范围

### 局部范围 📍

**目标：** 单个部分、段落或章节

**用例：**
- 修正拼写错误
- 更新特定数据
- 重写段落
- 添加/删除句子

**示例：**
```bash
python xunlong.py iterate <project-id> \
  "修正第3章第2段的拼写错误"
```

**流程：**
```mermaid
graph LR
    A[识别部分] --> B[提取上下文]
    B --> C[应用修改]
    C --> D[保留周围内容]
    D --> E[更新文档]
```

**速度：** 约30秒

### 部分范围 🎯

**目标：** 多个部分或章节

**用例：**
- 添加新部分
- 重组章节
- 扩展特定主题
- 删除冗余部分

**示例：**
```bash
python xunlong.py iterate <project-id> \
  "在第4、5、6章添加三个案例研究"
```

**流程：**
```mermaid
graph LR
    A[识别部分] --> B[规划更改]
    B --> C[修改各部分]
    C --> D[检查连贯性]
    D --> E[更新文档]
```

**速度：** 约2-5分钟

### 全局范围 🌐

**目标：** 整个文档

**用例：**
- 改变整体语调
- 在全文添加主题
- 重组文档结构
- 更改风格/格式

**示例：**
```bash
python xunlong.py iterate <project-id> \
  "使整个报告更技术化，并在全文添加代码示例"
```

**流程：**
```mermaid
graph LR
    A[分析文档] --> B[规划全局更改]
    B --> C[带上下文重新生成]
    C --> D[验证一致性]
    D --> E[更新文档]
```

**速度：** 约5-10分钟

## 迭代类型

### 添加内容 ➕

**在现有内容中添加新信息**

**示例：**
```bash
# 添加新章节
python xunlong.py iterate <project-id> \
  "在第5章和第6章之间添加关于实施挑战的新章节"

# 添加示例
python xunlong.py iterate <project-id> \
  "在每个主要部分添加真实世界的示例"

# 添加数据
python xunlong.py iterate <project-id> \
  "添加2024年的最新统计数据"
```

### 删除内容 ➖

**删除不需要的部分**

**示例：**
```bash
# 删除部分
python xunlong.py iterate <project-id> \
  "删除关于过时技术的部分"

# 删除重复
python xunlong.py iterate <project-id> \
  "删除第7章中重复的内容"

# 缩短
python xunlong.py iterate <project-id> \
  "将结论缩短为原来的一半"
```

### 修改内容 ✏️

**更改现有内容**

**示例：**
```bash
# 重写部分
python xunlong.py iterate <project-id> \
  "用更正式的语调重写引言"

# 更新信息
python xunlong.py iterate <project-id> \
  "用2025年的数据更新所有统计信息"

# 改进清晰度
python xunlong.py iterate <project-id> \
  "使第3章的解释更易于理解"
```

### 重组内容 🔀

**重新安排结构**

**示例：**
```bash
# 重新排序
python xunlong.py iterate <project-id> \
  "将第8章移到第5章之前"

# 重构
python xunlong.py iterate <project-id> \
  "将长章节拆分为更小的子部分"

# 合并
python xunlong.py iterate <project-id> \
  "将第2章和第3章合并为一个章节"
```

### 风格调整 🎨

**更改语调或格式**

**示例：**
```bash
# 语调
python xunlong.py iterate <project-id> \
  "使语调更加对话化和友好"

# 技术级别
python xunlong.py iterate <project-id> \
  "降低技术术语，使其对初学者更友好"

# 格式
python xunlong.py iterate <project-id> \
  "添加更多标题和要点以提高可读性"
```

## 版本控制

### 自动版本

每次迭代自动创建新版本：

```
storage/<project-id>/
├── version_1.md          # 原始
├── version_2.md          # 第一次迭代
├── version_3.md          # 第二次迭代
└── FINAL_REPORT.md       # 指向最新版本
```

### 版本管理

```bash
# 列出所有版本
python xunlong.py versions <project-id>

# 查看特定版本
python xunlong.py view <project-id> --version 2

# 回滚到之前版本
python xunlong.py rollback <project-id> --to-version 2

# 比较版本
python xunlong.py diff <project-id> --from 1 --to 3
```

### 版本历史

```bash
python xunlong.py history <project-id>
```

**输出：**
```
📚 版本历史

Version 1 (2025-10-05 14:30:22)
  ✓ 初始生成
  - 12,345字
  - 18个部分

Version 2 (2025-10-05 15:45:10)
  ✓ 添加案例研究到第4-6章
  - 15,678字（+3,333）
  - 21个部分（+3）

Version 3 (2025-10-05 16:20:33)
  ✓ 重写结论，使其更技术化
  - 16,234字（+556）
  - 21个部分
```

## 智能功能

### 上下文感知

迭代保持：
- 整体叙述流程
- 现有写作风格
- 引用一致性
- 角色/概念一致性（对于小说）

### 增量更改

```bash
# 不好：需要大量重新生成
python xunlong.py iterate <project-id> \
  "完全重写整个文档"

# 好：增量改进
python xunlong.py iterate <project-id> \
  "在第3部分添加更多技术细节，并澄清第7部分的结论"
```

### 变更跟踪

```bash
# 查看最后的更改
python xunlong.py changes <project-id>
```

**输出：**
```
🔄 最近的更改（版本2 → 版本3）

添加：
  ✓ 第4章：案例研究A
  ✓ 第5章：案例研究B
  ✓ 第6章：案例研究C

修改：
  ↻ 结论：重写为更技术化的语调

删除：
  ✗ 附录A：过时的统计数据
```

## 迭代策略

### 迭代优化

**目标明确：**
```bash
# ✓ 好
python xunlong.py iterate <project-id> \
  "在第2部分添加3个真实公司的示例"

# ✗ 模糊
python xunlong.py iterate <project-id> \
  "改进它"
```

### 增量方法

**逐步完善：**
```bash
# 第一次迭代：结构
python xunlong.py iterate <project-id> \
  "添加案例研究部分"

# 第二次迭代：内容
python xunlong.py iterate <project-id> \
  "在新案例研究部分填充示例"

# 第三次迭代：润色
python xunlong.py iterate <project-id> \
  "改进案例研究中的过渡"
```

### 测试修改

```bash
# 预览更改而不提交
python xunlong.py iterate <project-id> \
  "添加更多示例" \
  --preview

# 如果满意，应用
python xunlong.py iterate <project-id> \
  "添加更多示例"
```

## 特定于内容的迭代

### 报告迭代

```bash
# 添加数据
python xunlong.py iterate <report-id> \
  "添加2025年第一季度的财务数据"

# 更新来源
python xunlong.py iterate <report-id> \
  "用最近6个月的来源更新引用"

# 添加可视化
python xunlong.py iterate <report-id> \
  "在关键部分添加图表和图形"
```

### 小说迭代

```bash
# 角色发展
python xunlong.py iterate <fiction-id> \
  "深化主角在第8-12章的动机"

# 情节调整
python xunlong.py iterate <fiction-id> \
  "使第15章的转折更令人惊讶"

# 一致性
python xunlong.py iterate <fiction-id> \
  "修正第20章中的时间线矛盾"
```

### PPT迭代

```bash
# 幻灯片内容
python xunlong.py iterate <ppt-id> \
  "简化第5-8张幻灯片的要点"

# 视觉效果
python xunlong.py iterate <ppt-id> \
  "向第3张幻灯片添加数据图表"

# 演讲备注
python xunlong.py iterate <ppt-id> \
  "为每张幻灯片添加更详细的演讲备注"
```

## 示例工作流

### 报告精炼

```bash
# 1. 生成初始报告
python xunlong.py report "区块链技术" --depth standard

# 2. 审查并识别差距
cat storage/<project-id>/FINAL_REPORT.md

# 3. 添加缺失的部分
python xunlong.py iterate <project-id> \
  "添加关于安全考虑的部分"

# 4. 扩展关键主题
python xunlong.py iterate <project-id> \
  "扩展共识机制部分，包含更多技术细节"

# 5. 添加示例
python xunlong.py iterate <project-id> \
  "添加真实的区块链实施案例研究"

# 6. 润色
python xunlong.py iterate <project-id> \
  "改进引言和结论之间的流畅性"
```

### 小说改进

```bash
# 1. 生成初稿
python xunlong.py fiction "赛博朋克推理" \
  --chapters 20 \
  --style mystery

# 2. 审查情节
cat storage/<project-id>/chapters/chapter_10.md

# 3. 加强伏笔
python xunlong.py iterate <project-id> \
  "在第3-7章添加更多关于第15章揭示的伏笔"

# 4. 深化角色
python xunlong.py iterate <project-id> \
  "使反派的动机在第12章更有说服力"

# 5. 改善节奏
python xunlong.py iterate <project-id> \
  "在第8-10章加快行动节奏"
```

## 最佳实践

### ✅ 做

- 具体说明您想要什么
- 一次专注于一个或几个更改
- 在重大更改后审查
- 在尝试新想法前保存版本
- 使用预览进行大的修改

### ❌ 不要

- 发出模糊指令
- 试图一次改变所有内容
- 在不审查的情况下迭代多次
- 在没有备份的情况下丢失好版本
- 期望一次迭代完美

### 🎯 提示技巧

**好的提示：**
- "在第4部分添加关于X、Y和Z的3个示例"
- "将第2章中的技术术语简化为外行术语"
- "重写第6章的开头以创造更多悬念"

**不好的提示：**
- "改进它"
- "添加更多内容"
- "使其更好"

## API参考

```bash
python xunlong.py iterate <project-id> <instruction> [options]
```

| 参数 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| `<project-id>` | str | 必需 | 项目标识符 |
| `<instruction>` | str | 必需 | 修改指令 |
| `--scope` | str | `auto` | 修改范围（local/partial/global） |
| `--preview` | flag | `false` | 预览而不应用 |
| `--no-backup` | flag | `false` | 跳过自动备份 |
| `--model` | str | `gpt-4o-mini` | 要使用的LLM模型 |

## 辅助命令

```bash
# 版本管理
python xunlong.py versions <project-id>
python xunlong.py rollback <project-id> --to-version <N>
python xunlong.py diff <project-id> --from <N> --to <M>

# 变更跟踪
python xunlong.py changes <project-id>
python xunlong.py history <project-id>

# 比较
python xunlong.py compare <project-id> <other-project-id>
```

## 故障排除

### 问题：迭代过于激进

**症状：** 更改超出要求

**解决方案：**
```bash
# 指定更窄的范围
python xunlong.py iterate <project-id> \
  "只在第3部分添加示例" \
  --scope local

# 回滚并重试
python xunlong.py rollback <project-id> --to-version <N>
```

### 问题：更改不一致

**症状：** 新内容与现有风格不匹配

**解决方案：**
```bash
# 明确风格
python xunlong.py iterate <project-id> \
  "添加示例，保持相同的正式语调"

# 审查后迭代风格
python xunlong.py iterate <project-id> \
  "使新添加的部分与文档其余部分的风格一致"
```

### 问题：丢失了好版本

**解决方案：**
```bash
# 列出所有版本
python xunlong.py versions <project-id>

# 恢复到好版本
python xunlong.py rollback <project-id> --to-version <N>
```

## 下一步

- 了解[报告生成](/zh/guide/features/report)
- 探索[小说创作](/zh/guide/features/fiction)
- 查看[PPT制作](/zh/guide/features/ppt)
- 学习[导出格式](/zh/guide/features/export)
