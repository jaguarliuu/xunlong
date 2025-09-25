"""
Web搜索工具 - 基于DuckDuckGo搜索
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from playwright.async_api import async_playwright

from ..searcher.duckduckgo import DuckDuckGoSearcher

class WebSearcher:
    """Web搜索器"""
    
    def __init__(self):
        self.duckduckgo_searcher = DuckDuckGoSearcher()
        self.name = "Web搜索器"
        
    async def search(
        self, 
        query: str, 
        max_results: int = 10,
        region: str = "cn-zh"
    ) -> List[Dict[str, Any]]:
        """执行搜索"""
        
        try:
            logger.info(f"[{self.name}] 搜索查询: {query}")
            
            # 设置搜索结果数量
            self.duckduckgo_searcher.topk = max_results
            
            # 使用Playwright启动浏览器进行搜索
            async with async_playwright() as p:
                # 启动浏览器 - 使用有头模式
                browser = await p.chromium.launch(
                    headless=False,  # 有头模式，直接打开浏览器
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                
                try:
                    # 创建页面
                    page = await browser.new_page()
                    
                    # 设置用户代理
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                     '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    
                    # 执行搜索
                    search_results = await self.duckduckgo_searcher.search(page, query)
                    
                    # 格式化结果
                    formatted_results = []
                    for result in search_results:
                        formatted_result = {
                            "title": result.title,
                            "url": result.url,
                            "snippet": result.snippet or "",
                            "source": "duckduckgo"
                        }
                        formatted_results.append(formatted_result)
                    
                    logger.info(f"[{self.name}] 搜索完成，获得 {len(formatted_results)} 个结果")
                    return formatted_results
                    
                finally:
                    # 关闭浏览器
                    await browser.close()
            
        except Exception as e:
            logger.error(f"[{self.name}] 搜索失败: {e}")
            # 如果浏览器搜索失败，返回空结果而不是崩溃
            return []
    
    def search_sync(
        self, 
        query: str, 
        max_results: int = 10,
        region: str = "cn-zh"
    ) -> List[Dict[str, Any]]:
        """同步搜索接口"""
        try:
            # 检查是否已经在事件循环中
            try:
                loop = asyncio.get_running_loop()
                # 如果已经在事件循环中，创建一个新的线程来运行异步代码
                import concurrent.futures
                import threading
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.search(query, max_results, region))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
                    
            except RuntimeError:
                # 没有运行的事件循环，可以直接使用asyncio.run
                return asyncio.run(self.search(query, max_results, region))
        except Exception as e:
            logger.error(f"[{self.name}] 同步搜索失败: {e}")
            return []