"""
MCP搜索集成测试

测试智谱Web搜索MCP服务的集成
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

# 加载环境变量
load_dotenv()


async def test_mcp_manager():
    """测试MCP管理器"""
    from src.mcp.mcp_manager import get_mcp_manager

    logger.info("=" * 60)
    logger.info("测试1: MCP管理器初始化")
    logger.info("=" * 60)

    manager = get_mcp_manager()

    # 列出所有客户端
    all_clients = manager.list_clients()
    logger.info(f"已注册的MCP客户端: {all_clients}")

    # 列出已启用的客户端
    enabled_clients = manager.list_enabled_clients()
    logger.info(f"已启用的MCP客户端: {enabled_clients}")

    # 检查是否有启用的客户端
    has_enabled = manager.has_enabled_clients()
    logger.info(f"是否有已启用的客户端: {has_enabled}")

    return manager


async def test_zhipu_search(manager):
    """测试智谱Web搜索"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 智谱Web搜索")
    logger.info("=" * 60)

    if not manager.has_enabled_clients():
        logger.warning("没有已启用的MCP客户端，跳过搜索测试")
        logger.info("提示: 请在.env文件中配置 ZHIPU_MCP_API_KEY")
        return

    # 测试搜索
    query = "2025年10月3日 AIGC领域新闻"
    logger.info(f"搜索查询: {query}")

    result = await manager.search(query, max_results=5)

    logger.info(f"\n搜索状态: {result.get('status')}")
    logger.info(f"结果来源: {result.get('source')}")
    logger.info(f"结果数量: {len(result.get('results', []))}")

    # 显示搜索结果
    results = result.get("results", [])
    for i, item in enumerate(results, 1):
        logger.info(f"\n--- 结果 {i} ---")
        logger.info(f"标题: {item.get('title', 'N/A')}")
        logger.info(f"URL: {item.get('url', 'N/A')}")
        logger.info(f"摘要: {item.get('snippet', 'N/A')[:100]}...")


async def test_web_searcher():
    """测试集成的Web搜索器"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 集成的Web搜索器")
    logger.info("=" * 60)

    from src.tools.web_searcher import WebSearcher

    # 创建搜索器（优先使用MCP）
    searcher = WebSearcher(prefer_mcp=True)

    # 执行搜索
    query = "人工智能最新进展"
    logger.info(f"搜索查询: {query}")

    results = await searcher.search(query, max_results=3)

    logger.info(f"\n获得 {len(results)} 个搜索结果")

    # 显示结果
    for i, result in enumerate(results, 1):
        logger.info(f"\n--- 结果 {i} ---")
        logger.info(f"标题: {result.get('title', 'N/A')}")
        logger.info(f"URL: {result.get('url', 'N/A')}")
        logger.info(f"来源: {result.get('source', 'N/A')}")
        logger.info(f"摘要: {result.get('snippet', 'N/A')[:100]}...")


async def test_prompt_instruction():
    """测试提示词指令生成"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4: 提示词指令生成")
    logger.info("=" * 60)

    from src.mcp.mcp_manager import get_mcp_manager

    manager = get_mcp_manager()

    if not manager.has_enabled_clients():
        logger.warning("没有已启用的MCP客户端，跳过测试")
        return

    # 生成提示词指令
    query = "2025年10月3日 AIGC领域新闻"
    instruction = manager.get_search_prompt_instruction(query)

    logger.info(f"查询: {query}")
    logger.info(f"提示词指令: {instruction}")


async def main():
    """主测试函数"""
    logger.info("开始MCP搜索集成测试\n")

    try:
        # 测试1: MCP管理器
        manager = await test_mcp_manager()

        # 测试2: 智谱搜索
        await test_zhipu_search(manager)

        # 测试3: Web搜索器
        await test_web_searcher()

        # 测试4: 提示词指令
        await test_prompt_instruction()

        logger.info("\n" + "=" * 60)
        logger.info("所有测试完成!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
