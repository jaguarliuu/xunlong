"""项目信息和结构展示"""

import os
from pathlib import Path


def show_project_structure():
    """显示项目结构"""
    print("📁 DeepSearch 项目结构:")
    print("="*50)
    
    structure = """
deepsearch-codebuddy/
├── 📄 README.md                    # 项目说明文档
├── 📄 requirements.txt             # Python依赖列表
├── 📄 setup.py                     # 安装配置
├── 📄 Dockerfile                   # Docker配置
├── 📄 Makefile                     # 开发工具
├── 📄 .gitignore                   # Git忽略文件
├── 📄 main.py                      # CLI主入口
├── 📄 run_api.py                   # API服务入口
├── 📄 quick_start.py               # 快速启动脚本
├── 📄 test_deepsearch.py           # 测试脚本
├── 📄 project_info.py              # 项目信息
│
├── 📂 src/                         # 源代码目录
│   ├── 📄 __init__.py
│   ├── 📄 config.py                # 配置管理
│   ├── 📄 models.py                # 数据模型
│   ├── 📄 browser.py               # 浏览器控制
│   ├── 📄 extractor.py             # 内容抽取
│   ├── 📄 pipeline.py              # 主流程管道
│   ├── 📄 cli.py                   # CLI接口
│   ├── 📄 api.py                   # REST API
│   └── 📂 searcher/                # 搜索器模块
│       ├── 📄 __init__.py
│       ├── 📄 base.py              # 搜索器基类
│       └── 📄 duckduckgo.py        # DuckDuckGo实现
│
├── 📂 docs/                        # 文档目录
│   └── 📄 deepsearch.md            # 功能设计文档
│
├── 📂 examples/                    # 示例代码
│   ├── 📄 basic_usage.py           # 基本使用示例
│   └── 📄 api_client.py            # API客户端示例
│
└── 📂 shots/                       # 截图保存目录 (自动创建)
    """
    
    print(structure)


def show_feature_overview():
    """显示功能概览"""
    print("\n🔍 功能概览:")
    print("="*50)
    
    features = [
        ("🌐 多搜索引擎", "支持DuckDuckGo，预留Google、Bing扩展"),
        ("📄 智能抽取", "使用trafilatura抽取网页正文内容"),
        ("🖼️ 图片提取", "自动提取og:image和首个图片URL"),
        ("📸 自动截图", "保存每个页面的首屏截图"),
        ("⚙️ 灵活配置", "支持有头/无头模式，可配置抓取数量"),
        ("🚀 并发处理", "支持并发抓取多个页面提高效率"),
        ("💻 CLI接口", "提供命令行工具，支持多种参数"),
        ("🌐 REST API", "提供HTTP API接口，支持Web集成"),
        ("🐳 Docker支持", "提供Docker镜像，便于部署"),
        ("📊 结构化输出", "返回JSON格式的结构化数据")
    ]
    
    for feature, description in features:
        print(f"{feature:<15} {description}")


def show_tech_stack():
    """显示技术栈"""
    print("\n🛠️ 技术栈:")
    print("="*50)
    
    tech_stack = {
        "核心框架": [
            "Python 3.10+",
            "Playwright 1.47.0 (浏览器自动化)",
            "Pydantic 2.8.2 (数据验证)",
            "Loguru 0.7.2 (日志记录)"
        ],
        "内容处理": [
            "trafilatura 1.8.0 (正文抽取)",
            "BeautifulSoup4 4.12.3 (HTML解析)",
            "tenacity 8.3.0 (重试机制)"
        ],
        "接口框架": [
            "Typer 0.12.3 (CLI框架)",
            "FastAPI 0.115.0 (REST API)",
            "Uvicorn 0.30.0 (ASGI服务器)"
        ]
    }
    
    for category, tools in tech_stack.items():
        print(f"\n{category}:")
        for tool in tools:
            print(f"  • {tool}")


def show_usage_commands():
    """显示使用命令"""
    print("\n📖 使用命令:")
    print("="*50)
    
    commands = {
        "安装和设置": [
            "python quick_start.py              # 快速安装和设置",
            "pip install -r requirements.txt    # 安装依赖",
            "python -m playwright install chromium  # 安装浏览器"
        ],
        "CLI使用": [
            "python main.py search \"查询词\"      # 基本搜索",
            "python main.py search \"AI\" --topk 10  # 指定结果数量",
            "python main.py search \"ML\" --no-headless  # 显示浏览器",
            "python main.py search \"DL\" -o result.json  # 保存结果"
        ],
        "API服务": [
            "python run_api.py                  # 启动API服务",
            "curl \"localhost:8000/search?q=AI&k=5\"  # API搜索",
            "curl \"localhost:8000/health\"      # 健康检查"
        ],
        "开发工具": [
            "make help                          # 查看所有命令",
            "make install                       # 安装依赖",
            "make test                          # 运行测试",
            "make run-api                       # 启动API"
        ],
        "示例和测试": [
            "python test_deepsearch.py          # 运行测试",
            "python examples/basic_usage.py     # 基本使用示例",
            "python examples/api_client.py      # API客户端示例"
        ]
    }
    
    for category, cmds in commands.items():
        print(f"\n{category}:")
        for cmd in cmds:
            print(f"  {cmd}")


def show_configuration():
    """显示配置选项"""
    print("\n⚙️ 配置选项:")
    print("="*50)
    
    configs = {
        "环境变量": [
            "BROWSER_HEADLESS=true/false        # 浏览器模式",
            "DEEPSEARCH_TOPK=5                  # 默认抓取数量",
            "DEEPSEARCH_SHOTS_DIR=./shots       # 截图目录",
            "DEEPSEARCH_SEARCH_ENGINE=duckduckgo # 搜索引擎"
        ],
        "CLI参数": [
            "--topk, -k                         # 抓取结果数量",
            "--headless/--no-headless           # 浏览器模式",
            "--engine, -e                       # 搜索引擎",
            "--output, -o                       # 输出文件",
            "--shots-dir                        # 截图目录",
            "--verbose, -v                      # 详细输出"
        ],
        "API参数": [
            "q                                  # 搜索查询词",
            "k                                  # 抓取数量(1-20)",
            "engine                             # 搜索引擎",
            "headless                           # 浏览器模式"
        ]
    }
    
    for category, items in configs.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  {item}")


def check_file_status():
    """检查文件状态"""
    print("\n📋 文件状态检查:")
    print("="*50)
    
    important_files = [
        "README.md",
        "requirements.txt",
        "main.py",
        "run_api.py",
        "src/config.py",
        "src/pipeline.py",
        "src/cli.py",
        "src/api.py",
        "src/searcher/duckduckgo.py",
        "docs/deepsearch.md"
    ]
    
    for file_path in important_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"✅ {file_path:<30} ({size} bytes)")
        else:
            print(f"❌ {file_path:<30} (缺失)")


def main():
    """主函数"""
    print("📊 DeepSearch 项目信息")
    print("="*60)
    
    show_project_structure()
    show_feature_overview()
    show_tech_stack()
    show_usage_commands()
    show_configuration()
    check_file_status()
    
    print("\n" + "="*60)
    print("🎉 项目信息展示完成!")
    print("💡 运行 'python quick_start.py' 开始使用")
    print("="*60)


if __name__ == "__main__":
    main()