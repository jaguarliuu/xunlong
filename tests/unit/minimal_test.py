
"""最小化功能测试"""
import asyncio
from src.config import DeepSearchConfig

async def minimal_test():
    print("🧪 最小化测试...")
    try:
        config = DeepSearchConfig(headless=True, topk=1)
        print(f"✅ 配置创建成功: {config.search_engine}")
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(minimal_test())
