"""vs"""

import asyncio
from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline


async def test_both_modes():
    """TODO: Add docstring."""
    print("  vs ")
    print("="*50)
    
    query = "Python"
    
    # 
    print("\n1  (headless=False)")
    print("-" * 30)
    
    config_headful = DeepSearchConfig(
        headless=False,
        topk=1,
        shots_dir="./test_shots"
    )
    
    pipeline_headful = DeepSearchPipeline(config_headful)
    
    try:
        result_headful = await pipeline_headful.search(query)
        print(f" :")
        print(f"   : {result_headful.success_count}")
        print(f"   : {result_headful.error_count}")
        print(f"   : {result_headful.execution_time:.2f}s")
    except Exception as e:
        print(f" : {e}")
    
    # 
    await asyncio.sleep(2)
    
    # 
    print("\n2  (headless=True)")
    print("-" * 30)
    
    config_headless = DeepSearchConfig(
        headless=True,
        topk=1,
        shots_dir="./test_shots"
    )
    
    pipeline_headless = DeepSearchPipeline(config_headless)
    
    try:
        result_headless = await pipeline_headless.search(query)
        print(f" :")
        print(f"   : {result_headless.success_count}")
        print(f"   : {result_headless.error_count}")
        print(f"   : {result_headless.execution_time:.2f}s")
    except Exception as e:
        print(f" : {e}")
    
    print("\n :")
    print("DuckDuckGo")
    print("CLI")


if __name__ == "__main__":
    print(" DeepSearch ")
    
    try:
        asyncio.run(test_both_modes())
    except KeyboardInterrupt:
        print("\n ")
    except Exception as e:
        print(f"\n : {e}")
        import traceback
        traceback.print_exc()