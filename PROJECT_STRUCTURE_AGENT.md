# DeepSearch智能体系统项目结构

## 📁 完整项目结构

```
deepsearch-codebuddy/
├── 📄 README.md                     # 项目说明文档
├── 📄 requirements.txt              # Python依赖包
├── 📄 main_agent.py                 # 智能体系统主入口
├── 📄 PROJECT_STRUCTURE_AGENT.md    # 智能体系统项目结构文档
│
├── 📁 src/                          # 源代码目录
│   ├── 📄 __init__.py
│   ├── 📄 config.py                 # 基础配置管理
│   ├── 📄 pipeline.py               # 搜索管道
│   ├── 📄 browser.py                # 浏览器控制
│   ├── 📄 extractor.py              # 内容提取
│   ├── 📄 deep_search_agent.py      # 主智能体系统
│   ├── 📄 cli_agent.py              # CLI接口
│   ├── 📄 api_agent.py              # API接口
│   │
│   ├── 📁 searcher/                 # 搜索引擎模块
│   │   ├── 📄 __init__.py
│   │   └── 📄 duckduckgo.py         # DuckDuckGo搜索实现
│   │
│   ├── 📁 llm/                      # LLM模块
│   │   ├── 📄 __init__.py           # LLM模块导出
│   │   ├── 📄 config.py             # LLM配置管理
│   │   ├── 📄 client.py             # 统一LLM客户端
│   │   ├── 📄 prompts.py            # 提示词管理系统
│   │   └── 📄 manager.py            # LLM管理器
│   │
│   └── 📁 agents/                   # 智能体模块
│       ├── 📄 __init__.py           # 智能体模块导出
│       ├── 📄 base.py               # 智能体基类
│       ├── 📄 query_optimizer.py    # 查询优化智能体
│       ├── 📄 search_analyzer.py    # 搜索分析智能体
│       ├── 📄 content_synthesizer.py # 内容综合智能体
│       └── 📄 coordinator.py        # 智能体协调器(LangGraph)
│
├── 📁 prompts/                      # 提示词文件目录
│   ├── 📁 agents/                   # 智能体提示词
│   │   ├── 📁 query_optimizer/
│   │   │   └── 📄 system.yaml       # 查询优化智能体系统提示词
│   │   ├── 📁 search_analyzer/
│   │   │   └── 📄 system.yaml       # 搜索分析智能体系统提示词
│   │   └── 📁 content_synthesizer/
│   │       └── 📄 system.yaml       # 内容综合智能体系统提示词
│   ├── 📁 tasks/
│   │   └── 📄 deep_search.yaml      # 深度搜索任务提示词
│   └── 📁 tools/
│       └── 📄 web_search.yaml       # 网页搜索工具提示词
│
├── 📁 config/                       # 配置文件目录
│   └── 📄 llm_config.yaml           # LLM配置文件
│
├── 📁 tests/                        # 测试文件目录
│   ├── 📄 __init__.py
│   ├── 📄 basic_test_fixed.py       # 基础功能测试
│   └── 📄 test_agents.py            # 智能体系统测试
│
├── 📁 examples/                     # 示例代码目录
│   ├── 📄 __init__.py
│   └── 📄 basic_usage.py            # 基础使用示例
│
├── 📁 results/                      # 输出结果目录
│   ├── 📁 shots/                    # 截图文件
│   └── 📄 .gitkeep
│
└── 📁 docs/                         # 文档目录
    ├── 📄 deepsearch.md             # 原始设计文档
    └── 📄 .gitkeep
```

## 🧩 核心模块说明

### 1. 智能体系统 (`src/agents/`)

#### 🤖 智能体基类 (`base.py`)
- `BaseAgent`: 所有智能体的基类
- `AgentState`: 智能体状态管理
- `AgentMessage`: 智能体间消息传递

#### 🔍 查询优化智能体 (`query_optimizer.py`)
- 分析用户查询意图
- 生成优化的搜索策略
- 提取关键词和同义词
- 制定多层次搜索计划

#### 📊 搜索分析智能体 (`search_analyzer.py`)
- 深度分析搜索结果
- 评估信息质量和可信度
- 提取关键洞察和要点
- 生成结构化分析报告

#### 📝 内容综合智能体 (`content_synthesizer.py`)
- 整合多源信息
- 生成连贯的综合报告
- 优化内容结构和表达
- 提供结论和建议

#### 🎯 智能体协调器 (`coordinator.py`)
- 基于LangGraph的工作流管理
- 智能体间协作调度
- 状态管理和错误处理
- 并行处理优化

### 2. LLM模块 (`src/llm/`)

#### ⚙️ LLM配置 (`config.py`)
- 支持多种LLM提供商
- 灵活的配置管理
- 环境变量集成
- 预定义配置模板

#### 🔌 LLM客户端 (`client.py`)
- 统一的LLM调用接口
- 支持同步和异步调用
- 流式输出支持
- 错误处理和重试机制

#### 📋 提示词管理 (`prompts.py`)
- YAML格式提示词文件
- Jinja2模板支持
- 动态参数渲染
- 提示词缓存和热重载

#### 🎛️ LLM管理器 (`manager.py`)
- 统一管理所有LLM配置
- 客户端连接池
- 配置热更新
- 连接测试和监控

### 3. 接口层

#### 💻 CLI接口 (`cli_agent.py`)
- 命令行工具
- Rich库美化输出
- 批处理支持
- 配置文件支持

#### 🌐 API接口 (`api_agent.py`)
- RESTful API服务
- FastAPI框架
- 自动文档生成
- CORS支持

#### 🐍 Python SDK (`deep_search_agent.py`)
- 主智能体系统类
- 简化的调用接口
- 配置管理
- 状态监控

## 🎨 提示词系统

### 📁 提示词组织结构
```
prompts/
├── agents/           # 智能体系统提示词
│   ├── query_optimizer/
│   ├── search_analyzer/
│   └── content_synthesizer/
├── tasks/            # 任务相关提示词
└── tools/            # 工具使用提示词
```

### 📝 提示词格式
```yaml
name: "智能体名称"
description: "功能描述"
version: "1.0"
content: |
  系统提示词内容...
  支持Jinja2模板: {{ variable_name }}
```

## 🔧 配置系统

### 🎛️ LLM配置 (`config/llm_config.yaml`)
```yaml
default:                    # 默认配置
  provider: "openai"
  model_name: "gpt-4o-mini"
  temperature: 0.7

agents:                     # 智能体专用配置
  query_optimizer:
    temperature: 0.3
  search_analyzer:
    temperature: 0.5
  content_synthesizer:
    model_name: "gpt-4o"
```

## 🔄 工作流程

### 1. LangGraph工作流
```
用户查询 → 查询优化 → 网页搜索 → 结果分析 → 内容综合 → 最终报告
```

### 2. 智能体协作
- **状态共享**: 通过LangGraph状态图共享信息
- **并行处理**: 支持多个智能体并行工作
- **错误恢复**: 智能降级和重试策略
- **监控日志**: 完整的执行日志和状态跟踪

## 🧪 测试系统

### 📋 测试覆盖
- **单元测试**: 各模块功能测试
- **集成测试**: 智能体协作测试
- **端到端测试**: 完整流程测试
- **性能测试**: 响应时间和资源使用

### 🔍 测试工具
- `pytest`: 测试框架
- `asyncio`: 异步测试支持
- 模拟API调用避免实际费用

## 📊 监控和日志

### 📈 系统监控
- 智能体状态监控
- LLM调用统计
- 错误率和成功率
- 响应时间分析

### 📝 日志系统
- 结构化日志输出
- 多级别日志控制
- 文件和控制台输出
- 日志轮转和归档

## 🚀 部署和扩展

### 🐳 容器化部署
- Docker镜像构建
- 环境变量配置
- 健康检查
- 水平扩展支持

### 🔌 扩展性
- 插件化智能体
- 自定义提示词
- 多种LLM后端
- 灵活的配置系统

---

这个智能体系统架构提供了完整的多agent协作能力，结合了传统搜索的广度和AI分析的深度，为用户提供高质量的信息检索和分析服务。