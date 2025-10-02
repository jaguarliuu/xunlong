# XunLong CLI 使用文档

## 📋 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [命令详解](#命令详解)
  - [report - 报告生成](#report---报告生成)
  - [fiction - 小说创作](#fiction---小说创作)
  - [ppt - PPT生成](#ppt---ppt生成)
  - [ask - 快速问答](#ask---快速问答)
  - [status - 系统状态](#status---系统状态)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 概述

XunLong 是一个智能搜索与创作系统，使用专业的 Click CLI 框架，提供友好的命令行体验。

### 核心特性

✅ **显式类型控制** - 通过命令明确指定输出类型（report/fiction/ppt）
✅ **丰富的参数选项** - 精细控制每个生成过程
✅ **友好的帮助系统** - 每个命令都有详细说明和示例
✅ **前端友好** - 所有参数可直接映射到API接口

---

## 快速开始

### 安装依赖

```bash
pip install click
```

### 基本用法

```bash
# 查看所有命令
python xunlong.py --help

# 查看特定命令帮助
python xunlong.py fiction --help

# 执行命令
python xunlong.py fiction "写一篇推理小说" --genre mystery --length short
```

### 创建快捷方式（可选）

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias xunlong="python /path/to/xunlong.py"

# 使用
xunlong fiction "你的查询"
```

---

## 命令详解

### report - 报告生成

生成深度研究报告。

#### 语法

```bash
python xunlong.py report [OPTIONS] QUERY
```

#### 参数

| 参数 | 短选项 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--type` | `-t` | Choice | comprehensive | 报告类型 |
| `--depth` | `-d` | Choice | deep | 搜索深度 |
| `--max-results` | `-m` | Integer | 20 | 最大搜索结果数 |
| `--verbose` | `-v` | Flag | False | 显示详细过程 |

#### 报告类型

- `comprehensive` - 综合报告（全面分析）
- `daily` - 日报（快速总结）
- `analysis` - 分析报告（深度分析）
- `research` - 研究报告（学术风格）

#### 搜索深度

- `surface` - 浅层搜索（快速，结果较少）
- `medium` - 中等深度（平衡速度和质量）
- `deep` - 深度搜索（全面，耗时较长）

#### 示例

```bash
# 基础使用
python xunlong.py report "人工智能在医疗领域的应用"

# 生成分析报告，深度搜索，最多30个结果
python xunlong.py report "区块链技术发展" --type analysis --depth deep --max-results 30

# 生成日报，显示详细过程
python xunlong.py report "今日AI新闻" -t daily -v

# 简写形式
python xunlong.py report "量子计算" -t research -d medium -m 25 -v
```

---

### fiction - 小说创作

创作各类型小说。

#### 语法

```bash
python xunlong.py fiction [OPTIONS] QUERY
```

#### 参数

| 参数 | 短选项 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--genre` | `-g` | Choice | mystery | 小说类型 |
| `--length` | `-l` | Choice | short | 篇幅长度 |
| `--viewpoint` | `-vp` | Choice | first | 叙事视角 |
| `--constraint` | `-c` | Text (多次) | - | 特殊约束 |
| `--verbose` | `-v` | Flag | False | 显示详细过程 |

#### 小说类型

- `mystery` - 推理小说
- `scifi` - 科幻小说
- `fantasy` - 奇幻小说
- `horror` - 恐怖小说
- `romance` - 爱情小说
- `wuxia` - 武侠小说

#### 篇幅长度

- `short` - 短篇（约5章，5000字）
- `medium` - 中篇（约12章，5000-30000字）
- `long` - 长篇（约30章，30000字以上）

#### 叙事视角

- `first` - 第一人称（"我"）
- `third` - 第三人称（"他/她"）
- `omniscient` - 全知视角（上帝视角）

#### 特殊约束

可多次使用 `-c` 参数指定：

- `暴风雪山庄` - 封闭空间推理
- `密室` - 密室推理
- `本格推理` - 严格遵循本格推理规则
- `孤岛` - 孤岛模式
- `时间循环` - 时间循环设定

#### 示例

```bash
# 基础使用 - 短篇推理小说
python xunlong.py fiction "写一篇推理小说"

# 科幻中篇，第三人称视角
python xunlong.py fiction "太空探险故事" --genre scifi --length medium --viewpoint third

# 密室推理小说，多个约束条件
python xunlong.py fiction "密室杀人案" -g mystery -l short -c "暴风雪山庄" -c "本格推理"

# 从凶手视角的推理小说（使用查询描述视角）
python xunlong.py fiction "写一篇从凶手视角的推理小说，最后揭晓'我是凶手'" -g mystery -vp first -c "密室"

# 恐怖短篇，显示详细过程
python xunlong.py fiction "鬼屋惊魂" -g horror -l short -v
```

---

### ppt - PPT生成

生成演示文稿（功能开发中）。

#### 语法

```bash
python xunlong.py ppt [OPTIONS] QUERY
```

#### 参数

| 参数 | 短选项 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--theme` | `-t` | Choice | business | PPT主题 |
| `--slides` | `-s` | Integer | 10 | 幻灯片数量 |
| `--verbose` | `-v` | Flag | False | 显示详细过程 |

#### PPT主题

- `business` - 商务风格
- `academic` - 学术风格
- `creative` - 创意风格

#### 示例

```bash
# 商务PPT，15页
python xunlong.py ppt "产品介绍" --theme business --slides 15

# 学术PPT
python xunlong.py ppt "研究成果汇报" -t academic -s 20
```

**注意**：此功能正在开发中，敬请期待。

---

### ask - 快速问答

快速问答，不进行深度搜索（功能开发中）。

#### 语法

```bash
python xunlong.py ask [OPTIONS] QUESTION
```

#### 参数

| 参数 | 短选项 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--model` | `-m` | Choice | balanced | 模型选择 |
| `--verbose` | `-v` | Flag | False | 显示详细信息 |

#### 模型选择

- `fast` - 快速模式（速度优先）
- `balanced` - 平衡模式（速度和质量平衡）
- `quality` - 质量模式（质量优先）

#### 示例

```bash
python xunlong.py ask "什么是量子计算？"
python xunlong.py ask "如何学习Python？" --model quality
```

---

### status - 系统状态

查看系统运行状态和配置信息。

#### 语法

```bash
python xunlong.py status
```

#### 示例

```bash
python xunlong.py status
```

#### 输出示例

```
=== XunLong 系统状态 ===

系统: DeepSearch智能体系统
状态: ✓ 运行中

LLM配置: 1 个

可用提供商:
  • deepseek: 可用
  • openai: 未配置
  • anthropic: 未配置
```

---

## 最佳实践

### 1. 报告生成

#### 日常快速总结
```bash
python xunlong.py report "今日AI新闻" -t daily -d surface
```

#### 深度研究报告
```bash
python xunlong.py report "人工智能伦理问题研究" -t research -d deep -m 50 -v
```

#### 技术分析
```bash
python xunlong.py report "GPT-4技术分析" -t analysis -d deep
```

### 2. 小说创作

#### 短篇推理
```bash
python xunlong.py fiction "密室杀人案" -g mystery -l short -c "本格推理"
```

#### 中篇科幻
```bash
python xunlong.py fiction "火星殖民地的故事" -g scifi -l medium -vp third
```

#### 带特殊视角的推理
```bash
python xunlong.py fiction "从凶手视角写一个推理故事" -g mystery -vp first -c "暴风雪山庄" -c "密室"
```

### 3. 组合使用

先生成报告收集资料，再创作小说：

```bash
# 步骤1: 收集推理小说素材
python xunlong.py report "本格推理小说创作技巧" -t research

# 步骤2: 基于素材创作小说
python xunlong.py fiction "写一篇本格推理小说" -g mystery -c "本格推理"
```

---

## 常见问题

### Q1: 如何避免shell参数解析问题？

**问题**：查询包含特殊字符（如分号、引号）时可能无法正确解析

**解决方案**：
1. 使用单引号包裹查询
2. 避免在查询中使用shell特殊字符
3. 使用 `run_fiction_test.py` 等Python脚本

```bash
# 推荐：使用单引号
python xunlong.py fiction '写一篇推理小说，从凶手视角' -g mystery

# 不推荐：包含特殊字符
python xunlong.py fiction "写一篇推理小说;从凶手视角"  # 分号可能有问题
```

### Q2: 如何查看详细执行过程？

使用 `-v` 或 `--verbose` 参数：

```bash
python xunlong.py fiction "推理小说" -g mystery -v
```

### Q3: 生成的内容保存在哪里？

默认保存在 `storage/` 目录下，每次执行会创建一个项目文件夹：

```
storage/
└── 20251002_093058_写一篇推理小说/
    ├── metadata.json
    ├── reports/
    │   ├── FINAL_REPORT.md      # 最终输出
    │   └── SUMMARY.md            # 摘要
    ├── intermediate/             # 中间产物
    └── search_results/           # 搜索结果
```

### Q4: 如何自定义配置？

创建 `config/llm_config.yaml` 文件自定义LLM配置。

### Q5: 命令太长怎么办？

创建shell别名或脚本：

```bash
# ~/.bashrc 或 ~/.zshrc
alias xunlong-fiction="python /path/to/xunlong.py fiction"
alias xunlong-report="python /path/to/xunlong.py report"

# 使用
xunlong-fiction "推理小说" -g mystery -l short
```

---

## 高级用法

### 批量处理

使用shell脚本批量生成：

```bash
#!/bin/bash

# batch_fiction.sh
genres=("mystery" "scifi" "fantasy")

for genre in "${genres[@]}"; do
  python xunlong.py fiction "写一篇${genre}小说" -g ${genre} -l short
done
```

### 集成到工作流

```bash
# Makefile示例
.PHONY: daily-report fiction-create

daily-report:
	python xunlong.py report "今日AI新闻" -t daily

fiction-create:
	python xunlong.py fiction "推理小说" -g mystery -l short -c "密室"
```

---

## 版本信息

查看版本：

```bash
python xunlong.py --version
```

---

## 反馈与支持

- 使用问题：查看 `docs/` 目录下的其他文档
- Bug报告：提交到项目issue
- 功能建议：欢迎提交PR

---

**XunLong CLI v1.0.0** - 让智能创作触手可及 🚀
