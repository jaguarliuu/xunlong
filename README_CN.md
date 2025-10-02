# 🐉 XunLong 深度搜索智能体系统

> *"上穷碧落下黄泉，搜罗信息探龙脉"* - 智能深度搜索与分析系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Langfuse](https://img.shields.io/badge/Monitoring-Langfuse-purple.svg)](https://langfuse.com)

[English](README.md) | 简体中文

## 📖 项目简介

**XunLong（寻龙）** 是一个多智能体深度搜索与智能分析系统。如同寻龙点穴的风水师，本系统能够深入互联网信息的海洋，智能分解复杂查询，执行多轮深度搜索，并生成高质量的分析报告。

### 🌟 核心特性

- **🧠 多智能体协作** - 基于 LangGraph 的编排：任务分解 → 深度搜索 → 内容评估 → 报告生成
- **🔍 真实浏览器搜索** - Playwright 自动化，支持 DuckDuckGo 等搜索引擎
- **⏰ 时间感知处理** - 准确理解时间相关查询，支持特定日期检索
- **📊 智能内容评估** - 自动过滤无关内容，确保信息质量和时效性
- **⚡ 并行搜索执行** - 三级并行化架构，速度提升 5-6 倍
- **📁 完整存储系统** - 自动保存所有中间结果和最终报告
- **📈 全链路监控** - Langfuse 集成，完整的 LLM 调用追踪
- **🎯 专业报告生成** - 多种格式：日报、分析报告、研究论文
- **📖 AI 小说创作** - 支持情节设计、人物塑造、大纲生成的智能小说创作
- **🔧 灵活的命令行工具** - 易用的 CLI 接口，支持多种输出格式

## 🏗️ 系统架构

```
XunLong 系统
├── 🎯 任务分解器        # 分解复杂查询
├── 🔍 深度搜索器        # 执行并行搜索策略
├── 📊 内容评估器        # 评估相关性和质量
├── 📝 内容综合器        # 综合整理信息
├── 📄 报告生成器        # 生成结构化报告
├── ⏰ 时间工具          # 提供准确的时间上下文
├── 📁 存储管理器        # 管理项目存储
└── 🎭 协调器           # 编排智能体工作流
```

## 🚀 快速开始

### 系统要求

- Python 3.11+
- Node.js（用于 Playwright）
- 操作系统：Windows、macOS、Linux

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/xunlong.git
   cd xunlong
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **配置环境**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加你的 API 密钥
   ```

### 环境配置

编辑 `.env` 文件：

```env
# LLM 提供商（选择一个或多个）
DEEPSEEK_API_KEY=你的_deepseek_密钥
OPENAI_API_KEY=你的_openai_密钥
ANTHROPIC_API_KEY=你的_claude_密钥

# 默认设置
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_LLM_MODEL=deepseek-chat
DEFAULT_LLM_TEMPERATURE=0.7
DEFAULT_LLM_MAX_TOKENS=4000

# 可选：Langfuse 监控
LANGFUSE_PUB_KEY=你的公钥
LANGFUSE_SECRET_KEY=你的私钥
LANGFUSE_HOST=https://cloud.langfuse.com
ENABLE_MONITORING=false

# 浏览器设置
BROWSER_HEADLESS=true
```

## 💡 使用示例

### 命令行方式

```bash
# 使用 CLI 工具（推荐）
python xunlong.py search "人工智能最新发展"
python xunlong.py fiction "写一篇暴风雪山庄类型的推理小说"
python xunlong.py report "预制菜市场分析报告"

# 传统方式
python main_agent.py search "2025年9月24日的AI突破"

# 自定义输出
python xunlong.py search "区块链应用" --output reports/blockchain.json
```

### Python SDK

```python
from src.deep_search_agent import DeepSearchAgent

# 创建智能体
agent = DeepSearchAgent()

# 快速回答
answer = await agent.quick_answer("什么是大语言模型？")

# 深度搜索
result = await agent.search("2025年AI发展趋势")

# 访问结果
print(result['project_dir'])   # 项目目录
print(result['final_report'])  # 最终报告
```

### API 服务

```bash
# 启动 API 服务器
python run_api.py

# 调用 API
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI趋势", "topk": 5}'
```

## 📁 项目结构

```
XunLong/
├── 📂 src/                     # 源代码
│   ├── agents/                # 智能体模块
│   │   ├── fiction/          # 小说创作智能体
│   │   └── report/           # 报告生成智能体
│   ├── llm/                   # LLM 管理
│   ├── tools/                 # 工具集
│   ├── storage/               # 存储系统
│   └── monitoring/            # 监控模块
├── 📂 storage/                # 搜索结果（自动生成）
│   └── [project_id]/
│       ├── metadata.json
│       ├── intermediate/      # 处理步骤
│       ├── reports/           # 最终报告
│       │   ├── FINAL_REPORT.md
│       │   └── SUMMARY.md
│       └── search_results/    # 搜索数据
├── 📂 prompts/                # 提示词模板
├── 📂 tests/                  # 测试
│   ├── integration/           # 集成测试
│   ├── unit/                  # 单元测试
│   └── legacy/                # 遗留测试
├── 📂 scripts/                # 工具脚本
├── 📂 docs/                   # 文档
│   ├── INDEX.md               # 文档索引
│   ├── CLI_USAGE.md           # CLI 使用指南
│   ├── API_SPECIFICATION.md   # API 文档
│   ├── PRIVACY_POLICY.md      # 隐私政策
│   └── archive/               # 归档文档
├── 📂 examples/               # 示例代码
├── xunlong.py                 # 主 CLI 入口
├── main_agent.py              # 传统入口
├── run_api.py                 # API 服务器
├── README.md                  # 英文版说明
└── README_CN.md               # 中文版说明（本文件）
```

## 🎯 功能特性

### 🔍 深度搜索能力

- **多轮搜索策略** - 根据查询复杂度自适应搜索轮次
- **智能查询优化** - 自动生成最优搜索关键词
- **内容去重** - 避免重复信息
- **时间范围过滤** - 支持特定时间段检索
- **并行执行** - 三级并行化（任务 → 查询 → 提取）

### 🤖 智能体协作

- **智能任务分解** - 将复杂查询分解为可执行的子任务
- **并行处理** - 同时执行多个子任务
- **结果综合** - 智能合并搜索结果
- **质量评估** - 评估相关性和可信度

### 📊 专业报告

- **日报** - 特定领域的每日新闻摘要
- **分析报告** - 深入分析主题或事件
- **研究论文** - 学术级别的研究汇编
- **自定义格式** - 支持多种输出格式

### 📖 小说创作

- **情节设计** - 智能生成故事情节和转折点
- **人物塑造** - 创建立体的人物形象和背景
- **大纲生成** - 构建完整的章节大纲
- **写作辅助** - 提供写作建议和素材

### 📁 存储系统

每次搜索都会创建独立的项目目录：

```
storage/20251001_213000_ai_developments/
├── metadata.json              # 项目元数据
├── intermediate/              # 6个处理步骤（JSON）
├── reports/                   # 报告（Markdown）
│   ├── FINAL_REPORT.md       # 主报告
│   ├── SUMMARY.md            # 快速摘要
│   └── synthesis_report.md
├── search_results/            # 搜索数据（TXT）
└── execution_log.*            # 执行日志
```

**优势**：
- ✅ 自动保存所有结果
- ✅ 多种格式（JSON、Markdown、TXT）
- ✅ 易于导出和分享
- ✅ 完整可追溯

### 📈 性能表现

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 搜索速度 | 45-60秒 | 5-10秒 | **5-6倍** |
| 并行层级 | 1 | 3 | **3倍效率** |
| 结果可见性 | ❌ 难以查找 | ✅ 自动保存 | - |
| 跨平台支持 | ⚠️ 存在问题 | ✅ 完全支持 | - |

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 集成测试
python -m pytest tests/integration/

# 单元测试
python -m pytest tests/unit/
```

## 📚 文档

- **[文档索引](docs/INDEX.md)** - 完整文档指南
- **[CLI 使用指南](docs/CLI_USAGE.md)** - 命令行工具使用说明
- **[API 规范](docs/API_SPECIFICATION.md)** - API 接口文档
- **[隐私政策](docs/PRIVACY_POLICY.md)** - 隐私和数据处理
- **[存储系统](docs/archive/STORAGE_SYSTEM.md)** - 存储系统指南
- **[并行优化](docs/archive/PARALLEL_SEARCH_OPTIMIZATION.md)** - 性能优化指南

## 🛠️ 开发

### 添加新的搜索引擎

1. 在 `src/searcher/` 中创建搜索器类
2. 继承 `BaseSearcher`
3. 实现 `search` 方法
4. 在 `src/tools/web_searcher.py` 中注册

### 添加新的智能体

1. 在 `src/agents/` 中创建智能体类
2. 继承 `BaseAgent`
3. 实现 `process` 方法
4. 在协调器中注册

### 自定义报告模板

1. 在 `prompts/agents/report_generator/` 中创建模板
2. 使用 YAML 格式定义提示词
3. 在 `ReportGenerator` 中添加报告类型

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 贡献方式

- 🐛 报告错误
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交修复
- 🧪 添加测试

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🔒 隐私

我们非常重视隐私保护。详见[隐私政策](docs/PRIVACY_POLICY.md)了解：
- 我们收集什么数据
- 如何使用数据
- 如何保护数据
- 您的权利

**要点**：
- ✅ 所有数据本地存储（无远程数据库）
- ✅ 所有外部连接使用 HTTPS
- ✅ 开源透明
- ✅ 用户完全控制数据

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 多智能体编排
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Langfuse](https://langfuse.com/) - LLM 监控
- [Trafilatura](https://trafilatura.readthedocs.io/) - 内容提取

## 📞 联系方式

- 📧 邮箱：contact@xunlong.com
- 💬 讨论区：[GitHub Discussions](https://github.com/your-username/xunlong/discussions)
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-username/xunlong/issues)

## 🎊 最近更新

**版本 2.0**（2025-10-01）：
- ✅ 并行搜索速度提升 5-6 倍
- ✅ 完整的存储系统
- ✅ 跨平台兼容性
- ✅ 增强的隐私控制
- ✅ 更完善的文档

详见 [RECENT_IMPROVEMENTS.md](docs/archive/RECENT_IMPROVEMENTS.md)。

**版本 2.1**（2025-10-02）：
- ✅ 新增 AI 小说创作功能
- ✅ 改进的 CLI 工具
- ✅ 协作式报告生成
- ✅ 更好的项目组织

---

<div align="center">

**🐉 XunLong - 让信息搜索如寻龙点穴般精准 🐉**

*用 ❤️ 打造 by XunLong 团队*

[文档](docs/INDEX.md) · [隐私政策](docs/PRIVACY_POLICY.md) · [贡献指南](CONTRIBUTING.md)

</div>
