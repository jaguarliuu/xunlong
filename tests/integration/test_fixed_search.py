"""TODO: Add docstring."""

import asyncio
from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline


async def test_search_with_debug():
    """TODO: Add docstring."""
    print(" ")
    print("="*40)
    
    # 
    config = DeepSearchConfig(
        headless=False,  # 
        topk=2,
        shots_dir="./test_shots"
    )
    
    # 
    pipeline = DeepSearchPipeline(config)
    
    # 
    test_queries = [
        "GitHub",
        "Python programming",
        "machine learning"
    ]
    
    for query in test_queries:
        print(f"\n : {query}")
        print("-" * 30)
        
        try:
            result = await pipeline.search(query)
            
            print(f" :")
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
                        print(f"      : {item.text[:80]}...")
                    if item.screenshot_path:
                        print(f"      : {item.screenshot_path}")
                    if item.error:
                        print(f"      : {item.error}")
            else:
                print("    ")
            
            # 
            if result.success_count > 0:
                print(f"\n ")
                break
                
        except Exception as e:
            print(f" : {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*40)


if __name__ == "__main__":
    print(" DeepSearch ")
    
    try:
        asyncio.run(test_search_with_debug())
        
        print("\n :")
        print("1. CLI: python main.py search \"\" --topk 3")
        print("2. API: python run_api.py")
        print("3. : python examples/basic_usage.py")
        
    except KeyboardInterrupt:
        print("\n ")
    except Exception as e:
        print(f"\n : {e}")
        import traceback
        traceback.print_exc()