"""
MCP 

 Web  MCP 
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
from src.tools.web_searcher import WebSearcher
from src.mcp.mcp_manager import get_mcp_manager

# 
load_dotenv()


async def example_1_basic_search():
    """1:  - """
    print("\n" + "=" * 60)
    print(" 1: ")
    print("=" * 60)

    #  MCP
    searcher = WebSearcher(prefer_mcp=True)

    # 
    query = "2025"
    print(f"\n: {query}\n")

    results = await searcher.search(query, max_results=3)

    # 
    print(f" {len(results)} :\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   : {result['source']}")
        print(f"   : {result['snippet'][:100]}...")
        print()


async def example_2_force_duckduckgo():
    """2:  DuckDuckGo"""
    print("\n" + "=" * 60)
    print(" 2:  DuckDuckGo")
    print("=" * 60)

    searcher = WebSearcher(prefer_mcp=True)

    query = "Python "
    print(f"\n: {query} ( DuckDuckGo)\n")

    results = await searcher.search(
        query,
        max_results=3,
        force_duckduckgo=True  #  DuckDuckGo
    )

    print(f" {len(results)}  ( DuckDuckGo):\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']} (: {result['source']})")


async def example_3_direct_mcp():
    """3:  MCP Manager"""
    print("\n" + "=" * 60)
    print(" 3:  MCP Manager")
    print("=" * 60)

    manager = get_mcp_manager()

    #  MCP 
    if not manager.has_enabled_clients():
        print("\n   MCP ")
        print(" .env  ZHIPU_MCP_API_KEY")
        return

    enabled = manager.list_enabled_clients()
    print(f"\n MCP : {', '.join(enabled)}\n")

    # 
    query = ""
    print(f": {query}\n")

    result = await manager.search(query, max_results=3)

    if result.get("status") == "success":
        print(f"  (: {result.get('source')})")
        print(f" {len(result['results'])} :\n")

        for i, item in enumerate(result['results'], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['url']}")
    else:
        print(f" : {result.get('message')}")


async def example_4_multi_source():
    """4: """
    print("\n" + "=" * 60)
    print(" 4: ")
    print("=" * 60)

    manager = get_mcp_manager()

    if not manager.has_enabled_clients():
        print("\n   MCP ")
        return

    query = ""
    print(f"\n: {query}")
    print("...\n")

    result = await manager.multi_source_search(query, max_results=2)

    print(f": {result['total_results']}")
    print(f": {result['source_stats']}")
    print()

    for i, item in enumerate(result['results'], 1):
        print(f"{i}. {item['title']} (: {item['source']})")


async def example_5_prompt_instruction():
    """5:  LLM """
    print("\n" + "=" * 60)
    print(" 5:  LLM ")
    print("=" * 60)

    manager = get_mcp_manager()

    query = "2025103 AIGC"
    instruction = manager.get_search_prompt_instruction(query)

    print(f"\n: {query}")
    print(f"LLM : {instruction}")
    print("\n LLM  MCP ")


async def main():
    """TODO: Add docstring."""
    print("\n" + " MCP  " + "\n")

    #  API Key
    if not os.getenv("ZHIPU_MCP_API_KEY"):
        print("  :  ZHIPU_MCP_API_KEY")
        print(" DuckDuckGo ")
        print("\n:")
        print("1.  https://open.bigmodel.cn/  API Key")
        print("2.  .env : ZHIPU_MCP_API_KEY=your_key")
        print()

    try:
        # 
        await example_1_basic_search()
        await example_2_force_duckduckgo()
        await example_3_direct_mcp()
        await example_4_multi_source()
        await example_5_prompt_instruction()

        print("\n" + "=" * 60)
        print(" !")
        print("=" * 60)

    except Exception as e:
        logger.error(f": {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
