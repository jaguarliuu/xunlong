# DeepSearch 项目结构

## 📁 整理后的项目结构

```
deepsearch-codebuddy/
├── 📁 src/                     # 核心源代码
│   ├── __init__.py            # 包初始化
│   ├── config.py              # 配置管理
│   ├── models.py              # 数据模型
│   ├── browser.py             # 浏览器控制
│   ├── extractor.py           # 内容抽取
│   ├── pipeline.py            # 主流程管道
│   ├── cli.py                 # CLI接口
│   ├── api.py                 # REST API
│   └── 📁 searcher/           # 搜索器模块
│       ├── __init__.py        # 搜索器包初始化
│       ├── base.py            # 搜索器基类
│       └── duckduckgo.py      # DuckDuckGo搜索器
│
├── 📁 tests/                   # 测试模块
│   ├── __init__.py            # 测试包初始化
│   ├── basic_test.py          # 基础功能测试
│   ├── debug_search.py        # 搜索调试工具
│   ├── simple_test.py         # 简单测试
│   ├── minimal_test.py        # 最小测试
│   ├── test_deepsearch.py     # 完整功能测试
│   ├── test_fixed_search.py   # 修复后搜索测试
│   ├── test_headless_issue.py # 无头模式测试
│   └── test_simple_search.py  # 简单搜索测试
│
├── 📁 results/                 # 输出结果目录
│   ├── __init__.py            # 结果包初始化
│   ├── shots/                 # 截图文件目录
│   ├── debug_page.html        # 调试页面
│   ├── debug_screenshot.png   # 调试截图
│   └── *.json                 # 搜索结果JSON文件
│
├── 📁 config/                  # 配置文件目录
│   ├── __init__.py            # 配置包初始化
│   ├── requirements_windows.txt # Windows依赖
│   └── install_windows.py     # Windows安装脚本
│
├── 📁 examples/                # 使用示例
│   ├── basic_usage.py         # 基础使用示例
│   └── api_client.py          # API客户端示例
│
├── 📁 docs/                    # 项目文档
│   ├── deepsearch.md          # 原始设计文档
│   ├── DEPLOYMENT_GUIDE.md    # 部署指南
│   ├── FINAL_USER_GUIDE.md    # 用户使用指南
│   └── PROJECT_SUMMARY.md     # 项目总结
│
├── 📁 logs/                    # 日志文件目录
├── 📁 shots/                   # 默认截图目录（兼容性）
├── 📁 temp/                    # 临时文件目录
│
├── 📄 main.py                  # CLI主入口
├── 📄 run_api.py              # API服务入口
├── 📄 quick_start.py          # 快速启动脚本
├── 📄 project_info.py         # 项目信息脚本
├── 📄 README.md               # 项目说明
├── 📄 requirements.txt        # Python依赖
├── 📄 setup.py                # 安装脚本
├── 📄 Makefile                # 构建脚本
├── 📄 Dockerfile              # Docker配置
└── 📄 .gitignore              # Git忽略文件
```

## 📋 目录说明

### 🔧 核心模块 (`src/`)
- **config.py**: 配置管理，支持环境变量和命令行参数
- **models.py**: 数据模型定义，使用Pydantic
- **browser.py**: 浏览器控制，基于Playwright
- **extractor.py**: 内容抽取，使用trafilatura
- **pipeline.py**: 主流程管道，协调各模块
- **cli.py**: 命令行接口，基于Typer
- **api.py**: REST API接口，基于FastAPI
- **searcher/**: 搜索器模块，支持多种搜索引擎

### 🧪 测试模块 (`tests/`)
- **basic_test.py**: 基础功能测试，验证模块导入
- **test_*.py**: 各种功能测试脚本
- **debug_*.py**: 调试工具，用于问题诊断

### 📊 结果目录 (`results/`)
- **shots/**: 截图文件存放目录
- ***.json**: 搜索结果JSON文件
- **debug_***: 调试相关文件

### ⚙️ 配置目录 (`config/`)
- **requirements_windows.txt**: Windows环境依赖
- **install_windows.py**: Windows安装脚本

### 📚 文档目录 (`docs/`)
- **deepsearch.md**: 原始MVP设计文档
- **DEPLOYMENT_GUIDE.md**: 详细部署指南
- **FINAL_USER_GUIDE.md**: 完整用户使用指南
- **PROJECT_SUMMARY.md**: 项目功能总结

### 🚀 示例目录 (`examples/`)
- **basic_usage.py**: 基础API使用示例
- **api_client.py**: HTTP API客户端示例

## 🎯 使用方式

### 快速开始
```bash
# 1. 基础测试
python tests/basic_test.py

# 2. 搜索功能测试
python tests/test_fixed_search.py

# 3. CLI使用
python main.py search "查询词" --topk 5

# 4. API服务
python run_api.py
```

### 结果文件
- 搜索结果自动保存到 `results/` 目录
- 截图文件保存到 `results/shots/` 目录
- 可通过 `--output` 参数指定输出路径

### 配置管理
- 默认配置在 `src/config.py`
- 环境变量支持 `DEEPSEARCH_` 前缀
- 命令行参数优先级最高

## 🔄 项目整理说明

### 整理前后对比

**整理前**:
- 测试文件散落在根目录
- 结果文件混在项目根目录
- 配置文件位置不统一
- 文档分散存放

**整理后**:
- ✅ 测试文件统一放在 `tests/` 目录
- ✅ 结果文件统一放在 `results/` 目录
- ✅ 配置文件统一放在 `config/` 目录
- ✅ 文档文件统一放在 `docs/` 目录
- ✅ 示例代码统一放在 `examples/` 目录

### 兼容性保证
- 保持原有API接口不变
- 保持CLI命令格式不变
- 自动创建必要的目录结构
- 向后兼容旧的配置路径

## 📈 项目状态

- ✅ **功能完整**: 所有MVP-1功能已实现
- ✅ **结构清晰**: 模块化设计，职责分明
- ✅ **测试完备**: 多层次测试覆盖
- ✅ **文档齐全**: 从设计到使用的完整文档
- ✅ **部署就绪**: 支持多种部署方式

---

**项目已完成整理，结构清晰，可以投入使用！** 🎉