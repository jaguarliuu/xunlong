"""修复版基础功能测试"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


if __name__ == "__main__":
    print("🚀 DeepSearch 基础测试 (修复版)")
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
    else:
        print("\n❌ 部分测试失败，请检查安装")