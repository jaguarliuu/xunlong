
"""TODO: Add docstring."""
import asyncio
from src.config import DeepSearchConfig

async def minimal_test():
    print(" ...")
    try:
        config = DeepSearchConfig(headless=True, topk=1)
        print(f" : {config.search_engine}")
        return True
    except Exception as e:
        print(f" : {e}")
        return False

if __name__ == "__main__":
    asyncio.run(minimal_test())
