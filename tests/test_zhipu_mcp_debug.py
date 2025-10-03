"""
智谱 MCP 调试测试

用于诊断智谱 Web 搜索 MCP 服务的连接问题
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
import httpx

# 加载环境变量
load_dotenv()


async def test_1_check_env():
    """测试1: 检查环境变量配置"""
    print("\n" + "=" * 70)
    print("测试 1: 检查环境变量")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")

    if not api_key:
        print("❌ 未配置 ZHIPU_MCP_API_KEY")
        print("请在 .env 文件中添加:")
        print("ZHIPU_MCP_API_KEY=your_api_key_here")
        return False
    else:
        # 显示部分key（隐藏敏感信息）
        masked_key = api_key[:10] + "..." + api_key[-10:] if len(api_key) > 20 else "***"
        print(f"✅ 已配置 ZHIPU_MCP_API_KEY: {masked_key}")
        return True


async def test_2_simple_request():
    """测试2: 简单的HTTP请求测试"""
    print("\n" + "=" * 70)
    print("测试 2: 简单的HTTP GET请求")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("⚠️  跳过：未配置API Key")
        return

    # 构建URL
    base_url = f"https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={api_key}"

    print(f"URL: {base_url[:60]}...{base_url[-20:]}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\n发送GET请求...")
            response = await client.get(
                base_url,
                headers={
                    "Accept": "text/event-stream",
                    "User-Agent": "XunLong MCP Client/1.0"
                }
            )

            print(f"✅ 响应状态: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")

            if response.status_code == 200:
                content = response.text[:500]
                print(f"响应内容（前500字符）:\n{content}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()


async def test_3_sse_with_query():
    """测试3: 带查询参数的SSE请求"""
    print("\n" + "=" * 70)
    print("测试 3: 带查询参数的SSE流式请求")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("⚠️  跳过：未配置API Key")
        return

    # 构建URL with query
    from urllib.parse import urlencode

    base_url = f"https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={api_key}"
    search_params = {
        "query": "人工智能",
        "count": 3
    }
    search_url = f"{base_url}&{urlencode(search_params)}"

    print(f"查询: 人工智能")
    print(f"URL: {search_url[:60]}...{search_url[-30:]}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("\n发送SSE流式请求...")

            async with client.stream(
                'GET',
                search_url,
                headers={
                    "Accept": "text/event-stream",
                    "User-Agent": "XunLong MCP Client/1.0"
                }
            ) as response:
                print(f"✅ 响应状态: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type')}")

                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"❌ 错误响应: {error_text.decode()[:500]}")
                    return

                print("\n开始接收SSE事件流:")
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
                                print(f"  ✓ 事件 {event_count} 解析成功")
                                print(f"    数据: {json.dumps(event_data, ensure_ascii=False, indent=2)[:300]}")
                            except json.JSONDecodeError as e:
                                print(f"  ✗ JSON解析失败: {e}")
                                print(f"    原始数据: {data_str[:200]}")

                print("-" * 70)
                print(f"✅ SSE流结束，共接收 {line_count} 行，{event_count} 个事件")

    except httpx.TimeoutException:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()


async def test_4_use_mcp_client():
    """测试4: 使用MCP客户端"""
    print("\n" + "=" * 70)
    print("测试 4: 使用MCP客户端类")
    print("=" * 70)

    api_key = os.getenv("ZHIPU_MCP_API_KEY")
    if not api_key:
        print("⚠️  跳过：未配置API Key")
        return

    try:
        from src.mcp.zhipu_web_search import ZhipuWebSearchClient

        client = ZhipuWebSearchClient(api_key=api_key)

        print(f"✅ 客户端初始化成功")
        print(f"客户端名称: {client.name}")
        print(f"URL: {client.config.url[:60]}...")

        print("\n执行搜索...")
        result = await client.call_tool(
            "web_search",
            {"query": "人工智能", "max_results": 3}
        )

        print(f"\n搜索结果:")
        print(f"状态: {result.get('status')}")
        print(f"消息: {result.get('message', 'N/A')}")
        print(f"结果数: {len(result.get('results', []))}")

        for i, item in enumerate(result.get('results', [])[:3], 1):
            print(f"\n结果 {i}:")
            print(f"  标题: {item.get('title', 'N/A')}")
            print(f"  URL: {item.get('url', 'N/A')}")
            print(f"  摘要: {item.get('snippet', 'N/A')[:100]}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """运行所有诊断测试"""
    print("\n" + "🔍 智谱 MCP 服务诊断测试 " + "\n")

    # 设置日志级别为DEBUG以查看详细信息
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    try:
        # 测试1: 检查环境变量
        has_key = await test_1_check_env()

        if not has_key:
            print("\n⚠️  请先配置 ZHIPU_MCP_API_KEY 后再运行测试")
            return

        # 测试2: 简单请求
        await test_2_simple_request()

        # 测试3: SSE流式请求
        await test_3_sse_with_query()

        # 测试4: 使用MCP客户端
        await test_4_use_mcp_client()

        print("\n" + "=" * 70)
        print("诊断测试完成")
        print("=" * 70)

    except Exception as e:
        logger.error(f"测试运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
