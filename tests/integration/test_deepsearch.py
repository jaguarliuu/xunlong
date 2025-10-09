"""DeepSearch """

import asyncio
import json
from pathlib import Path

from src.config import DeepSearchConfig
from src.pipeline import DeepSearchPipeline


async def test_search():
    """TODO: Add docstring."""
    print("  DeepSearch...")
    
    # 
    config = DeepSearchConfig(
        headless=False,  # 
        topk=3,          # 3
        shots_dir="./test_shots"
    )
    
    # 
    pipeline = DeepSearchPipeline(config)
    
    # 
    test_queries = [
        "Python web scraping",
        "",
        "2025"
    ]
    
    for query in test_queries:
        print(f"\n : {query}")
        
        try:
            result = await pipeline.search(query)
            
            print(f" :")
            print(f"   - : {result.total_found}")
            print(f"   - : {result.success_count}")
            print(f"   - : {result.error_count}")
            print(f"   - : {result.execution_time:.2f}s")
            
            # 
            output_file = f"test_result_{query.replace(' ', '_')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
            
            print(f"   - : {output_file}")
            
            # 2
            for i, item in enumerate(result.items[:2], 1):
                status = "" if not item.error else ""
                print(f"   {status} {i}. {item.title[:50]}...")
                if item.text:
                    print(f"      : {item.text[:100]}...")
                if item.screenshot_path:
                    print(f"      : {item.screenshot_path}")
            
        except Exception as e:
            print(f" : {e}")
        
        print("-" * 60)


async def test_single_page():
    """TODO: Add docstring."""
    print("\n ...")
    
    config = DeepSearchConfig(headless=False)
    pipeline = DeepSearchPipeline(config)
    
    # 
    result = await pipeline.search("GitHub")
    
    if result.items:
        item = result.items[0]
        print(f" :")
        print(f"   URL: {item.url}")
        print(f"   : {item.title}")
        print(f"   : {item.length} ")
        print(f"   : {item.screenshot_path}")
        print(f"   OG: {item.og_image_url}")
        print(f"   : {item.first_image_url}")
        
        if item.text:
            print(f"   : {item.text[:200]}...")


if __name__ == "__main__":
    print(" DeepSearch ")
    print("=" * 60)
    
    # 
    Path("test_shots").mkdir(exist_ok=True)
    
    try:
        # 
        asyncio.run(test_search())
        asyncio.run(test_single_page())
        
        print("\n !")
        
    except KeyboardInterrupt:
        print("\n ")
    except Exception as e:
        print(f"\n : {e}")
        import traceback
        traceback.print_exc()