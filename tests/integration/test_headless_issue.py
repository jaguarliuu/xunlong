"""测试有头vs无头模式的差异"""

import asyncio
from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline


async def test_both_modes():
    """测试有头和无头模式"""
    print("🧪 测试有头 vs 无头模式差异")
    print("="*50)
    
    query = "Python"
    
    # 测试有头模式
    print("\n1️⃣ 测试有头模式 (headless=False)")
    print("-" * 30)
    
    config_headful = DeepSearchConfig(
        headless=False,
        topk=1,
        shots_dir="./test_shots"
    )
    
    pipeline_headful = DeepSearchPipeline(config_headful)
    
    try:
        result_headful = await pipeline_headful.search(query)
        print(f"✅ 有头模式结果:")
        print(f"   成功: {result_headful.success_count}")
        print(f"   失败: {result_headful.error_count}")
        print(f"   耗时: {result_headful.execution_time:.2f}s")
    except Exception as e:
        print(f"❌ 有头模式失败: {e}")
    
    # 等待一下
    await asyncio.sleep(2)
    
    # 测试无头模式
    print("\n2️⃣ 测试无头模式 (headless=True)")
    print("-" * 30)
    
    config_headless = DeepSearchConfig(
        headless=True,
        topk=1,
        shots_dir="./test_shots"
    )
    
    pipeline_headless = DeepSearchPipeline(config_headless)
    
    try:
        result_headless = await pipeline_headless.search(query)
        print(f"✅ 无头模式结果:")
        print(f"   成功: {result_headless.success_count}")
        print(f"   失败: {result_headless.error_count}")
        print(f"   耗时: {result_headless.execution_time:.2f}s")
    except Exception as e:
        print(f"❌ 无头模式失败: {e}")
    
    print("\n📊 结论:")
    print("如果有头模式成功而无头模式失败，说明DuckDuckGo有反爬虫检测")
    print("建议：CLI默认使用有头模式，或者实现更强的反检测机制")


if __name__ == "__main__":
    print("🔍 DeepSearch 模式对比测试")
    
    try:
        asyncio.run(test_both_modes())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()