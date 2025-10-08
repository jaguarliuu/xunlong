"""DuckDuckGo搜索器实现"""

import asyncio
from typing import List, Optional
from playwright.async_api import Page
from loguru import logger
from urllib.parse import quote_plus

from .base import BaseSearcher
from ..models import SearchLink


class DuckDuckGoSearcher(BaseSearcher):
    """DuckDuckGo搜索器"""
    
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
        在DuckDuckGo执行搜索
        
        Args:
            page: Playwright页面对象
            query: 搜索查询词
            
        Returns:
            搜索结果链接列表
        """
        try:
            logger.info(f"开始在DuckDuckGo搜索: {query}")

            # 构建搜索URL，支持时间过滤
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

            # 访问DuckDuckGo搜索结果页
            await page.goto(search_url, wait_until="domcontentloaded")
            await asyncio.sleep(4)  # 留出加载时间
            
            # 尝试多种可能的搜索结果选择器
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
            
            # 逐个尝试选择器
            for selector in possible_selectors:
                try:
                    count = await page.locator(selector).count()
                    if count > 0:
                        result_selector = selector
                        result_count = count
                        logger.debug(f"找到有效选择器: {selector}, 结果数量: {count}")
                        break
                except Exception as e:
                    logger.debug(f"选择器 {selector} 失败: {e}")
                    continue
            
            if result_count == 0:
                # 如果所有选择器都失败，尝试获取页面内容进行调试
                page_content = await page.content()
                logger.debug(f"页面内容长度: {len(page_content)}")
                logger.debug(f"页面标题: {await page.title()}")
                raise Exception("无法找到搜索结果元素")
            
            logger.debug(f"使用选择器: {result_selector}, 找到 {result_count} 个结果")
            
            # 抓取搜索结果
            results = []
            result_elements = await page.locator(result_selector).all()
            
            logger.info(f"找到 {len(result_elements)} 个搜索结果")
            
            for i, element in enumerate(result_elements[:self.topk]):
                try:
                    # 提取标题和链接 - 使用更精确的选择器
                    title_element = element.locator('a[data-testid="result-title-a"]')
                    if await title_element.count() == 0:
                        # 备用选择器
                        title_element = element.locator('h2 a, h3 a, .result__a')
                    
                    title = await title_element.inner_text()
                    url = await title_element.get_attribute('href')
                    
                    # 提取摘要 - 尝试多种选择器
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
                        logger.debug(f"提取结果 {i+1}: {title[:50]}...")
                
                except Exception as e:
                    logger.warning(f"提取第 {i+1} 个结果时出错: {e}")
                    continue
            
            logger.info(f"成功提取 {len(results)} 个搜索结果")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo搜索失败: {e}")
            return []
