"""DeepSearch 测试脚本"""

import asyncio
import json
from pathlib import Path

from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline


async def test_search():
    """测试搜索功能"""
    print("🔍 开始测试 DeepSearch...")
    
    # 创建配置
    config = DeepSearchConfig(
        headless=False,  # 使用有头模式便于观察
        topk=3,          # 只抓取3个结果用于测试
        shots_dir="./test_shots"
    )
    
    # 创建管道
    pipeline = DeepSearchPipeline(config)
    
    # 测试查询
    test_queries = [
        "Python web scraping",
        "机器学习入门",
        "2025年人工智能发展趋势"
    ]
    
    for query in test_queries:
        print(f"\n📝 测试查询: {query}")
        
        try:
            result = await pipeline.search(query)
            
            print(f"✅ 搜索完成:")
            print(f"   - 找到结果: {result.total_found}")
            print(f"   - 成功处理: {result.success_count}")
            print(f"   - 处理失败: {result.error_count}")
            print(f"   - 执行时间: {result.execution_time:.2f}s")
            
            # 保存结果
            output_file = f"test_result_{query.replace(' ', '_')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
            
            print(f"   - 结果已保存: {output_file}")
            
            # 显示前2个结果的摘要
            for i, item in enumerate(result.items[:2], 1):
                status = "✓" if not item.error else "✗"
                print(f"   {status} {i}. {item.title[:50]}...")
                if item.text:
                    print(f"      正文: {item.text[:100]}...")
                if item.screenshot_path:
                    print(f"      截图: {item.screenshot_path}")
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
        
        print("-" * 60)


async def test_single_page():
    """测试单页面处理"""
    print("\n🔍 测试单页面处理...")
    
    config = DeepSearchConfig(headless=False)
    pipeline = DeepSearchPipeline(config)
    
    # 测试一个简单的搜索
    result = await pipeline.search("GitHub")
    
    if result.items:
        item = result.items[0]
        print(f"✅ 页面处理测试:")
        print(f"   URL: {item.url}")
        print(f"   标题: {item.title}")
        print(f"   正文长度: {item.length} 字符")
        print(f"   截图: {item.screenshot_path}")
        print(f"   OG图片: {item.og_image_url}")
        print(f"   首图: {item.first_image_url}")
        
        if item.text:
            print(f"   正文预览: {item.text[:200]}...")


if __name__ == "__main__":
    print("🚀 DeepSearch 测试开始")
    print("=" * 60)
    
    # 创建测试目录
    Path("test_shots").mkdir(exist_ok=True)
    
    try:
        # 运行测试
        asyncio.run(test_search())
        asyncio.run(test_single_page())
        
        print("\n🎉 所有测试完成!")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()