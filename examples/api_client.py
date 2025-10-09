"""DeepSearch API """

import requests
import json
from typing import Dict, Any


class DeepSearchClient:
    """DeepSearch API """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def search(
        self, 
        query: str, 
        topk: int = 5, 
        engine: str = "duckduckgo", 
        headless: bool = True
    ) -> Dict[str, Any]:
        """
        
        
        Args:
            query: 
            topk: 
            engine: 
            headless: 
            
        Returns:
            
        """
        url = f"{self.base_url}/search"
        params = {
            "q": query,
            "k": topk,
            "engine": engine,
            "headless": headless
        }
        
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_config(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            response = requests.get(f"{self.base_url}/config", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def main():
    """API"""
    print(" DeepSearch API ")
    print("=" * 40)
    
    # 
    client = DeepSearchClient()
    
    # 
    print(" API...")
    health = client.health_check()
    if "error" in health:
        print(f" API: {health['error']}")
        print("API: python run_api.py")
        return
    
    print(f" API: {health}")
    
    # 
    print("\n ...")
    config = client.get_config()
    print(f": {json.dumps(config, indent=2, ensure_ascii=False)}")
    
    # 
    print("\n ...")
    queries = [
        "Python",
        "",
        "Web"
    ]
    
    for query in queries:
        print(f"\n : {query}")
        
        result = client.search(
            query=query,
            topk=3,
            headless=True
        )
        
        if "error" in result:
            print(f" : {result['error']}")
            continue
        
        print(f" :")
        print(f"   - : {result['query']}")
        print(f"   - : {result['engine']}")
        print(f"   - : {result['total_found']}")
        print(f"   - : {result['success_count']}")
        print(f"   - : {result['error_count']}")
        print(f"   - : {result['execution_time']:.2f}s")
        
        # 2
        for i, item in enumerate(result['items'][:2], 1):
            status = "" if not item.get('error') else ""
            print(f"   {status} {i}. {item['title'][:50]}...")
            if item.get('text'):
                print(f"      : {item['text'][:80]}...")
        
        print("-" * 40)


if __name__ == "__main__":
    main()