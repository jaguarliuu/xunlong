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
import httpx

# 
load_dotenv()


async def test_1_check_env():
    """1: """
    print("\n" + "=" * 70)
    print(" 1: ")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")

    if not api_key:
        print("  ZHIPU_MCP_API_KEY")
        print(" .env :")
        print("ZHIPU_MCP_API_KEY=your_api_key_here")
        return False
    else:
        # key
        masked_key = api_key[:10] + "..." + api_key[-10:] if len(api_key) > 20 else "***"
        print(f"  ZHIPU_MCP_API_KEY: {masked_key}")
        return True


async def test_2_simple_request():
    """2: HTTP"""
    print("\n" + "=" * 70)
    print(" 2: HTTP GET")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("  API Key")
        return

    # URL
    base_url = f"https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={api_key}"

    print(f"URL: {base_url[:60]}...{base_url[-20:]}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\nGET...")
            response = await client.get(
                base_url,
                headers={
                    "Accept": "text/event-stream",
                    "User-Agent": "XunLong MCP Client/1.0"
                }
            )

            print(f" : {response.status_code}")
            print(f": {dict(response.headers)}")

            if response.status_code == 200:
                content = response.text[:500]
                print(f"500:\n{content}")
            else:
                print(f" : {response.status_code}")
                print(f": {response.text[:500]}")

    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()


async def test_3_sse_with_query():
    """3: SSE"""
    print("\n" + "=" * 70)
    print(" 3: SSE")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("  API Key")
        return

    # URL with query
    from urllib.parse import urlencode

    base_url = f"https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={api_key}"
    search_params = {
        "query": "",
        "count": 3
    }
    search_url = f"{base_url}&{urlencode(search_params)}"

    print(f": ")
    print(f"URL: {search_url[:60]}...{search_url[-30:]}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("\nSSE...")

            async with client.stream(
                'GET',
                search_url,
                headers={
                    "Accept": "text/event-stream",
                    "User-Agent": "XunLong MCP Client/1.0"
                }
            ) as response:
                print(f" : {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type')}")

                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f" : {error_text.decode()[:500]}")
                    return

                print("\nSSE:")
                print("-" * 70)

                line_count = 0
                event_count = 0

                async for line in response.aiter_lines():
                    line_count += 1

                    if not line:
                        continue

                    print(f"[{line_count}] {line}")

                    if line.startswith('data: '):
                        event_count += 1
                        data_str = line[6:].strip()

                        if data_str not in ['[DONE]', '']:
                            try:
                                import json
                                event_data = json.loads(data_str)
                                print(f"    {event_count} ")
                                print(f"    : {json.dumps(event_data, ensure_ascii=False, indent=2)[:300]}")
                            except json.JSONDecodeError as e:
                                print(f"   JSON: {e}")
                                print(f"    : {data_str[:200]}")

                print("-" * 70)
                print(f" SSE {line_count} {event_count} ")

    except httpx.TimeoutException:
        print(" ")
    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()


async def test_4_use_mcp_client():
    """4: MCP"""
    print("\n" + "=" * 70)
    print(" 4: MCP")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("  API Key")
        return

    try:
        from src.mcp.zhipu_web_search import ZhipuWebSearchClient

        client = ZhipuWebSearchClient(api_key=api_key)

        print(f" ")
        print(f": {client.name}")
        print(f"URL: {client.config.url[:60]}...")

        print("\n...")
        result = await client.call_tool(
            "web_search",
            {"query": "", "max_results": 3}
        )

        print(f"\n:")
        print(f": {result.get('status')}")
        print(f": {result.get('message', 'N/A')}")
        print(f": {len(result.get('results', []))}")

        for i, item in enumerate(result.get('results', [])[:3], 1):
            print(f"\n {i}:")
            print(f"  : {item.get('title', 'N/A')}")
            print(f"  URL: {item.get('url', 'N/A')}")
            print(f"  : {item.get('snippet', 'N/A')[:100]}")

    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()


async def main():
    """TODO: Add docstring."""
    print("\n" + "  MCP  " + "\n")

    # DEBUG
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    try:
        # 1: 
        has_key = await test_1_check_env()

        if not has_key:
            print("\n   ZHIPU_MCP_API_KEY ")
            return

        # 2: 
        await test_2_simple_request()

        # 3: SSE
        await test_3_sse_with_query()

        # 4: MCP
        await test_4_use_mcp_client()

        print("\n" + "=" * 70)
        print("")
        print("=" * 70)

    except Exception as e:
        logger.error(f": {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
