"""DuckDuckGo"""

import asyncio
from typing import List, Optional
from playwright.async_api import Page
from loguru import logger
from urllib.parse import quote_plus

from .base import BaseSearcher
from ..models import SearchLink


class DuckDuckGoSearcher(BaseSearcher):
    """DuckDuckGo"""
    
    @property
    def name(self) -> str:
        return "duckduckgo"
    
    async def search(
        self,
        page: Page,
        query: str,
        time_filter: Optional[str] = None,
        region: str = "cn-zh"
    ) -> List[SearchLink]:
        """
        DuckDuckGo
        
        Args:
            page: Playwright
            query: 
            
        Returns:
            
        """
        try:
            logger.info(f"DuckDuckGo: {query}")

            # URL
            mapped_filter = None
            filter_map = {
                "day": "d",
                "week": "w",
                "month": "m",
                "year": "y"
            }
            if time_filter:
                mapped_filter = filter_map.get(time_filter.lower())

            params = f"?q={quote_plus(query)}&ia=web&kl={region}"
            if mapped_filter:
                params += f"&df={mapped_filter}"

            search_url = f"https://duckduckgo.com/{params}"

            # DuckDuckGo
            await page.goto(search_url, wait_until="domcontentloaded")
            await asyncio.sleep(4)  # 
            
            # 
            possible_selectors = [
                '[data-testid="result"]',
                'article[data-testid="result"]', 
                '.result',
                '.web-result',
                '[data-layout="organic"]',
                'article',
                '.result__body',
                'div[data-domain]',
                'h3 a[href]'
            ]
            
            result_selector = None
            result_count = 0
            
            # 
            for selector in possible_selectors:
                try:
                    count = await page.locator(selector).count()
                    if count > 0:
                        result_selector = selector
                        result_count = count
                        logger.debug(f": {selector}, : {count}")
                        break
                except Exception as e:
                    logger.debug(f" {selector} : {e}")
                    continue
            
            if result_count == 0:
                # 
                page_content = await page.content()
                logger.debug(f": {len(page_content)}")
                logger.debug(f": {await page.title()}")
                raise Exception("")
            
            logger.debug(f": {result_selector},  {result_count} ")
            
            # 
            results = []
            result_elements = await page.locator(result_selector).all()
            
            logger.info(f" {len(result_elements)} ")
            
            for i, element in enumerate(result_elements[:self.topk]):
                try:
                    #  - 
                    title_element = element.locator('a[data-testid="result-title-a"]')
                    if await title_element.count() == 0:
                        # 
                        title_element = element.locator('h2 a, h3 a, .result__a')
                    
                    title = await title_element.inner_text()
                    url = await title_element.get_attribute('href')
                    
                    #  - 
                    snippet = ""
                    snippet_selectors = [
                        '[data-result="snippet"]',
                        '.result__snippet',
                        '[data-testid="result-snippet"]',
                        '.result-snippet'
                    ]
                    
                    for snippet_selector in snippet_selectors:
                        snippet_element = element.locator(snippet_selector)
                        if await snippet_element.count() > 0:
                            snippet = await snippet_element.inner_text()
                            break
                    
                    if url and title:
                        results.append(SearchLink(
                            url=url,
                            title=title.strip(),
                            snippet=snippet.strip() if snippet else None
                        ))
                        logger.debug(f" {i+1}: {title[:50]}...")
                
                except Exception as e:
                    logger.warning(f" {i+1} : {e}")
                    continue
            
            logger.info(f" {len(results)} ")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo: {e}")
            return []
