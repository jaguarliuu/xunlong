"""DeepSearch API 客户端示例"""

import requests
import json
from typing import Dict, Any


class DeepSearchClient:
    """DeepSearch API 客户端"""
    
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
        执行搜索
        
        Args:
            query: 搜索查询词
            topk: 抓取结果数量
            engine: 搜索引擎
            headless: 是否无头模式
            
        Returns:
            搜索结果字典
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
        """健康检查"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        try:
            response = requests.get(f"{self.base_url}/config", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def main():
    """API客户端使用示例"""
    print("🌐 DeepSearch API 客户端示例")
    print("=" * 40)
    
    # 创建客户端
    client = DeepSearchClient()
    
    # 健康检查
    print("🔍 检查API服务状态...")
    health = client.health_check()
    if "error" in health:
        print(f"❌ API服务不可用: {health['error']}")
        print("请先启动API服务: python run_api.py")
        return
    
    print(f"✅ API服务正常: {health}")
    
    # 获取配置
    print("\n⚙️ 获取服务配置...")
    config = client.get_config()
    print(f"配置信息: {json.dumps(config, indent=2, ensure_ascii=False)}")
    
    # 执行搜索
    print("\n🔍 执行搜索...")
    queries = [
        "Python爬虫教程",
        "机器学习入门",
        "Web开发框架对比"
    ]
    
    for query in queries:
        print(f"\n📝 搜索: {query}")
        
        result = client.search(
            query=query,
            topk=3,
            headless=True
        )
        
        if "error" in result:
            print(f"❌ 搜索失败: {result['error']}")
            continue
        
        print(f"✅ 搜索完成:")
        print(f"   - 查询词: {result['query']}")
        print(f"   - 搜索引擎: {result['engine']}")
        print(f"   - 找到结果: {result['total_found']}")
        print(f"   - 成功: {result['success_count']}")
        print(f"   - 失败: {result['error_count']}")
        print(f"   - 耗时: {result['execution_time']:.2f}s")
        
        # 显示前2个结果
        for i, item in enumerate(result['items'][:2], 1):
            status = "✓" if not item.get('error') else "✗"
            print(f"   {status} {i}. {item['title'][:50]}...")
            if item.get('text'):
                print(f"      内容: {item['text'][:80]}...")
        
        print("-" * 40)


if __name__ == "__main__":
    main()