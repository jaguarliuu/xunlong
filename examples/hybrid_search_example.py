"""
 - MCP + 

MCP
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

# 
load_dotenv()


async def example_1_full_pipeline():
    """1:  - MCP + """
    print("\n" + "=" * 70)
    print(" 1: MCP + ")
    print("=" * 70)

    # 
    searcher = WebSearcher(
        prefer_mcp=True,         # MCP
        extract_content=True,    # 
        extract_images=True      # 
    )

    # 
    query = "2025"
    print(f"\n : {query}")
    print(" :")
    print("   1. MCPURL")
    print("   2. URL")
    print("   3. \n")

    results = await searcher.search(query, max_results=3)

    # 
    print(f"\n  {len(results)} :\n")
    for i, result in enumerate(results, 1):
        print(f"{'' * 70}")
        print(f"  {i}: {result['title']}")
        print(f" URL: {result['url']}")
        print(f" : {result['source']}")
        print(f" : {result.get('snippet', '')[:100]}...")

        if result.get('has_full_content'):
            full_content = result.get('full_content', '')
            print(f" : {len(full_content)} ")
            print(f"   : {full_content[:200]}...")

            images = result.get('images', [])
            print(f"  : {len(images)}")
            for j, img in enumerate(images[:3], 1):
                print(f"    {j}: {img['url']}")
                print(f"          : {img['width']}x{img['height']}")
        else:
            print(f"  : {result.get('fetch_error', '')}")

        print()


async def example_2_search_only():
    """2: """
    print("\n" + "=" * 70)
    print(" 2: ")
    print("=" * 70)

    #  - 
    searcher = WebSearcher(
        prefer_mcp=True,
        extract_content=False,   # 
        extract_images=False     # 
    )

    query = ""
    print(f"\n : {query}")
    print(" : \n")

    results = await searcher.search(query, max_results=5)

    print(f"  {len(results)} :\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   {result.get('snippet', '')[:100]}...")
        print()


async def example_3_mixed_mode():
    """3:  - """
    print("\n" + "=" * 70)
    print(" 3: ")
    print("=" * 70)

    # 
    searcher_fast = WebSearcher(
        prefer_mcp=True,
        extract_content=False
    )

    query = ""
    print(f"\n : ")
    print(f"   : {query}\n")

    quick_results = await searcher_fast.search(query, max_results=10)
    print(f"  {len(quick_results)} \n")

    # 
    print(":")
    for i, result in enumerate(quick_results, 1):
        print(f"{i}. {result['title']}")

    # 3
    print(f"\n : 3\n")

    searcher_full = WebSearcher(
        prefer_mcp=False,  # URL
        extract_content=True,
        extract_images=True
    )

    # 3
    top_results = quick_results[:3]
    detailed_results = await searcher_full._fetch_full_content_with_browser(top_results)

    print(f" :\n")
    for i, result in enumerate(detailed_results, 1):
        print(f"{i}. {result['title']}")
        if result.get('has_full_content'):
            print(f"   : {len(result.get('full_content', ''))} ")
            print(f"   : {result.get('image_count', 0)} ")
        print()


async def example_4_image_showcase():
    """4: """
    print("\n" + "=" * 70)
    print(" 4: ")
    print("=" * 70)

    searcher = WebSearcher(
        prefer_mcp=True,
        extract_content=True,
        extract_images=True
    )

    query = "AI"
    print(f"\n : {query}")
    print("  \n")

    results = await searcher.search(query, max_results=2)

    total_images = 0
    for i, result in enumerate(results, 1):
        images = result.get('images', [])
        total_images += len(images)

        print(f"\n{'' * 70}")
        print(f"  {i}: {result['title']}")
        print(f"   {len(images)} :\n")

        for j, img in enumerate(images, 1):
            print(f"   {j}. {img['alt'] or '()'}")
            print(f"      URL: {img['url']}")
            print(f"      : {img['width']}x{img['height']}")
            print()

    print(f"{'=' * 70}")
    print(f"  {total_images} ")


async def main():
    """TODO: Add docstring."""
    print("\n" + "  - MCP +  " + "\n")

    # 
    if not os.getenv("ZHIPU_MCP_API_KEY"):
        print("  :  ZHIPU_MCP_API_KEY")
        print(" DuckDuckGo \n")
    else:
        print("  ZHIPU_MCP_API_KEYMCP\n")

    try:
        # 
        await example_1_full_pipeline()
        await example_2_search_only()
        await example_3_mixed_mode()
        await example_4_image_showcase()

        print("\n" + "=" * 70)
        print(" !")
        print("=" * 70)

    except Exception as e:
        logger.error(f": {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
