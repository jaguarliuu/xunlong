# 🐉 XunLong Deep Search Agent System

> *"Exploring the depths of information, from heaven to earth"* - Intelligent deep search and analysis system

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Langfuse](https://img.shields.io/badge/Monitoring-Langfuse-purple.svg)](https://langfuse.com)

## 📖 Overview

**XunLong** is a multi-agent deep search and intelligent analysis system. Like ancient dragon seekers exploring dragon veins, this system dives deep into the ocean of internet information, intelligently decomposes complex queries, executes multi-round deep searches, and generates high-quality analytical reports.

### 🌟 Key Features

- **🧠 Multi-Agent Collaboration** - LangGraph-based orchestration: Task Decomposition → Deep Search → Content Evaluation → Report Generation
- **🔍 Real Browser Search** - Playwright automation supporting DuckDuckGo and more
- **⏰ Time-Aware Processing** - Accurate understanding of time-related queries with date-specific retrieval
- **📊 Intelligent Content Evaluation** - Automatic filtering of irrelevant content ensuring quality and timeliness
- **⚡ Parallel Search Execution** - 5-6x faster with 3-level parallelization
- **📁 Complete Storage System** - Auto-save all intermediate and final results
- **📈 Full Chain Monitoring** - Langfuse integration for complete LLM tracing
- **🎯 Professional Report Generation** - Multiple formats: daily reports, analysis, research papers

## 🏗️ System Architecture

```
XunLong System
├── 🎯 Task Decomposer      # Break down complex queries
├── 🔍 Deep Searcher        # Execute parallel search strategies
├── 📊 Content Evaluator    # Evaluate relevance and quality
├── 📝 Content Synthesizer  # Synthesize information
├── 📄 Report Generator     # Generate structured reports
├── ⏰ Time Tool            # Provide accurate time context
├── 📁 Storage Manager      # Manage project storage
└── 🎭 Coordinator         # Orchestrate agent workflow
```

## 🚀 Quick Start

### Requirements

- Python 3.11+
- Node.js (for Playwright)
- OS: Windows, macOS, Linux

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/xunlong.git
   cd xunlong
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

### Configuration

Edit `.env` file:

```env
# LLM Provider (choose one or more)
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key

# Default Settings
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_LLM_MODEL=deepseek-chat
DEFAULT_LLM_TEMPERATURE=0.7
DEFAULT_LLM_MAX_TOKENS=4000

# Optional: Langfuse Monitoring
LANGFUSE_PUB_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
ENABLE_MONITORING=false

# Browser Settings
BROWSER_HEADLESS=true
```

## 💡 Usage Examples

### Command Line

```bash
# Basic search
python main_agent.py search "artificial intelligence latest developments"

# Specific date query
python main_agent.py search "AI breakthroughs on September 24, 2025"

# Custom output
python main_agent.py search "blockchain applications" --output reports/blockchain.json
```

### Python SDK

```python
from src.deep_search_agent import DeepSearchAgent

# Create agent
agent = DeepSearchAgent()

# Quick answer
answer = await agent.quick_answer("What is a large language model?")

# Deep search
result = await agent.search("AI development trends in 2025")

# Access results
print(result['project_dir'])  # Project directory
print(result['final_report'])  # Final report
```

### API Service

```bash
# Start API server
python run_api.py

# Call API
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI trends", "topk": 5}'
```

## 📁 Project Structure

```
XunLong/
├── 📂 src/                     # Source code
│   ├── agents/                # Agent modules
│   ├── llm/                   # LLM management
│   ├── tools/                 # Utility tools
│   ├── storage/               # Storage system
│   └── monitoring/            # Monitoring
├── 📂 storage/                # Search results (auto-generated)
│   └── [project_id]/
│       ├── metadata.json
│       ├── intermediate/      # Processing steps
│       ├── reports/           # Final reports
│       │   ├── FINAL_REPORT.md
│       │   └── SUMMARY.md
│       └── search_results/    # Search data
├── 📂 prompts/                # Prompt templates
├── 📂 tests/                  # Tests
│   └── legacy/                # Legacy tests
├── 📂 scripts/                # Utility scripts
├── 📂 docs/                   # Documentation
│   ├── INDEX.md               # Documentation index
│   ├── PRIVACY_POLICY.md      # Privacy policy
│   └── archive/               # Archived docs
├── main_agent.py              # Main entry point
├── run_api.py                 # API server
└── README.md                  # This file
```

## 🎯 Features

### 🔍 Deep Search Capabilities

- **Multi-Round Search Strategy** - Adaptive search rounds based on query complexity
- **Intelligent Query Optimization** - Auto-generate optimal search keywords
- **Content Deduplication** - Avoid duplicate information
- **Time Range Filtering** - Support specific time period retrieval
- **Parallel Execution** - 3-level parallelization (tasks → queries → extraction)

### 🤖 Agent Collaboration

- **Intelligent Task Decomposition** - Break complex queries into executable subtasks
- **Parallel Processing** - Execute multiple subtasks simultaneously
- **Result Synthesis** - Auto-merge search results intelligently
- **Quality Assessment** - Evaluate relevance and credibility

### 📊 Professional Reports

- **Daily Reports** - Daily news summaries for specific domains
- **Analysis Reports** - In-depth analysis of topics or events
- **Research Papers** - Academic-level research compilations
- **Custom Formats** - Support multiple output formats

### 📁 Storage System

Every search creates an independent project directory:

```
storage/20251001_213000_ai_developments/
├── metadata.json              # Project metadata
├── intermediate/              # 6 processing steps (JSON)
├── reports/                   # Reports (Markdown)
│   ├── FINAL_REPORT.md       # Main report
│   ├── SUMMARY.md            # Quick summary
│   └── synthesis_report.md
├── search_results/            # Search data (TXT)
└── execution_log.*            # Execution logs
```

**Benefits**:
- ✅ Auto-save all results
- ✅ Multiple formats (JSON, Markdown, TXT)
- ✅ Easy to export and share
- ✅ Complete traceability

### 📈 Performance

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Search Speed | 45-60s | 5-10s | **5-6x faster** |
| Parallel Levels | 1 | 3 | **3x more efficient** |
| Result Visibility | ❌ Hard to find | ✅ Auto-saved | - |
| Cross-Platform | ⚠️ Issues | ✅ Full support | - |

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/

# Unit tests
python -m pytest tests/unit/
```

## 📚 Documentation

- **[Documentation Index](docs/INDEX.md)** - Complete documentation guide
- **[Privacy Policy](docs/PRIVACY_POLICY.md)** - Privacy and data handling
- **[Storage System](docs/archive/STORAGE_SYSTEM.md)** - Storage system guide
- **[Parallel Optimization](docs/archive/PARALLEL_SEARCH_OPTIMIZATION.md)** - Performance guide
- **[Bug Fixes](docs/archive/BUGFIX_SUMMARY.md)** - Bug fix summary

## 🛠️ Development

### Adding New Search Engine

1. Create searcher class in `src/searcher/`
2. Inherit from `BaseSearcher`
3. Implement `search` method
4. Register in `src/tools/web_searcher.py`

### Adding New Agent

1. Create agent class in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement `process` method
4. Register in coordinator

### Custom Report Template

1. Create template in `prompts/agents/report_generator/`
2. Define prompt in YAML format
3. Add report type in `ReportGenerator`

## 🤝 Contributing

We welcome all contributions! Please check [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit fixes
- 🧪 Add tests

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🔒 Privacy

We take privacy seriously. See [Privacy Policy](docs/PRIVACY_POLICY.md) for:
- What data we collect
- How we use it
- How we protect it
- Your rights

**Key Points**:
- ✅ All data stored locally (no remote database)
- ✅ HTTPS for all external connections
- ✅ Open source for transparency
- ✅ Full user control over data

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [Playwright](https://playwright.dev/) - Browser automation
- [Langfuse](https://langfuse.com/) - LLM monitoring
- [Trafilatura](https://trafilatura.readthedocs.io/) - Content extraction

## 📞 Contact

- 📧 Email: contact@xunlong.com
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/xunlong/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/xunlong/issues)

## 🎊 Recent Updates

**Version 2.0** (2025-10-01):
- ✅ 5-6x faster parallel search
- ✅ Complete storage system
- ✅ Cross-platform compatibility
- ✅ Enhanced privacy controls
- ✅ Better documentation

See [RECENT_IMPROVEMENTS.md](docs/archive/RECENT_IMPROVEMENTS.md) for details.

---

<div align="center">

**🐉 XunLong - Making information search as precise as dragon hunting 🐉**

*Built with ❤️ by the XunLong Team*

[Documentation](docs/INDEX.md) · [Privacy Policy](docs/PRIVACY_POLICY.md) · [Contributing](CONTRIBUTING.md)

</div>
