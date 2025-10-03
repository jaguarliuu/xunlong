"""
混合搜索示例 - MCP搜索 + 浏览器内容抓取

演示如何使用MCP快速搜索，然后用浏览器获取完整内容和图片
"""

import asyncio
import os
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from dotenv import load_dotenv
from src.tools.web_searcher import WebSearcher

# 加载环境变量
load_dotenv()


async def example_1_full_pipeline():
    """示例1: 完整流程 - MCP搜索 + 浏览器抓取内容和图片"""
    print("\n" + "=" * 70)
    print("示例 1: 完整流程（MCP搜索 + 浏览器抓取）")
    print("=" * 70)

    # 创建搜索器
    searcher = WebSearcher(
        prefer_mcp=True,         # 优先使用MCP搜索
        extract_content=True,    # 使用浏览器抓取完整内容
        extract_images=True      # 提取图片
    )

    # 执行搜索
    query = "2025年人工智能最新突破"
    print(f"\n🔍 搜索查询: {query}")
    print("📝 工作流程:")
    print("   1. 使用MCP搜索获取URL列表（快速、无验证码）")
    print("   2. 使用浏览器访问每个URL抓取完整内容")
    print("   3. 提取文章中的图片\n")

    results = await searcher.search(query, max_results=3)

    # 显示结果
    print(f"\n✅ 获得 {len(results)} 个完整结果:\n")
    for i, result in enumerate(results, 1):
        print(f"{'─' * 70}")
        print(f"📄 结果 {i}: {result['title']}")
        print(f"🔗 URL: {result['url']}")
        print(f"📊 来源: {result['source']}")
        print(f"📝 摘要: {result.get('snippet', '')[:100]}...")

        if result.get('has_full_content'):
            full_content = result.get('full_content', '')
            print(f"📖 完整内容: {len(full_content)} 字符")
            print(f"   预览: {full_content[:200]}...")

            images = result.get('images', [])
            print(f"🖼️  图片数量: {len(images)}")
            for j, img in enumerate(images[:3], 1):
                print(f"   图片 {j}: {img['url']}")
                print(f"          尺寸: {img['width']}x{img['height']}")
        else:
            print(f"⚠️  未获取完整内容: {result.get('fetch_error', '未知错误')}")

        print()


async def example_2_search_only():
    """示例2: 仅搜索，不抓取完整内容（速度更快）"""
    print("\n" + "=" * 70)
    print("示例 2: 仅搜索模式（不抓取完整内容）")
    print("=" * 70)

    # 创建搜索器 - 禁用内容抓取
    searcher = WebSearcher(
        prefer_mcp=True,
        extract_content=False,   # 不抓取完整内容
        extract_images=False     # 不提取图片
    )

    query = "机器学习算法"
    print(f"\n🔍 搜索查询: {query}")
    print("⚡ 快速模式: 只获取标题和摘要\n")

    results = await searcher.search(query, max_results=5)

    print(f"✅ 获得 {len(results)} 个结果:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   {result.get('snippet', '')[:100]}...")
        print()


async def example_3_mixed_mode():
    """示例3: 混合模式 - 先快速搜索，再选择性抓取"""
    print("\n" + "=" * 70)
    print("示例 3: 混合模式（先快速搜索，再选择性抓取）")
    print("=" * 70)

    # 第一步：快速搜索
    searcher_fast = WebSearcher(
        prefer_mcp=True,
        extract_content=False
    )

    query = "深度学习框架比较"
    print(f"\n🔍 第一步: 快速搜索获取候选列表")
    print(f"   查询: {query}\n")

    quick_results = await searcher_fast.search(query, max_results=10)
    print(f"✅ 快速获得 {len(quick_results)} 个候选\n")

    # 显示候选
    print("候选列表:")
    for i, result in enumerate(quick_results, 1):
        print(f"{i}. {result['title']}")

    # 第二步：选择前3个进行完整抓取
    print(f"\n📖 第二步: 对前3个结果抓取完整内容\n")

    searcher_full = WebSearcher(
        prefer_mcp=False,  # 已有URL，不需要再搜索
        extract_content=True,
        extract_images=True
    )

    # 手动抓取前3个
    top_results = quick_results[:3]
    detailed_results = await searcher_full._fetch_full_content_with_browser(top_results)

    print(f"✅ 完成详细抓取:\n")
    for i, result in enumerate(detailed_results, 1):
        print(f"{i}. {result['title']}")
        if result.get('has_full_content'):
            print(f"   内容: {len(result.get('full_content', ''))} 字符")
            print(f"   图片: {result.get('image_count', 0)} 张")
        print()


async def example_4_image_showcase():
    """示例4: 重点展示图片提取功能"""
    print("\n" + "=" * 70)
    print("示例 4: 图片提取展示")
    print("=" * 70)

    searcher = WebSearcher(
        prefer_mcp=True,
        extract_content=True,
        extract_images=True
    )

    query = "AI生成图片技术"
    print(f"\n🔍 搜索: {query}")
    print("🖼️  重点提取文章中的图片\n")

    results = await searcher.search(query, max_results=2)

    total_images = 0
    for i, result in enumerate(results, 1):
        images = result.get('images', [])
        total_images += len(images)

        print(f"\n{'─' * 70}")
        print(f"📄 文章 {i}: {result['title']}")
        print(f"🖼️  提取到 {len(images)} 张图片:\n")

        for j, img in enumerate(images, 1):
            print(f"   {j}. {img['alt'] or '(无描述)'}")
            print(f"      URL: {img['url']}")
            print(f"      尺寸: {img['width']}x{img['height']}")
            print()

    print(f"{'=' * 70}")
    print(f"📊 总计提取 {total_images} 张图片")


async def main():
    """运行所有示例"""
    print("\n" + "🔍 混合搜索示例 - MCP + 浏览器 " + "\n")

    # 检查配置
    if not os.getenv("ZHIPU_MCP_API_KEY"):
        print("⚠️  提示: 未配置 ZHIPU_MCP_API_KEY")
        print("系统将使用 DuckDuckGo 进行搜索（可能遇到验证码）\n")
    else:
        print("✅ 已配置 ZHIPU_MCP_API_KEY，将使用智谱MCP搜索\n")

    try:
        # 运行示例
        await example_1_full_pipeline()
        await example_2_search_only()
        await example_3_mixed_mode()
        await example_4_image_showcase()

        print("\n" + "=" * 70)
        print("✅ 所有示例运行完成!")
        print("=" * 70)

    except Exception as e:
        logger.error(f"示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
