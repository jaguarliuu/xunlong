"""测试修复后的搜索功能"""

import asyncio
from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline


async def test_search_with_debug():
    """带调试信息的搜索测试"""
    print("🔍 测试修复后的搜索功能")
    print("="*40)
    
    # 创建配置
    config = DeepSearchConfig(
        headless=False,  # 显示浏览器便于观察
        topk=2,
        shots_dir="./test_shots"
    )
    
    # 创建管道
    pipeline = DeepSearchPipeline(config)
    
    # 测试查询列表
    test_queries = [
        "GitHub",
        "Python programming",
        "machine learning"
    ]
    
    for query in test_queries:
        print(f"\n📝 测试查询: {query}")
        print("-" * 30)
        
        try:
            result = await pipeline.search(query)
            
            print(f"✅ 搜索结果:")
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
                        print(f"      内容预览: {item.text[:80]}...")
                    if item.screenshot_path:
                        print(f"      截图: {item.screenshot_path}")
                    if item.error:
                        print(f"      错误: {item.error}")
            else:
                print("   ❌ 未找到有效结果")
            
            # 如果第一个查询成功，就不继续测试了
            if result.success_count > 0:
                print(f"\n🎉 搜索功能正常工作！")
                break
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*40)


if __name__ == "__main__":
    print("🚀 DeepSearch 修复测试")
    
    try:
        asyncio.run(test_search_with_debug())
        
        print("\n📖 如果搜索成功，您可以:")
        print("1. 使用CLI: python main.py search \"查询词\" --topk 3")
        print("2. 启动API: python run_api.py")
        print("3. 运行示例: python examples/basic_usage.py")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()