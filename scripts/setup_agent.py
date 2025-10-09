"""DeepSearch - Windows"""

import os
import sys
import subprocess
import asyncio
import platform
from pathlib import Path


def print_step(step: str):
    """TODO: Add docstring."""
    print(f"\n {step}")
    print("-" * 50)


def run_command(command: str, description: str = ""):
    """TODO: Add docstring."""
    if description:
        print(f": {description}")
    
    print(f": {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(f": {result.stdout.strip()}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f" : {e}")
        if e.stderr:
            print(f": {e.stderr.strip()}")
        return False


def get_os_info():
    """TODO: Add docstring."""
    system = platform.system()
    return {
        "system": system,
        "is_windows": system == "Windows",
        "is_linux": system == "Linux",
        "is_mac": system == "Darwin"
    }


def check_python_version():
    """Python"""
    print_step("Python")
    
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(" Python 3.8")
        return False
    
    print(" Python")
    return True


def install_dependencies():
    """TODO: Add docstring."""
    print_step("Python")
    
    # pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "pip"):
        return False
    
    # 
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", ""):
        return False
    
    print(" ")
    return True


def setup_playwright():
    """Playwright"""
    print_step("Playwright")
    
    if not run_command("playwright install chromium", "Chromium"):
        print(" Playwright")
        return False
    
    print(" Playwright")
    return True


def create_directories():
    """TODO: Add docstring."""
    print_step("")
    
    directories = [
        "results",
        "results/shots",
        "config",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f" : {directory}")
    
    return True


def detect_available_llm_providers():
    """LLM"""
    print_step("LLM")
    
    providers = [
        # (, , )
        ("OPENAI_API_KEY", "OpenAI", "GPT-4, GPT-3.5-turbo"),
        ("AZURE_OPENAI_API_KEY", "Azure OpenAI", "OpenAI"),
        ("ANTHROPIC_API_KEY", "Anthropic", "Claude"),
        ("ZHIPU_API_KEY", "AI", "GLM-4"),
        ("DASHSCOPE_API_KEY", "", ""),
        ("QWEN_API_KEY", "", ""),
        ("DEEPSEEK_API_KEY", "DeepSeek", ""),
        ("LLM_API_KEY", "LLM", "OpenAI API"),
    ]
    
    found_providers = []
    
    for env_key, provider_name, description in providers:
        value = os.getenv(env_key)
        if value:
            print(f"  {provider_name}: {value[:10]}... ({description})")
            found_providers.append((env_key, provider_name))
        else:
            print(f"  {env_key} ({provider_name})")
    
    # Ollama
    print(f"\n Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f" Ollama: {len(models)} ")
            if models:
                model_names = [model.get("name", "unknown") for model in models[:3]]
                print(f"   : {', '.join(model_names)}")
            found_providers.append(("OLLAMA", "Ollama"))
        else:
            print(" Ollama")
    except:
        print(" Ollama")
    
    if not found_providers:
        print("\n LLM")
        show_env_setup_instructions()
        return False
    
    print(f"\n  {len(found_providers)} LLM")
    return True


def show_env_setup_instructions():
    """TODO: Add docstring."""
    os_info = get_os_info()
    
    print("\n :")
    
    if os_info["is_windows"]:
        print("\n Windows PowerShell :")
        print("  # ")
        print("  $env:DASHSCOPE_API_KEY='your-qwen-api-key'        # ")
        print("  $env:DEEPSEEK_API_KEY='your-deepseek-api-key'     # DeepSeek")
        print("  $env:ZHIPU_API_KEY='your-zhipu-api-key'           # AI")
        print("  ")
        print("  # ")
        print("  $env:OPENAI_API_KEY='your-openai-api-key'         # OpenAI")
        print("  $env:ANTHROPIC_API_KEY='your-anthropic-api-key'   # Claude")
        print("  ")
        print("  # OpenAI API")
        print("  $env:LLM_API_KEY='your-api-key'")
        print("  $env:LLM_BASE_URL='your-base-url'")
        print("  ")
        print(" Windows CMD :")
        print("  set DASHSCOPE_API_KEY=your-qwen-api-key")
        print("  set DEEPSEEK_API_KEY=your-deepseek-api-key")
        print("  ")
        print(" Windows :")
        print("  1.  Win+R sysdm.cpl")
        print("  2. ''")
        print("  3. ''''")
        print("  4. : DASHSCOPE_API_KEY")
        print("  5. : your-qwen-api-key")
        print("  6. ")
        
    else:
        print("\n Linux/Mac :")
        print("  # ")
        print("  export DASHSCOPE_API_KEY='your-qwen-api-key'      # ")
        print("  export DEEPSEEK_API_KEY='your-deepseek-api-key'   # DeepSeek")
        print("  export ZHIPU_API_KEY='your-zhipu-api-key'         # AI")
        print("  ")
        print("  #  ~/.bashrc  ~/.zshrc")
        print("  echo 'export DASHSCOPE_API_KEY=\"your-qwen-api-key\"' >> ~/.bashrc")
        print("  source ~/.bashrc")
    
    print("\n :")
    print("  - : https://dashscope.aliyuncs.com/")
    print("  - DeepSeek: https://platform.deepseek.com/")
    print("  - AI: https://open.bigmodel.cn/")
    print("  ")
    print(" :")
    print("  -  Ollama: https://ollama.ai/")
    print("  - : ollama serve")
    print("  - : ollama pull llama3")


def set_env_var_interactive():
    """TODO: Add docstring."""
    print_step("")
    
    os_info = get_os_info()
    
    print(" API")
    print(":")
    print("1.  (Qwen) - ")
    print("2. DeepSeek - ")
    print("3. AI (GLM) - ")
    print("4. OpenAI - GPT-4")
    print("5. ")
    
    try:
        choice = input("\n (1-5): ").strip()
        
        if choice == "5":
            print(" ")
            return False
        
        provider_map = {
            "1": ("DASHSCOPE_API_KEY", "", " https://dashscope.aliyuncs.com/ API"),
            "2": ("DEEPSEEK_API_KEY", "DeepSeek", " https://platform.deepseek.com/ API"),
            "3": ("ZHIPU_API_KEY", "AI", " https://open.bigmodel.cn/ API"),
            "4": ("OPENAI_API_KEY", "OpenAI", " https://platform.openai.com/ API")
        }
        
        if choice not in provider_map:
            print(" ")
            return False
        
        env_key, provider_name, instruction = provider_map[choice]
        
        print(f"\n  {provider_name} API")
        print(f" {instruction}")
        
        api_key = input(f"\n {provider_name} API: ").strip()
        
        if not api_key:
            print(" API")
            return False
        
        # 
        os.environ[env_key] = api_key
        
        # 
        print(f"\n  {env_key}")
        print("\n :")
        
        if os_info["is_windows"]:
            print(f"  PowerShell: $env:{env_key}='{api_key}'")
            print(f"  CMD: set {env_key}={api_key}")
            print("  ")
        else:
            print(f"  export {env_key}='{api_key}'")
            print(f"  echo 'export {env_key}=\"{api_key}\"' >> ~/.bashrc")
        
        return True
        
    except KeyboardInterrupt:
        print("\n ")
        return False
    except Exception as e:
        print(f" : {e}")
        return False


def recommend_llm_config():
    """LLM"""
    print_step("LLM")
    
    # 
    if os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY"):
        recommended = " (qwen)"
        print(" ")
    elif os.getenv("DEEPSEEK_API_KEY"):
        recommended = "DeepSeek (deepseek)"
        print(" DeepSeek")
    elif os.getenv("ZHIPU_API_KEY"):
        recommended = "AI (zhipu)"
        print(" AI")
    elif os.getenv("OPENAI_API_KEY"):
        recommended = "OpenAI (openai)"
        print(" OpenAI")
    elif os.getenv("LLM_API_KEY"):
        recommended = "LLM"
        print(" LLMOpenAI API")
    else:
        recommended = "Ollama"
        print(" Ollama")
    
    print(f" : {recommended}")
    
    # 
    print("\n :")
    print("  - : DeepSeek")
    print("  - : GPT-4Claude")
    print("  - : Ollama")
    print("  - : ")
    
    return True


async def test_basic_functionality():
    """TODO: Add docstring."""
    print_step("")
    
    try:
        # 
        sys.path.append(str(Path(__file__).parent / "src"))
        
        from src.deep_search_agent import DeepSearchAgent
        
        print(" DeepSearchAgent")
        
        # 
        agent = DeepSearchAgent()
        print(" ")
        
        # 
        status = agent.get_system_status()
        print(f"  {status['llm_manager']['total_configs']} LLM")
        
        # 
        available_providers = status['llm_manager']['available_providers']
        print(f"  {len(available_providers)} LLM:")
        
        for provider, info in available_providers.items():
            status_icon = "" if info['status'] == "" else ""
            print(f"   {status_icon} {provider}: {info['status']} ({info['default_model']})")
        
        # 
        prompts = agent.llm_manager.get_prompt_manager().list_prompts()
        print(f"  {len(prompts)} ")
        
        # 
        available_count = sum(1 for info in available_providers.values() if info['status'] == "")
        if available_count > 0:
            try:
                print(" LLM...")
                answer = await agent.quick_answer("''")
                print(f" LLM: {answer[:50]}...")
            except Exception as e:
                print(f" LLM: {e}")
                print("   API")
        else:
            print(" LLM")
        
        return True
        
    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()
        return False


def show_usage_examples():
    """TODO: Add docstring."""
    print_step("")
    
    os_info = get_os_info()
    
    print(" :")
    if os_info["is_windows"]:
        print("  python main_agent.py                              # ")
        print("  python -m src.cli_agent search \"\"   # CLI")
        print("  python -m src.cli_agent quick \"\"    # ")
        print("  python -m src.cli_agent status                    # ")
        print("  python -m src.api_agent                           # API")
    else:
        print("  python main_agent.py                              # ")
        print("  python -m src.cli_agent search ''   # CLI")
        print("  python -m src.cli_agent quick ''    # ")
        print("  python -m src.cli_agent status                    # ")
        print("  python -m src.api_agent                           # API")
    
    print("\n Python SDK:")
    print("  from src.deep_search_agent import DeepSearchAgent")
    print("  agent = DeepSearchAgent()")
    print("  result = await agent.search('')")
    print("  answer = await agent.quick_answer('')")
    
    print("\n API:")
    print("  : python -m src.api_agent")
    print("  : http://localhost:8000/docs")
    print("  : http://localhost:8000/health")


def main():
    """TODO: Add docstring."""
    os_info = get_os_info()
    
    print(" DeepSearch")
    print("   : OpenAI, Claude, , DeepSeek, AI, Ollama")
    print(f"   : {os_info['system']}")
    print("=" * 70)
    
    # Python
    if not check_python_version():
        sys.exit(1)
    
    # 
    if not create_directories():
        sys.exit(1)
    
    # 
    if not install_dependencies():
        print(" ")
        sys.exit(1)
    
    # Playwright
    setup_playwright()  # 
    
    # LLM
    llm_available = detect_available_llm_providers()
    
    # 
    if not llm_available:
        print("\n API")
        try:
            setup_now = input(" y : ").strip().lower()
            if setup_now in ['y', 'yes', '']:
                if set_env_var_interactive():
                    llm_available = True
        except KeyboardInterrupt:
            print("\n ")
    
    # 
    if llm_available:
        recommend_llm_config()
    
    # 
    print_step("")
    
    try:
        test_result = asyncio.run(test_basic_functionality())
        
        if test_result:
            print("\n ")
            print("=" * 70)
            print(" DeepSearch")
            
            if llm_available:
                show_usage_examples()
            else:
                print("\n LLM API:")
                show_env_setup_instructions()
                print("\n  : python main_agent.py")
            
        else:
            print("\n ")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()