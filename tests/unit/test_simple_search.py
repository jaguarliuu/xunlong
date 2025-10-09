"""TODO: Add docstring."""

import asyncio
import json
from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline


async def test_simple_search():
    """TODO: Add docstring."""
    print(" ")
    print("="*40)
    
    #  - 
    config = DeepSearchConfig(
        headless=False,  # 
        topk=1,          # 1
        shots_dir="./test_shots"
    )
    
    # 
    pipeline = DeepSearchPipeline(config)
    
    # 
    query = "Python"
    print(f": {query}")
    
    try:
        result = await pipeline.search(query)
        
        print(f"\n :")
        print(f"   : {result.query}")
        print(f"   : {result.engine}")
        print(f"   : {result.total_found}")
        print(f"   : {result.success_count}")
        print(f"   : {result.error_count}")
        print(f"   : {result.execution_time:.2f}s")
        
        if result.items:
            for i, item in enumerate(result.items, 1):
                status = "" if not item.error else ""
                print(f"\n   {status}  {i}:")
                print(f"      : {item.title}")
                print(f"      URL: {item.url}")
                print(f"      : {item.length} ")
                if item.text:
                    print(f"      : {item.text[:100]}...")
                if item.screenshot_path:
                    print(f"      : {item.screenshot_path}")
                if item.error:
                    print(f"      : {item.error}")
        
        # 
        with open("test_search_result.json", "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
        print(f"\n : test_search_result.json")
        
        return result.success_count > 0
        
    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print(" DeepSearch ")
    
    try:
        success = asyncio.run(test_simple_search())
        
        if success:
            print("\n ")
            print("\n :")
            print("1. python main.py search \"\" --topk 3")
            print("2. python run_api.py  # API")
        else:
            print("\n ")
            
    except KeyboardInterrupt:
        print("\n ")
    except Exception as e:
        print(f"\n : {e}")
        import traceback
        traceback.print_exc()