"""Windows"""

import os
import sys
import subprocess
from pathlib import Path


def install_with_precompiled():
    """TODO: Add docstring."""
    print(" Windows - ")
    print("="*50)
    
    # pip
    print(" pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        print(" pip")
    except Exception as e:
        print(f" pip: {e}")
    
    # 
    core_packages = [
        "playwright==1.47.0",
        "trafilatura==1.8.0", 
        "beautifulsoup4==4.12.3",
        "pydantic==2.8.2",
        "loguru==0.7.2",
        "typer==0.12.3",
        "requests>=2.28.0"
    ]
    
    print(" ...")
    for package in core_packages:
        try:
            print(f"   {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                          check=True, capture_output=True)
            print(f"   {package} ")
        except Exception as e:
            print(f"   {package} : {e}")
    
    # API
    optional_packages = [
        "fastapi==0.115.0",
        "uvicorn==0.30.0", 
        "tenacity==8.3.0"
    ]
    
    print("\n ...")
    for package in optional_packages:
        try:
            print(f"   {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                          check=True, capture_output=True)
            print(f"   {package} ")
        except Exception as e:
            print(f"   {package} : {e}")
    
    print("\n Playwright...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True)
        print(" Playwright")
    except Exception as e:
        print(f" Playwright: {e}")
        return False
    
    return True


def create_minimal_test():
    """TODO: Add docstring."""
    test_code = '''
"""TODO: Add docstring."""
import asyncio
from src.config import DeepSearchConfig

async def minimal_test():
    print(" ...")
    try:
        config = DeepSearchConfig(headless=True, topk=1)
        print(f" : {config.search_engine}")
        return True
    except Exception as e:
        print(f" : {e}")
        return False

if __name__ == "__main__":
    asyncio.run(minimal_test())
'''
    
    with open("minimal_test.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    print(" : minimal_test.py")


def main():
    """TODO: Add docstring."""
    print(" DeepSearch Windows ")
    print("="*50)
    
    # Python
    if sys.version_info < (3, 10):
        print(" Python 3.10")
        return
    
    print(f" Python: {sys.version}")
    
    # 
    print("\n ...")
    for dir_name in ["shots", "logs", "temp"]:
        Path(dir_name).mkdir(exist_ok=True)
    print(" ")
    
    # 
    if install_with_precompiled():
        print("\n !")
        
        # 
        create_minimal_test()
        
        print("\n :")
        print("1. : python minimal_test.py")
        print("2. : python main.py search \"\" --topk 1 --verbose")
        print("3. ")
        
        print("\n :")
        print("1. Visual Studio Build Tools:")
        print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print("2. conda:")
        print("   conda install playwright beautifulsoup4 pydantic")
        
    else:
        print("\n ")


if __name__ == "__main__":
    main()