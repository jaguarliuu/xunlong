"""简单搜索测试"""

import asyncio
import json
from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline


async def test_simple_search():
    """测试简单搜索功能"""
    print("🔍 测试简单搜索功能")
    print("="*40)
    
    # 创建配置 - 使用有头模式便于观察
    config = DeepSearchConfig(
        headless=False,  # 显示浏览器便于调试
        topk=1,          # 只测试1个结果
        shots_dir="./test_shots"
    )
    
    # 创建管道
    pipeline = DeepSearchPipeline(config)
    
    # 执行搜索
    query = "Python"
    print(f"搜索查询: {query}")
    
    try:
        result = await pipeline.search(query)
        
        print(f"\n✅ 搜索完成:")
        print(f"   查询词: {result.query}")
        print(f"   搜索引擎: {result.engine}")
        print(f"   找到结果: {result.total_found}")
        print(f"   成功处理: {result.success_count}")
        print(f"   处理失败: {result.error_count}")
        print(f"   执行时间: {result.execution_time:.2f}s")
        
        if result.items:
            for i, item in enumerate(result.items, 1):
                status = "✓" if not item.error else "✗"
                print(f"\n   {status} 结果 {i}:")
                print(f"      标题: {item.title}")
                print(f"      URL: {item.url}")
                print(f"      正文长度: {item.length} 字符")
                if item.text:
                    print(f"      内容预览: {item.text[:100]}...")
                if item.screenshot_path:
                    print(f"      截图: {item.screenshot_path}")
                if item.error:
                    print(f"      错误: {item.error}")
        
        # 保存结果
        with open("test_search_result.json", "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
        print(f"\n💾 结果已保存到: test_search_result.json")
        
        return result.success_count > 0
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 DeepSearch 简单搜索测试")
    
    try:
        success = asyncio.run(test_simple_search())
        
        if success:
            print("\n🎉 搜索测试成功！")
            print("\n📖 现在可以尝试:")
            print("1. python main.py search \"你的查询词\" --topk 3")
            print("2. python run_api.py  # 启动API服务")
        else:
            print("\n❌ 搜索测试失败")
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()