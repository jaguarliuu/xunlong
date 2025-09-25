"""
简单Web搜索工具 - 使用requests进行搜索
"""
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from loguru import logger
import urllib.parse
from bs4 import BeautifulSoup
import re

class SimpleWebSearcher:
    """简单Web搜索器"""
    
    def __init__(self):
        self.name = "简单Web搜索器"
        self.timeout = 30
        
    async def search(
        self, 
        query: str, 
        max_results: int = 10,
        region: str = "cn-zh"
    ) -> List[Dict[str, Any]]:
        """执行搜索"""
        
        try:
            logger.info(f"[{self.name}] 搜索查询: {query}")
            
            # 使用多个搜索引擎
            results = []
            
            # 1. 搜索百度（适合中文内容）
            baidu_results = await self._search_baidu(query, max_results // 2)
            results.extend(baidu_results)
            
            # 2. 搜索必应（国际内容）
            bing_results = await self._search_bing(query, max_results // 2)
            results.extend(bing_results)
            
            # 去重
            seen_urls = set()
            unique_results = []
            for result in results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            logger.info(f"[{self.name}] 搜索完成，获得 {len(unique_results)} 个结果")
            return unique_results[:max_results]
            
        except Exception as e:
            logger.error(f"[{self.name}] 搜索失败: {e}")
            return []
    
    async def _search_baidu(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """搜索百度"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.baidu.com/s?wd={encoded_query}&rn={max_results}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.warning(f"[{self.name}] 百度搜索失败: HTTP {response.status}")
                        return []
                    
                    html = await response.text()
                    return self._parse_baidu_results(html)
        
        except Exception as e:
            logger.error(f"[{self.name}] 百度搜索异常: {e}")
            return []
    
    async def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """搜索必应"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.bing.com/search?q={encoded_query}&count={max_results}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.warning(f"[{self.name}] 必应搜索失败: HTTP {response.status}")
                        return []
                    
                    html = await response.text()
                    return self._parse_bing_results(html)
        
        except Exception as e:
            logger.error(f"[{self.name}] 必应搜索异常: {e}")
            return []
    
    def _parse_baidu_results(self, html: str) -> List[Dict[str, Any]]:
        """解析百度搜索结果"""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 百度搜索结果的选择器
            result_items = soup.find_all('div', class_='result')
            
            for item in result_items:
                try:
                    # 提取标题和链接
                    title_element = item.find('h3')
                    if not title_element:
                        continue
                    
                    link_element = title_element.find('a')
                    if not link_element:
                        continue
                    
                    title = link_element.get_text().strip()
                    url = link_element.get('href', '')
                    
                    # 提取摘要
                    snippet = ""
                    snippet_element = item.find('span', class_='content-right_8Zs40')
                    if not snippet_element:
                        snippet_element = item.find('div', class_='c-abstract')
                    if snippet_element:
                        snippet = snippet_element.get_text().strip()
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "baidu"
                        })
                
                except Exception as e:
                    logger.debug(f"[{self.name}] 解析百度结果项失败: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"[{self.name}] 解析百度结果失败: {e}")
        
        return results
    
    def _parse_bing_results(self, html: str) -> List[Dict[str, Any]]:
        """解析必应搜索结果"""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 必应搜索结果的选择器
            result_items = soup.find_all('li', class_='b_algo')
            
            for item in result_items:
                try:
                    # 提取标题和链接
                    title_element = item.find('h2')
                    if not title_element:
                        continue
                    
                    link_element = title_element.find('a')
                    if not link_element:
                        continue
                    
                    title = link_element.get_text().strip()
                    url = link_element.get('href', '')
                    
                    # 提取摘要
                    snippet = ""
                    snippet_element = item.find('p')
                    if snippet_element:
                        snippet = snippet_element.get_text().strip()
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "bing"
                        })
                
                except Exception as e:
                    logger.debug(f"[{self.name}] 解析必应结果项失败: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"[{self.name}] 解析必应结果失败: {e}")
        
        return results