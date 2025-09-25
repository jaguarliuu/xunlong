# 🐉 寻龙探索 (XunLong Explorer)

> *"上穷碧落下黄泉，动手动脚找东西"* - 智能深度搜索与分析系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Langfuse](https://img.shields.io/badge/Monitoring-Langfuse-purple.svg)](https://langfuse.com)

## 📖 项目简介

**寻龙探索**是一个基于多智能体协作的深度搜索与智能分析系统。如同古代寻龙师探寻龙脉一般，本系统能够深入互联网的信息海洋，智能分解复杂查询，执行多轮深度搜索，并生成高质量的分析报告。

### 🌟 核心特色

- **🧠 多智能体协作** - 基于LangGraph的智能体编排，任务分解→深度搜索→内容评估→报告生成
- **🔍 真实浏览器搜索** - 使用Playwright自动化，支持DuckDuckGo等搜索引擎
- **⏰ 时间感知处理** - 准确理解时间相关查询，支持特定日期的信息检索
- **📊 智能内容评估** - 自动过滤不相关内容，确保信息质量和时效性
- **📈 全链路监控** - 集成Langfuse，实现LLM调用的完整追踪和分析
- **🎯 专业报告生成** - 支持AI日报、分析报告、研究报告等多种格式

## 🏗️ 系统架构

```
寻龙探索系统
├── 🎯 任务分解智能体    # 将复杂查询分解为可执行子任务
├── 🔍 深度搜索智能体    # 执行多轮搜索策略
├── 📊 内容评估智能体    # 评估内容相关性和时效性
├── 📝 报告生成智能体    # 生成结构化专业报告
├── ⏰ 时间工具         # 提供准确的时间上下文
└── 🎭 协调器          # 管理智能体协作流程
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js (用于Playwright)
- 支持的操作系统：Windows、macOS、Linux

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/xunlong-explorer.git
   cd xunlong-explorer
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入您的API密钥
   ```

4. **运行测试**
   ```bash
   python tests/integration/test_system.py
   ```

### 配置说明

在 `.env` 文件中配置以下参数：

```env
# Langfuse监控配置
LANGFUSE_PUB_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# LLM API配置（任选其一或多个）
DASHSCOPE_API_KEY=your_qwen_api_key          # 通义千问
OPENAI_API_KEY=your_openai_api_key           # OpenAI GPT
ANTHROPIC_API_KEY=your_claude_api_key        # Claude
DEEPSEEK_API_KEY=your_deepseek_api_key       # DeepSeek
ZHIPU_API_KEY=your_zhipu_api_key             # 智谱AI

# 系统配置
DEFAULT_LLM_PROVIDER=qwen                    # 默认LLM提供商
ENABLE_MONITORING=true                       # 启用监控
BROWSER_HEADLESS=false                       # 浏览器模式
```

## 💡 使用示例

### CLI命令行使用

```bash
# 基础搜索
python main_agent.py search "人工智能最新发展"

# 生成AI日报
python main_agent.py search "获取2025年9月24日AIGC领域发生的大事件，输出AI日报" --verbose

# 指定输出文件
python main_agent.py search "区块链技术应用" --output reports/blockchain_analysis.json
```

### Python SDK使用

```python
from src.deep_search_agent import DeepSearchAgent

# 创建智能体
agent = DeepSearchAgent()

# 快速问答
answer = await agent.quick_answer("什么是大语言模型？")

# 深度搜索分析
result = await agent.search("2025年AI发展趋势分析")
print(result['final_report']['report_content'])
```

### API服务使用

```bash
# 启动API服务
python run_api.py

# 调用API
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "人工智能发展趋势", "topk": 5}'
```

## 📁 项目结构

```
寻龙探索/
├── 📂 src/                     # 核心源代码
│   ├── 🤖 agents/             # 智能体模块
│   │   ├── task_decomposer.py  # 任务分解智能体
│   │   ├── deep_searcher.py    # 深度搜索智能体
│   │   ├── content_evaluator.py # 内容评估智能体
│   │   ├── report_generator.py  # 报告生成智能体
│   │   └── coordinator_simple.py # 协调器
│   ├── 🧠 llm/                # LLM管理模块
│   │   ├── client.py          # LLM客户端
│   │   ├── manager.py         # LLM管理器
│   │   └── config.py          # LLM配置
│   ├── 🔧 tools/              # 工具模块
│   │   ├── web_searcher.py    # 网页搜索工具
│   │   ├── content_extractor.py # 内容提取工具
│   │   └── time_tool.py       # 时间工具
│   ├── 📊 monitoring/         # 监控模块
│   │   └── langfuse_monitor.py # Langfuse监控
│   └── 🔍 searcher/           # 搜索引擎模块
│       └── duckduckgo.py      # DuckDuckGo搜索器
├── 📂 tests/                  # 测试模块
│   ├── integration/           # 集成测试
│   └── unit/                  # 单元测试
├── 📂 prompts/                # 提示词模板
│   ├── agents/                # 智能体提示词
│   ├── tasks/                 # 任务提示词
│   └── tools/                 # 工具提示词
├── 📂 results/                # 搜索结果输出
├── 📂 examples/               # 使用示例
├── 📂 docs/                   # 项目文档
└── 📂 config/                 # 配置文件
```

## 🎯 功能特性

### 🔍 深度搜索能力

- **多轮搜索策略** - 根据查询复杂度自动调整搜索轮次
- **智能查询优化** - 自动生成最优搜索关键词
- **内容去重过滤** - 避免重复信息，提高结果质量
- **时间范围限定** - 支持特定时间段的信息检索

### 🤖 智能体协作

- **任务智能分解** - 将复杂查询分解为多个可执行子任务
- **并行处理能力** - 多个子任务并行执行，提高效率
- **结果智能合并** - 自动整合多个搜索结果
- **质量评估机制** - 对搜索结果进行相关性和可信度评估

### 📊 专业报告生成

- **AI日报** - 特定领域的每日资讯汇总
- **分析报告** - 深度分析特定主题或事件
- **研究报告** - 学术级别的研究成果整理
- **自定义格式** - 支持多种输出格式和模板

### 📈 监控与分析

- **实时监控** - 通过Langfuse监控所有LLM调用
- **性能分析** - 分析搜索效率和结果质量
- **成本追踪** - 跟踪API调用成本
- **错误诊断** - 详细的错误日志和诊断信息

## 🛠️ 开发指南

### 添加新的搜索引擎

1. 在 `src/searcher/` 目录下创建新的搜索器类
2. 继承 `BaseSearcher` 基类
3. 实现 `search` 方法
4. 在 `src/tools/web_searcher.py` 中注册新搜索器

### 添加新的智能体

1. 在 `src/agents/` 目录下创建新的智能体类
2. 继承 `BaseAgent` 基类
3. 实现 `process` 方法
4. 在协调器中注册新智能体

### 自定义报告模板

1. 在 `prompts/agents/report_generator/` 目录下创建新模板
2. 使用YAML格式定义提示词
3. 在 `ReportGenerator` 中添加新的报告类型

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行集成测试
python -m pytest tests/integration/

# 运行单元测试
python -m pytest tests/unit/

# 运行特定测试
python tests/integration/test_langfuse_integration.py
```

## 📊 性能指标

- **搜索速度** - 平均单次搜索时间 < 30秒
- **内容质量** - 相关性评分 > 85%
- **系统稳定性** - 99.5% 可用性
- **并发支持** - 支持最多10个并发搜索任务

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 贡献方式

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🧪 添加测试用例

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 多智能体编排框架
- [Playwright](https://playwright.dev/) - 浏览器自动化工具
- [Langfuse](https://langfuse.com/) - LLM监控平台
- [Trafilatura](https://trafilatura.readthedocs.io/) - 网页内容提取

## 📞 联系我们

- 📧 邮箱：contact@xunlong-explorer.com
- 💬 讨论：[GitHub Discussions](https://github.com/your-username/xunlong-explorer/discussions)
- 🐛 问题：[GitHub Issues](https://github.com/your-username/xunlong-explorer/issues)

---

<div align="center">

**🐉 寻龙探索 - 让信息搜索如寻龙探宝般精准高效 🐉**

*Built with ❤️ by the XunLong Team*

</div>