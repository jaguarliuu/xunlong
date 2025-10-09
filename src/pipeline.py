"""DeepSearch"""

import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger

from .searcher.duckduckgo import DuckDuckGoSearcher
from .browser import BrowserManager
from .extractor import ContentExtractor
from .config import DeepSearchConfig


class DeepSearchPipeline:
    """ - """
    
    def __init__(self, config: Optional[DeepSearchConfig] = None):
        self.config = config or DeepSearchConfig()
        self.searcher = DuckDuckGoSearcher()
        self.browser_manager = BrowserManager(self.config)
        self.extractor = ContentExtractor()
        
        logger.info("DeepSearch")
    
    async def search_and_extract(
        self, 
        query: str, 
        topk: int = 5,
        extract_content: bool = True
    ) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        try:
            logger.info(f": {query} (topk={topk})")
            
            # 1: 
            search_results = []
            
            async with self.browser_manager as browser:
                page = await browser.new_page()
                
                # topk
                self.searcher.topk = topk
                
                # 
                search_links = await self.searcher.search(page, query)
                
                # 
                for link in search_links:
                    search_results.append({
                        'url': link.url,
                        'title': link.title,
                        'snippet': link.snippet or ''
                    })
                
                await page.close()
            
            if not search_results:
                logger.warning("")
                return []
            
            logger.info(f" {len(search_results)} ")
            
            if not extract_content:
                return search_results
            
            # 2: 
            extracted_results = []
            
            async with self.browser_manager as browser:
                for i, result in enumerate(search_results):
                    try:
                        logger.info(f" {i+1}/{len(search_results)}: {result.get('title', 'Unknown')}")
                        
                        # 
                        page_content = await browser.get_page_content(result['url'])
                        
                        if page_content:
                            # 
                            extracted_content = self.extractor.extract_content(
                                page_content, 
                                result['url']
                            )
                            
                            # 
                            enhanced_result = {
                                **result,
                                'content': extracted_content.get('content', ''),
                                'summary': extracted_content.get('summary', ''),
                                'metadata': extracted_content.get('metadata', {}),
                                'extraction_status': 'success'
                            }
                        else:
                            # 
                            enhanced_result = {
                                **result,
                                'content': result.get('snippet', ''),
                                'summary': result.get('snippet', ''),
                                'metadata': {},
                                'extraction_status': 'failed'
                            }
                        
                        extracted_results.append(enhanced_result)
                        
                    except Exception as e:
                        logger.error(f" {result.get('url', 'Unknown URL')}: {e}")
                        
                        # 
                        failed_result = {
                            **result,
                            'content': result.get('snippet', ''),
                            'summary': result.get('snippet', ''),
                            'metadata': {},
                            'extraction_status': 'error',
                            'extraction_error': str(e)
                        }
                        extracted_results.append(failed_result)
            
            logger.info(f" {len(extracted_results)} ")
            return extracted_results
            
        except Exception as e:
            logger.error(f": {e}")
            return []
    
    async def simple_search(self, query: str, topk: int = 5) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        return await self.search_and_extract(query, topk, extract_content=False)
    
    async def extract_url_content(self, url: str) -> Dict[str, Any]:
        """URL"""
        try:
            logger.info(f"URL: {url}")
            
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
            logger.error(f"URL {url}: {e}")
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'content': '',
                'summary': '',
                'metadata': {}
            }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
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