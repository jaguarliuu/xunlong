"""DeepSearch智能体系统安装和设置脚本 - 支持多种大模型（Windows兼容）"""

import os
import sys
import subprocess
import asyncio
import platform
from pathlib import Path


def print_step(step: str):
    """打印安装步骤"""
    print(f"\n🔧 {step}")
    print("-" * 50)


def run_command(command: str, description: str = ""):
    """运行命令"""
    if description:
        print(f"执行: {description}")
    
    print(f"命令: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(f"输出: {result.stdout.strip()}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stderr:
            print(f"错误: {e.stderr.strip()}")
        return False


def get_os_info():
    """获取操作系统信息"""
    system = platform.system()
    return {
        "system": system,
        "is_windows": system == "Windows",
        "is_linux": system == "Linux",
        "is_mac": system == "Darwin"
    }


def check_python_version():
    """检查Python版本"""
    print_step("检查Python版本")
    
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True


def install_dependencies():
    """安装依赖包"""
    print_step("安装Python依赖包")
    
    # 升级pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip"):
        return False
    
    # 安装依赖
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "安装项目依赖"):
        return False
    
    print("✅ 依赖包安装完成")
    return True


def setup_playwright():
    """设置Playwright浏览器"""
    print_step("设置Playwright浏览器")
    
    if not run_command("playwright install chromium", "安装Chromium浏览器"):
        print("⚠️ Playwright浏览器安装失败，可能影响网页搜索功能")
        return False
    
    print("✅ Playwright浏览器设置完成")
    return True


def create_directories():
    """创建必要的目录"""
    print_step("创建项目目录")
    
    directories = [
        "results",
        "results/shots",
        "config",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    return True


def detect_available_llm_providers():
    """检测可用的LLM提供商"""
    print_step("检测可用的LLM提供商")
    
    providers = [
        # (环境变量名, 提供商名称, 描述)
        ("OPENAI_API_KEY", "OpenAI", "GPT-4, GPT-3.5-turbo"),
        ("AZURE_OPENAI_API_KEY", "Azure OpenAI", "企业级OpenAI服务"),
        ("ANTHROPIC_API_KEY", "Anthropic", "Claude系列模型"),
        ("ZHIPU_API_KEY", "智谱AI", "GLM-4等国产大模型"),
        ("DASHSCOPE_API_KEY", "通义千问", "阿里云大模型服务"),
        ("QWEN_API_KEY", "通义千问", "阿里云大模型服务"),
        ("DEEPSEEK_API_KEY", "DeepSeek", "深度求索大模型"),
        ("LLM_API_KEY", "通用LLM", "可用于多种兼容OpenAI API的服务"),
    ]
    
    found_providers = []
    
    for env_key, provider_name, description in providers:
        value = os.getenv(env_key)
        if value:
            print(f"✅ 找到 {provider_name}: {value[:10]}... ({description})")
            found_providers.append((env_key, provider_name))
        else:
            print(f"⚪ 未找到 {env_key} ({provider_name})")
    
    # 检查Ollama
    print(f"\n🔍 检查Ollama本地服务...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ 找到Ollama服务，可用模型: {len(models)} 个")
            if models:
                model_names = [model.get("name", "unknown") for model in models[:3]]
                print(f"   示例模型: {', '.join(model_names)}")
            found_providers.append(("OLLAMA", "Ollama本地服务"))
        else:
            print("⚪ Ollama服务未运行")
    except:
        print("⚪ Ollama服务未运行或未安装")
    
    if not found_providers:
        print("\n❌ 未找到任何可用的LLM提供商！")
        show_env_setup_instructions()
        return False
    
    print(f"\n✅ 找到 {len(found_providers)} 个可用的LLM提供商")
    return True


def show_env_setup_instructions():
    """显示环境变量设置说明"""
    os_info = get_os_info()
    
    print("\n📋 请配置以下环境变量之一:")
    
    if os_info["is_windows"]:
        print("\n🪟 Windows PowerShell 设置方法:")
        print("  # 国产大模型（推荐，便宜好用）")
        print("  $env:DASHSCOPE_API_KEY='your-qwen-api-key'        # 通义千问")
        print("  $env:DEEPSEEK_API_KEY='your-deepseek-api-key'     # DeepSeek")
        print("  $env:ZHIPU_API_KEY='your-zhipu-api-key'           # 智谱AI")
        print("  ")
        print("  # 国外大模型")
        print("  $env:OPENAI_API_KEY='your-openai-api-key'         # OpenAI")
        print("  $env:ANTHROPIC_API_KEY='your-anthropic-api-key'   # Claude")
        print("  ")
        print("  # 通用配置（适用于兼容OpenAI API的服务）")
        print("  $env:LLM_API_KEY='your-api-key'")
        print("  $env:LLM_BASE_URL='your-base-url'")
        print("  ")
        print("🪟 Windows CMD 设置方法:")
        print("  set DASHSCOPE_API_KEY=your-qwen-api-key")
        print("  set DEEPSEEK_API_KEY=your-deepseek-api-key")
        print("  ")
        print("🪟 Windows 永久设置（推荐）:")
        print("  1. 按 Win+R，输入 sysdm.cpl")
        print("  2. 点击'环境变量'按钮")
        print("  3. 在'用户变量'中点击'新建'")
        print("  4. 变量名: DASHSCOPE_API_KEY")
        print("  5. 变量值: your-qwen-api-key")
        print("  6. 重启终端生效")
        
    else:
        print("\n🐧 Linux/Mac 设置方法:")
        print("  # 临时设置")
        print("  export DASHSCOPE_API_KEY='your-qwen-api-key'      # 通义千问")
        print("  export DEEPSEEK_API_KEY='your-deepseek-api-key'   # DeepSeek")
        print("  export ZHIPU_API_KEY='your-zhipu-api-key'         # 智谱AI")
        print("  ")
        print("  # 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）")
        print("  echo 'export DASHSCOPE_API_KEY=\"your-qwen-api-key\"' >> ~/.bashrc")
        print("  source ~/.bashrc")
    
    print("\n💡 推荐使用国产大模型:")
    print("  - 通义千问: https://dashscope.aliyuncs.com/")
    print("  - DeepSeek: https://platform.deepseek.com/")
    print("  - 智谱AI: https://open.bigmodel.cn/")
    print("  ")
    print("🏠 或使用免费的本地模型:")
    print("  - 下载安装 Ollama: https://ollama.ai/")
    print("  - 运行: ollama serve")
    print("  - 下载模型: ollama pull llama3")


def set_env_var_interactive():
    """交互式设置环境变量"""
    print_step("交互式环境变量设置")
    
    os_info = get_os_info()
    
    print("🎯 让我们为你设置API密钥")
    print("请选择你要使用的大模型提供商:")
    print("1. 通义千问 (Qwen) - 推荐，性价比高")
    print("2. DeepSeek - 编程能力强，价格便宜")
    print("3. 智谱AI (GLM) - 国产大模型，功能全面")
    print("4. OpenAI - GPT-4，功能强大")
    print("5. 跳过设置，稍后手动配置")
    
    try:
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "5":
            print("⚪ 跳过设置，请稍后手动配置环境变量")
            return False
        
        provider_map = {
            "1": ("DASHSCOPE_API_KEY", "通义千问", "请访问 https://dashscope.aliyuncs.com/ 获取API密钥"),
            "2": ("DEEPSEEK_API_KEY", "DeepSeek", "请访问 https://platform.deepseek.com/ 获取API密钥"),
            "3": ("ZHIPU_API_KEY", "智谱AI", "请访问 https://open.bigmodel.cn/ 获取API密钥"),
            "4": ("OPENAI_API_KEY", "OpenAI", "请访问 https://platform.openai.com/ 获取API密钥")
        }
        
        if choice not in provider_map:
            print("❌ 无效选择")
            return False
        
        env_key, provider_name, instruction = provider_map[choice]
        
        print(f"\n📝 设置 {provider_name} API密钥")
        print(f"💡 {instruction}")
        
        api_key = input(f"\n请输入你的 {provider_name} API密钥: ").strip()
        
        if not api_key:
            print("❌ API密钥不能为空")
            return False
        
        # 设置环境变量（当前会话）
        os.environ[env_key] = api_key
        
        # 显示永久设置方法
        print(f"\n✅ 已为当前会话设置 {env_key}")
        print("\n💾 要永久保存此设置，请执行以下命令:")
        
        if os_info["is_windows"]:
            print(f"  PowerShell: $env:{env_key}='{api_key}'")
            print(f"  CMD: set {env_key}={api_key}")
            print("  或通过系统环境变量设置（推荐）")
        else:
            print(f"  export {env_key}='{api_key}'")
            print(f"  echo 'export {env_key}=\"{api_key}\"' >> ~/.bashrc")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚪ 用户取消设置")
        return False
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        return False


def recommend_llm_config():
    """推荐LLM配置"""
    print_step("推荐LLM配置")
    
    # 检测最佳提供商
    if os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY"):
        recommended = "通义千问 (qwen)"
        print("🎯 推荐使用通义千问，性价比高，中文支持好")
    elif os.getenv("DEEPSEEK_API_KEY"):
        recommended = "DeepSeek (deepseek)"
        print("🎯 推荐使用DeepSeek，编程能力强，价格便宜")
    elif os.getenv("ZHIPU_API_KEY"):
        recommended = "智谱AI (zhipu)"
        print("🎯 推荐使用智谱AI，国产大模型，功能全面")
    elif os.getenv("OPENAI_API_KEY"):
        recommended = "OpenAI (openai)"
        print("🎯 推荐使用OpenAI，功能强大，生态完善")
    elif os.getenv("LLM_API_KEY"):
        recommended = "通用LLM配置"
        print("🎯 检测到通用LLM配置，请确保兼容OpenAI API格式")
    else:
        recommended = "Ollama本地服务"
        print("🎯 推荐使用Ollama本地服务，免费且隐私安全")
    
    print(f"✅ 当前推荐配置: {recommended}")
    
    # 显示配置建议
    print("\n💡 配置建议:")
    print("  - 开发测试: 使用通义千问或DeepSeek，成本低")
    print("  - 生产环境: 使用GPT-4或Claude，质量高")
    print("  - 隐私要求: 使用Ollama本地模型")
    print("  - 中文场景: 优先选择国产大模型")
    
    return True


async def test_basic_functionality():
    """测试基本功能"""
    print_step("测试基本功能")
    
    try:
        # 导入主要模块
        sys.path.append(str(Path(__file__).parent / "src"))
        
        from src.deep_search_agent import DeepSearchAgent
        
        print("✅ 成功导入DeepSearchAgent")
        
        # 创建智能体实例
        agent = DeepSearchAgent()
        print("✅ 成功创建智能体实例")
        
        # 获取系统状态
        status = agent.get_system_status()
        print(f"✅ 系统状态正常，共有 {status['llm_manager']['total_configs']} 个LLM配置")
        
        # 显示可用提供商
        available_providers = status['llm_manager']['available_providers']
        print(f"✅ 检测到 {len(available_providers)} 个LLM提供商:")
        
        for provider, info in available_providers.items():
            status_icon = "✅" if info['status'] == "可用" else "⚪"
            print(f"   {status_icon} {provider}: {info['status']} ({info['default_model']})")
        
        # 检查提示词
        prompts = agent.llm_manager.get_prompt_manager().list_prompts()
        print(f"✅ 提示词加载成功，共 {len(prompts)} 个提示词")
        
        # 测试连接（如果有可用的提供商）
        available_count = sum(1 for info in available_providers.values() if info['status'] == "可用")
        if available_count > 0:
            try:
                print("🔍 测试LLM连接...")
                answer = await agent.quick_answer("你好，请回复'测试成功'")
                print(f"✅ LLM连接测试成功: {answer[:50]}...")
            except Exception as e:
                print(f"⚠️ LLM连接测试失败: {e}")
                print("   这可能是API密钥、网络或配置问题")
        else:
            print("⚠️ 没有可用的LLM提供商，跳过连接测试")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_usage_examples():
    """显示使用示例"""
    print_step("使用示例")
    
    os_info = get_os_info()
    
    print("🚀 快速开始:")
    if os_info["is_windows"]:
        print("  python main_agent.py                              # 运行演示")
        print("  python -m src.cli_agent search \"人工智能发展趋势\"   # CLI搜索")
        print("  python -m src.cli_agent quick \"什么是机器学习？\"    # 快速回答")
        print("  python -m src.cli_agent status                    # 查看系统状态")
        print("  python -m src.api_agent                           # 启动API服务")
    else:
        print("  python main_agent.py                              # 运行演示")
        print("  python -m src.cli_agent search '人工智能发展趋势'   # CLI搜索")
        print("  python -m src.cli_agent quick '什么是机器学习？'    # 快速回答")
        print("  python -m src.cli_agent status                    # 查看系统状态")
        print("  python -m src.api_agent                           # 启动API服务")
    
    print("\n📖 Python SDK:")
    print("  from src.deep_search_agent import DeepSearchAgent")
    print("  agent = DeepSearchAgent()")
    print("  result = await agent.search('查询内容')")
    print("  answer = await agent.quick_answer('问题')")
    
    print("\n🌐 API服务:")
    print("  启动: python -m src.api_agent")
    print("  文档: http://localhost:8000/docs")
    print("  健康检查: http://localhost:8000/health")


def main():
    """主安装流程"""
    os_info = get_os_info()
    
    print("🚀 DeepSearch智能体系统安装程序")
    print("   支持多种大模型: OpenAI, Claude, 通义千问, DeepSeek, 智谱AI, Ollama等")
    print(f"   当前系统: {os_info['system']}")
    print("=" * 70)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 创建目录
    if not create_directories():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败，请检查网络连接和权限")
        sys.exit(1)
    
    # 设置Playwright
    setup_playwright()  # 不强制要求成功
    
    # 检测LLM提供商
    llm_available = detect_available_llm_providers()
    
    # 如果没有找到提供商，提供交互式设置
    if not llm_available:
        print("\n🤔 是否要现在设置API密钥？")
        try:
            setup_now = input("输入 y 进行设置，或按回车跳过: ").strip().lower()
            if setup_now in ['y', 'yes', '是']:
                if set_env_var_interactive():
                    llm_available = True
        except KeyboardInterrupt:
            print("\n⚪ 跳过设置")
    
    # 推荐配置
    if llm_available:
        recommend_llm_config()
    
    # 测试基本功能
    print_step("运行基本功能测试")
    
    try:
        test_result = asyncio.run(test_basic_functionality())
        
        if test_result:
            print("\n🎉 安装完成！")
            print("=" * 70)
            print("✅ DeepSearch智能体系统已成功安装和配置")
            
            if llm_available:
                show_usage_examples()
            else:
                print("\n⚠️ 请先配置LLM API密钥后再使用:")
                show_env_setup_instructions()
                print("\n  然后运行: python main_agent.py")
            
        else:
            print("\n❌ 安装过程中出现问题，请检查错误信息")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()