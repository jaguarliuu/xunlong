"""基础功能测试 - 不依赖playwright版本"""

def test_core_modules():
    """测试核心模块"""
    print("🧪 测试核心模块...")
    
    try:
        # 测试配置模块
        from src.config import DeepSearchConfig
        config = DeepSearchConfig()
        print(f"✅ 配置模块: {config.search_engine}, topk={config.topk}")
        
        # 测试数据模型
        from src.models import SearchResult, PageExtract, SearchLink
        print("✅ 数据模型导入成功")
        
        # 测试搜索器
        from src.searcher import DuckDuckGoSearcher
        searcher = DuckDuckGoSearcher(topk=3)
        print(f"✅ 搜索器: {searcher.name}")
        
        # 测试内容抽取器
        from src.extractor import ContentExtractor
        extractor = ContentExtractor()
        print("✅ 内容抽取器创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 核心模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_basic():
    """测试CLI基础功能"""
    print("\n🧪 测试CLI基础功能...")
    
    try:
        from src.cli import app
        print("✅ CLI模块导入成功")
        
        # 测试配置创建
        from src.config import DeepSearchConfig
        test_config = DeepSearchConfig(
            headless=True,
            topk=1,
            search_engine="duckduckgo"
        )
        print(f"✅ 测试配置创建: {test_config.search_engine}")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI测试失败: {e}")
        return False


def test_api_basic():
    """测试API基础功能"""
    print("\n🧪 测试API基础功能...")
    
    try:
        from src.api import app as api_app
        print("✅ API模块导入成功")
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False


def show_next_steps():
    """显示下一步操作"""
    print("\n📖 下一步测试:")
    print("="*40)
    
    print("1. 测试CLI帮助:")
    print("   python main.py --help")
    
    print("\n2. 简单搜索测试:")
    print("   python main.py search \"GitHub\" --topk 1 --verbose")
    
    print("\n3. 启动API服务:")
    print("   python run_api.py")
    
    print("\n4. 运行完整示例:")
    print("   python examples/basic_usage.py")
    
    print("\n⚠️ 注意事项:")
    print("- 首次运行可能需要下载浏览器")
    print("- 确保网络连接正常")
    print("- 某些网站可能有反爬虫机制")


if __name__ == "__main__":
    print("🚀 DeepSearch 基础测试")
    print("="*40)
    
    success = True
    
    # 测试核心模块
    if not test_core_modules():
        success = False
    
    # 测试CLI
    if not test_cli_basic():
        success = False
    
    # 测试API
    if not test_api_basic():
        success = False
    
    if success:
        print("\n🎉 所有基础测试通过！")
        show_next_steps()
    else:
        print("\n❌ 部分测试失败，请检查安装")
        print("\n🔧 故障排除:")
        print("1. 确保所有依赖已安装: pip install -r requirements.txt")
        print("2. 安装浏览器: python -m playwright install chromium")
        print("3. 检查Python版本: python --version (需要3.10+)")