"""简单功能测试"""

def test_imports():
    """测试导入"""
    print("🧪 测试模块导入...")
    
    try:
        import sys
        print(f"✅ Python版本: {sys.version_info.major}.{sys.version_info.minor}")
        
        import playwright
        try:
            from playwright import __version__ as pw_version
            print(f"✅ Playwright版本: {pw_version}")
        except ImportError:
            print("✅ Playwright导入成功（版本信息不可用）")
        
        from src.config import DeepSearchConfig
        print("✅ 配置模块导入成功")
        
        config = DeepSearchConfig()
        print(f"✅ 配置创建成功: {config.search_engine}, topk={config.topk}")
        
        from src.models import SearchResult, PageExtract
        print("✅ 数据模型导入成功")
        
        from src.searcher import DuckDuckGoSearcher
        print("✅ 搜索器导入成功")
        
        print("\n🎉 所有核心模块导入成功！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_help():
    """测试CLI帮助"""
    print("\n🧪 测试CLI帮助...")
    try:
        from src.cli import app
        print("✅ CLI模块导入成功")
        return True
    except Exception as e:
        print(f"❌ CLI测试失败: {e}")
        return False


if __name__ == "__main__":
    print("🚀 DeepSearch 简单测试")
    print("="*40)
    
    success = test_imports()
    if success:
        test_cli_help()
        print("\n✅ 基础测试完成！可以尝试运行搜索功能")
        print("\n📖 下一步测试:")
        print("python main.py search \"GitHub\" --topk 1 --verbose")
    else:
        print("\n❌ 基础测试失败，请检查安装")