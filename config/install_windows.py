"""Windows环境专用安装脚本"""

import os
import sys
import subprocess
from pathlib import Path


def install_with_precompiled():
    """使用预编译包安装"""
    print("🔧 Windows环境安装 - 使用预编译包")
    print("="*50)
    
    # 升级pip
    print("📦 升级pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        print("✅ pip升级完成")
    except Exception as e:
        print(f"⚠️ pip升级失败: {e}")
    
    # 安装核心包（避免编译问题）
    core_packages = [
        "playwright==1.47.0",
        "trafilatura==1.8.0", 
        "beautifulsoup4==4.12.3",
        "pydantic==2.8.2",
        "loguru==0.7.2",
        "typer==0.12.3",
        "requests>=2.28.0"
    ]
    
    print("📦 安装核心包...")
    for package in core_packages:
        try:
            print(f"  安装 {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                          check=True, capture_output=True)
            print(f"  ✅ {package} 安装成功")
        except Exception as e:
            print(f"  ❌ {package} 安装失败: {e}")
    
    # 安装可选包（API相关）
    optional_packages = [
        "fastapi==0.115.0",
        "uvicorn==0.30.0", 
        "tenacity==8.3.0"
    ]
    
    print("\n📦 安装可选包...")
    for package in optional_packages:
        try:
            print(f"  安装 {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                          check=True, capture_output=True)
            print(f"  ✅ {package} 安装成功")
        except Exception as e:
            print(f"  ⚠️ {package} 安装失败（可选包）: {e}")
    
    print("\n🌐 安装Playwright浏览器...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True)
        print("✅ Playwright浏览器安装完成")
    except Exception as e:
        print(f"❌ Playwright安装失败: {e}")
        return False
    
    return True


def create_minimal_test():
    """创建最小化测试"""
    test_code = '''
"""最小化功能测试"""
import asyncio
from src.config import DeepSearchConfig

async def minimal_test():
    print("🧪 最小化测试...")
    try:
        config = DeepSearchConfig(headless=True, topk=1)
        print(f"✅ 配置创建成功: {config.search_engine}")
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(minimal_test())
'''
    
    with open("minimal_test.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    print("📝 创建最小化测试文件: minimal_test.py")


def main():
    """主函数"""
    print("🚀 DeepSearch Windows 安装程序")
    print("="*50)
    
    # 检查Python版本
    if sys.version_info < (3, 10):
        print("❌ 需要Python 3.10或更高版本")
        return
    
    print(f"✅ Python版本: {sys.version}")
    
    # 创建目录
    print("\n📁 创建目录...")
    for dir_name in ["shots", "logs", "temp"]:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ 目录创建完成")
    
    # 安装依赖
    if install_with_precompiled():
        print("\n🎉 安装完成!")
        
        # 创建测试文件
        create_minimal_test()
        
        print("\n📖 下一步:")
        print("1. 运行测试: python minimal_test.py")
        print("2. 简单搜索: python main.py search \"测试\" --topk 1 --verbose")
        print("3. 如果遇到问题，请查看下面的手动安装说明")
        
        print("\n🔧 手动安装说明（如果自动安装失败）:")
        print("1. 安装Visual Studio Build Tools:")
        print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print("2. 或者使用conda环境:")
        print("   conda install playwright beautifulsoup4 pydantic")
        
    else:
        print("\n❌ 自动安装失败，请参考手动安装说明")


if __name__ == "__main__":
    main()