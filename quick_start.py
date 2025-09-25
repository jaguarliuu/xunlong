"""DeepSearch 快速启动脚本"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 10):
        print("❌ 需要Python 3.10或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version}")
    return True


def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def install_playwright():
    """安装Playwright浏览器"""
    print("🌐 安装Playwright浏览器...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True, text=True)
        print("✅ Playwright浏览器安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Playwright安装失败: {e}")
        return False


def create_directories():
    """创建必要的目录"""
    print("📁 创建目录结构...")
    directories = ["shots", "logs", "temp"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ 目录创建完成")


async def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试基本功能...")
    
    try:
        from src.config import DeepSearchConfig
        from src.pipeline import DeepSearchPipeline
        
        # 创建配置
        config = DeepSearchConfig(
            headless=True,
            topk=1,  # 只测试1个结果
            shots_dir="./shots"
        )
        
        # 创建管道
        pipeline = DeepSearchPipeline(config)
        
        # 执行简单搜索
        result = await pipeline.search("GitHub")
        
        if result.items and result.success_count > 0:
            print("✅ 基本功能测试通过")
            print(f"   - 成功抓取: {result.success_count} 个结果")
            print(f"   - 执行时间: {result.execution_time:.2f}s")
            return True
        else:
            print("❌ 基本功能测试失败: 未能成功抓取结果")
            return False
            
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False


def show_usage_examples():
    """显示使用示例"""
    print("\n" + "="*60)
    print("🎉 DeepSearch 安装完成！")
    print("="*60)
    
    print("\n📖 使用方法:")
    
    print("\n1️⃣ CLI 命令行使用:")
    print("   python main.py search \"Python教程\"")
    print("   python main.py search \"机器学习\" --topk 10 --no-headless")
    print("   python main.py search \"AI发展\" --output results.json")
    
    print("\n2️⃣ API 服务使用:")
    print("   启动服务: python run_api.py")
    print("   访问文档: http://localhost:8000/docs")
    print("   搜索接口: http://localhost:8000/search?q=查询词&k=5")
    
    print("\n3️⃣ 运行示例:")
    print("   python examples/basic_usage.py")
    print("   python test_deepsearch.py")
    
    print("\n4️⃣ 使用Makefile:")
    print("   make help          # 查看所有命令")
    print("   make run-cli       # 运行CLI示例")
    print("   make run-api       # 启动API服务")
    print("   make test          # 运行测试")
    
    print("\n📁 项目结构:")
    print("   src/               # 源代码")
    print("   docs/              # 文档")
    print("   examples/          # 使用示例")
    print("   shots/             # 截图保存目录")
    print("   main.py            # CLI入口")
    print("   run_api.py         # API入口")
    
    print("\n⚙️ 配置选项:")
    print("   环境变量 BROWSER_HEADLESS=true/false")
    print("   环境变量 DEEPSEARCH_TOPK=5")
    print("   环境变量 DEEPSEARCH_SHOTS_DIR=./shots")


def main():
    """主函数"""
    print("🚀 DeepSearch 快速启动")
    print("="*40)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_dependencies():
        print("\n💡 提示: 请手动运行以下命令安装依赖:")
        print("   pip install -r requirements.txt")
        return
    
    # 安装Playwright
    if not install_playwright():
        print("\n💡 提示: 请手动运行以下命令安装Playwright:")
        print("   python -m playwright install chromium")
        return
    
    # 创建目录
    create_directories()
    
    # 测试基本功能
    print("\n🧪 正在测试基本功能...")
    try:
        success = asyncio.run(test_basic_functionality())
        if not success:
            print("⚠️ 基本功能测试未通过，但安装已完成")
    except Exception as e:
        print(f"⚠️ 无法运行功能测试: {e}")
        print("但安装过程已完成，您可以手动测试功能")
    
    # 显示使用示例
    show_usage_examples()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ 安装被用户中断")
    except Exception as e:
        print(f"\n❌ 安装过程中出现错误: {e}")
        import traceback
        traceback.print_exc()