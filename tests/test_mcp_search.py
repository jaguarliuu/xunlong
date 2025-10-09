"""
MCP

WebMCP
"""

import asyncio
import os
from pathlib import Path
import sys

# 
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from dotenv import load_dotenv

# 
load_dotenv()


async def test_mcp_manager():
    """MCP"""
    from src.mcp.mcp_manager import get_mcp_manager

    logger.info("=" * 60)
    logger.info("1: MCP")
    logger.info("=" * 60)

    manager = get_mcp_manager()

    # 
    all_clients = manager.list_clients()
    logger.info(f"MCP: {all_clients}")

    # 
    enabled_clients = manager.list_enabled_clients()
    logger.info(f"MCP: {enabled_clients}")

    # 
    has_enabled = manager.has_enabled_clients()
    logger.info(f": {has_enabled}")

    return manager


async def test_zhipu_search(manager):
    """Web"""
    logger.info("\n" + "=" * 60)
    logger.info("2: Web")
    logger.info("=" * 60)

    if not manager.has_enabled_clients():
        logger.warning("MCP")
        logger.info(": .env ZHIPU_MCP_API_KEY")
        return

    # 
    query = "2025103 AIGC"
    logger.info(f": {query}")

    result = await manager.search(query, max_results=5)

    logger.info(f"\n: {result.get('status')}")
    logger.info(f": {result.get('source')}")
    logger.info(f": {len(result.get('results', []))}")

    # 
    results = result.get("results", [])
    for i, item in enumerate(results, 1):
        logger.info(f"\n---  {i} ---")
        logger.info(f": {item.get('title', 'N/A')}")
        logger.info(f"URL: {item.get('url', 'N/A')}")
        logger.info(f": {item.get('snippet', 'N/A')[:100]}...")


async def test_web_searcher():
    """Web"""
    logger.info("\n" + "=" * 60)
    logger.info("3: Web")
    logger.info("=" * 60)

    from src.tools.web_searcher import WebSearcher

    # MCP
    searcher = WebSearcher(prefer_mcp=True)

    # 
    query = ""
    logger.info(f": {query}")

    results = await searcher.search(query, max_results=3)

    logger.info(f"\n {len(results)} ")

    # 
    for i, result in enumerate(results, 1):
        logger.info(f"\n---  {i} ---")
        logger.info(f": {result.get('title', 'N/A')}")
        logger.info(f"URL: {result.get('url', 'N/A')}")
        logger.info(f": {result.get('source', 'N/A')}")
        logger.info(f": {result.get('snippet', 'N/A')[:100]}...")


async def test_prompt_instruction():
    """TODO: Add docstring."""
    logger.info("\n" + "=" * 60)
    logger.info("4: ")
    logger.info("=" * 60)

    from src.mcp.mcp_manager import get_mcp_manager

    manager = get_mcp_manager()

    if not manager.has_enabled_clients():
        logger.warning("MCP")
        return

    # 
    query = "2025103 AIGC"
    instruction = manager.get_search_prompt_instruction(query)

    logger.info(f": {query}")
    logger.info(f": {instruction}")


async def main():
    """TODO: Add docstring."""
    logger.info("MCP\n")

    try:
        # 1: MCP
        manager = await test_mcp_manager()

        # 2: 
        await test_zhipu_search(manager)

        # 3: Web
        await test_web_searcher()

        # 4: 
        await test_prompt_instruction()

        logger.info("\n" + "=" * 60)
        logger.info("!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f": {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
