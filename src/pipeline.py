"""DeepSearch搜索管道"""

import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger

from .searcher.duckduckgo import DuckDuckGoSearcher
from .browser import BrowserManager
from .extractor import ContentExtractor
from .config import DeepSearchConfig


class DeepSearchPipeline:
    """深度搜索管道 - 整合搜索、浏览和提取功能"""
    
    def __init__(self, config: Optional[DeepSearchConfig] = None):
        self.config = config or DeepSearchConfig()
        self.searcher = DuckDuckGoSearcher()
        self.browser_manager = BrowserManager(self.config)
        self.extractor = ContentExtractor()
        
        logger.info("DeepSearch管道初始化完成")
    
    async def search_and_extract(
        self, 
        query: str, 
        topk: int = 5,
        extract_content: bool = True
    ) -> List[Dict[str, Any]]:
        """搜索并提取内容"""
        try:
            logger.info(f"开始搜索和提取: {query} (topk={topk})")
            
            # 步骤1: 执行搜索
            search_results = []
            
            async with self.browser_manager as browser:
                page = await browser.new_page()
                
                # 设置搜索器的topk参数
                self.searcher.topk = topk
                
                # 执行搜索
                search_links = await self.searcher.search(page, query)
                
                # 转换为字典格式
                for link in search_links:
                    search_results.append({
                        'url': link.url,
                        'title': link.title,
                        'snippet': link.snippet or ''
                    })
                
                await page.close()
            
            if not search_results:
                logger.warning("搜索未返回任何结果")
                return []
            
            logger.info(f"搜索完成，找到 {len(search_results)} 个结果")
            
            if not extract_content:
                return search_results
            
            # 步骤2: 提取内容
            extracted_results = []
            
            async with self.browser_manager as browser:
                for i, result in enumerate(search_results):
                    try:
                        logger.info(f"提取内容 {i+1}/{len(search_results)}: {result.get('title', 'Unknown')}")
                        
                        # 访问页面
                        page_content = await browser.get_page_content(result['url'])
                        
                        if page_content:
                            # 提取结构化内容
                            extracted_content = self.extractor.extract_content(
                                page_content, 
                                result['url']
                            )
                            
                            # 合并结果
                            enhanced_result = {
                                **result,
                                'content': extracted_content.get('content', ''),
                                'summary': extracted_content.get('summary', ''),
                                'metadata': extracted_content.get('metadata', {}),
                                'extraction_status': 'success'
                            }
                        else:
                            # 内容提取失败，保留原始结果
                            enhanced_result = {
                                **result,
                                'content': result.get('snippet', ''),
                                'summary': result.get('snippet', ''),
                                'metadata': {},
                                'extraction_status': 'failed'
                            }
                        
                        extracted_results.append(enhanced_result)
                        
                    except Exception as e:
                        logger.error(f"提取内容失败 {result.get('url', 'Unknown URL')}: {e}")
                        
                        # 添加失败的结果
                        failed_result = {
                            **result,
                            'content': result.get('snippet', ''),
                            'summary': result.get('snippet', ''),
                            'metadata': {},
                            'extraction_status': 'error',
                            'extraction_error': str(e)
                        }
                        extracted_results.append(failed_result)
            
            logger.info(f"内容提取完成，成功提取 {len(extracted_results)} 个结果")
            return extracted_results
            
        except Exception as e:
            logger.error(f"搜索和提取失败: {e}")
            return []
    
    async def simple_search(self, query: str, topk: int = 5) -> List[Dict[str, Any]]:
        """简单搜索（不提取内容）"""
        return await self.search_and_extract(query, topk, extract_content=False)
    
    async def extract_url_content(self, url: str) -> Dict[str, Any]:
        """提取单个URL的内容"""
        try:
            logger.info(f"提取URL内容: {url}")
            
            async with self.browser_manager as browser:
                page_content = await browser.get_page_content(url)
                
                if page_content:
                    extracted_content = self.extractor.extract_content(page_content, url)
                    return {
                        'url': url,
                        'status': 'success',
                        **extracted_content
                    }
                else:
                    return {
                        'url': url,
                        'status': 'failed',
                        'content': '',
                        'summary': '',
                        'metadata': {}
                    }
                    
        except Exception as e:
            logger.error(f"URL内容提取失败 {url}: {e}")
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'content': '',
                'summary': '',
                'metadata': {}
            }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """获取管道状态"""
        return {
            'searcher': 'DuckDuckGo',
            'browser': 'Playwright',
            'extractor': 'Trafilatura',
            'config': {
                'headless': self.config.headless,
                'timeout': self.config.timeout,
                'max_pages': self.config.max_pages
            }
        }