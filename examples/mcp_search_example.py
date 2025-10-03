"""
MCP 搜索服务使用示例

演示如何使用智谱 Web 搜索 MCP 服务
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
from src.mcp.mcp_manager import get_mcp_manager

# 加载环境变量
load_dotenv()


async def example_1_basic_search():
    """示例1: 基础搜索 - 自动选择最佳搜索源"""
    print("\n" + "=" * 60)
    print("示例 1: 基础搜索")
    print("=" * 60)

    # 创建搜索器（优先使用 MCP）
    searcher = WebSearcher(prefer_mcp=True)

    # 执行搜索
    query = "2025年人工智能最新进展"
    print(f"\n搜索查询: {query}\n")

    results = await searcher.search(query, max_results=3)

    # 显示结果
    print(f"获得 {len(results)} 个结果:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   来源: {result['source']}")
        print(f"   摘要: {result['snippet'][:100]}...")
        print()


async def example_2_force_duckduckgo():
    """示例2: 强制使用 DuckDuckGo"""
    print("\n" + "=" * 60)
    print("示例 2: 强制使用 DuckDuckGo")
    print("=" * 60)

    searcher = WebSearcher(prefer_mcp=True)

    query = "Python 编程教程"
    print(f"\n搜索查询: {query} (强制使用 DuckDuckGo)\n")

    results = await searcher.search(
        query,
        max_results=3,
        force_duckduckgo=True  # 强制使用 DuckDuckGo
    )

    print(f"获得 {len(results)} 个结果 (全部来自 DuckDuckGo):\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']} (来源: {result['source']})")


async def example_3_direct_mcp():
    """示例3: 直接使用 MCP Manager"""
    print("\n" + "=" * 60)
    print("示例 3: 直接使用 MCP Manager")
    print("=" * 60)

    manager = get_mcp_manager()

    # 检查 MCP 服务状态
    if not manager.has_enabled_clients():
        print("\n⚠️  未配置 MCP 服务")
        print("请在 .env 文件中设置 ZHIPU_MCP_API_KEY")
        return

    enabled = manager.list_enabled_clients()
    print(f"\n已启用的 MCP 服务: {', '.join(enabled)}\n")

    # 执行搜索
    query = "机器学习算法"
    print(f"搜索查询: {query}\n")

    result = await manager.search(query, max_results=3)

    if result.get("status") == "success":
        print(f"✓ 搜索成功 (来源: {result.get('source')})")
        print(f"获得 {len(result['results'])} 个结果:\n")

        for i, item in enumerate(result['results'], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['url']}")
    else:
        print(f"✗ 搜索失败: {result.get('message')}")


async def example_4_multi_source():
    """示例4: 多源搜索（高级功能）"""
    print("\n" + "=" * 60)
    print("示例 4: 多源搜索")
    print("=" * 60)

    manager = get_mcp_manager()

    if not manager.has_enabled_clients():
        print("\n⚠️  未配置 MCP 服务，跳过此示例")
        return

    query = "深度学习框架对比"
    print(f"\n搜索查询: {query}")
    print("使用所有可用的搜索源...\n")

    result = await manager.multi_source_search(query, max_results=2)

    print(f"总结果数: {result['total_results']}")
    print(f"来源统计: {result['source_stats']}")
    print()

    for i, item in enumerate(result['results'], 1):
        print(f"{i}. {item['title']} (来源: {item['source']})")


async def example_5_prompt_instruction():
    """示例5: 生成 LLM 提示词指令"""
    print("\n" + "=" * 60)
    print("示例 5: 生成 LLM 提示词指令")
    print("=" * 60)

    manager = get_mcp_manager()

    query = "2025年10月3日 AIGC领域新闻"
    instruction = manager.get_search_prompt_instruction(query)

    print(f"\n查询: {query}")
    print(f"LLM 指令: {instruction}")
    print("\n此指令可用于提示 LLM 使用 MCP 搜索工具")


async def main():
    """运行所有示例"""
    print("\n" + "🔍 MCP 搜索服务使用示例 " + "\n")

    # 检查 API Key
    if not os.getenv("ZHIPU_MCP_API_KEY"):
        print("⚠️  注意: 未配置 ZHIPU_MCP_API_KEY")
        print("部分示例将使用 DuckDuckGo 降级搜索")
        print("\n配置方法:")
        print("1. 访问 https://open.bigmodel.cn/ 获取 API Key")
        print("2. 在 .env 文件中添加: ZHIPU_MCP_API_KEY=your_key")
        print()

    try:
        # 运行示例
        await example_1_basic_search()
        await example_2_force_duckduckgo()
        await example_3_direct_mcp()
        await example_4_multi_source()
        await example_5_prompt_instruction()

        print("\n" + "=" * 60)
        print("✓ 所有示例运行完成!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
