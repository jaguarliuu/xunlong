"""DeepSearch """

import os
import sys
import subprocess
import asyncio
from pathlib import Path


def check_python_version():
    """Python"""
    if sys.version_info < (3, 10):
        print(" Python 3.10")
        print(f": {sys.version}")
        return False
    print(f" Python: {sys.version}")
    return True


def install_dependencies():
    """TODO: Add docstring."""
    print(" ...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print(" ")
        return True
    except subprocess.CalledProcessError as e:
        print(f" : {e}")
        print(f": {e.stderr}")
        return False


def install_playwright():
    """Playwright"""
    print(" Playwright...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True, text=True)
        print(" Playwright")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Playwright: {e}")
        return False


def create_directories():
    """TODO: Add docstring."""
    print(" ...")
    directories = ["shots", "logs", "temp"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    print(" ")


async def test_basic_functionality():
    """TODO: Add docstring."""
    print(" ...")
    
    try:
        from src.config import DeepSearchConfig
        from src.pipeline import DeepSearchPipeline
        
        # 
        config = DeepSearchConfig(
            headless=True,
            topk=1,  # 1
            shots_dir="./shots"
        )
        
        # 
        pipeline = DeepSearchPipeline(config)
        
        # 
        result = await pipeline.search("GitHub")
        
        if result.items and result.success_count > 0:
            print(" ")
            print(f"   - : {result.success_count} ")
            print(f"   - : {result.execution_time:.2f}s")
            return True
        else:
            print(" : ")
            return False
            
    except Exception as e:
        print(f" : {e}")
        return False


def show_usage_examples():
    """TODO: Add docstring."""
    print("\n" + "="*60)
    print(" DeepSearch ")
    print("="*60)
    
    print("\n :")
    
    print("\n1 CLI :")
    print("   python main.py search \"Python\"")
    print("   python main.py search \"\" --topk 10 --no-headless")
    print("   python main.py search \"AI\" --output results.json")
    
    print("\n2 API :")
    print("   : python run_api.py")
    print("   : http://localhost:8000/docs")
    print("   : http://localhost:8000/search?q=&k=5")
    
    print("\n3 :")
    print("   python examples/basic_usage.py")
    print("   python test_deepsearch.py")
    
    print("\n4 Makefile:")
    print("   make help          # ")
    print("   make run-cli       # CLI")
    print("   make run-api       # API")
    print("   make test          # ")
    
    print("\n :")
    print("   src/               # ")
    print("   docs/              # ")
    print("   examples/          # ")
    print("   shots/             # ")
    print("   main.py            # CLI")
    print("   run_api.py         # API")
    
    print("\n :")
    print("    BROWSER_HEADLESS=true/false")
    print("    DEEPSEARCH_TOPK=5")
    print("    DEEPSEARCH_SHOTS_DIR=./shots")


def main():
    """TODO: Add docstring."""
    print(" DeepSearch ")
    print("="*40)
    
    # Python
    if not check_python_version():
        return
    
    # 
    if not install_dependencies():
        print("\n : :")
        print("   pip install -r requirements.txt")
        return
    
    # Playwright
    if not install_playwright():
        print("\n : Playwright:")
        print("   python -m playwright install chromium")
        return
    
    # 
    create_directories()
    
    # 
    print("\n ...")
    try:
        success = asyncio.run(test_basic_functionality())
        if not success:
            print(" ")
    except Exception as e:
        print(f" : {e}")
        print("")
    
    # 
    show_usage_examples()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n ")
    except Exception as e:
        print(f"\n : {e}")
        import traceback
        traceback.print_exc()