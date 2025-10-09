"""
Web - DuckDuckGo + MCP+ 
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from playwright.async_api import async_playwright
import base64
from pathlib import Path

from ..searcher.duckduckgo import DuckDuckGoSearcher
# from ..mcp.mcp_manager import get_mcp_manager  # MCP
from ..utils.image_processor import ImageProcessor
from .image_downloader import ImageDownloader

class WebSearcher:
    """Web - MCP + """

    def __init__(
        self,
        prefer_mcp: bool = False,
        extract_content: bool = True,
        extract_images: bool = True,  # 
        image_insert_mode: str = "smart"
    ):
        """
        Web

        Args:
            prefer_mcp: MCP- 
            extract_content: 
            extract_images: 
            image_insert_mode: 
                - "smart": alt
                - "top": 
                - "bottom": 
                - "distribute": 
                - "none": 
        """
        self.duckduckgo_searcher = DuckDuckGoSearcher()
        # TODO: MCP
        # self.mcp_manager = get_mcp_manager()
        self.mcp_manager = None
        self.prefer_mcp = False  # MCP
        self.extract_content = extract_content
        self.extract_images = extract_images  # 
        self.image_insert_mode = image_insert_mode
        self.name = "Web"

        # 
        if extract_images:
            self.image_downloader = ImageDownloader()
        else:
            self.image_downloader = None

        logger.info(
            f"[{self.name}]  "
            f"(MCP: {'' if extract_images else ''})"
        )
        
    async def search(
        self,
        query: str,
        max_results: int = 10,
        region: str = "cn-zh",
        force_duckduckgo: bool = False,
        fetch_full_content: bool = None,
        time_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        MCPURL + 

        :
        1. MCP/DuckDuckGoURL
        2. URL

        Args:
            query: 
            max_results: 
            region: 
            force_duckduckgo: DuckDuckGoMCP
            fetch_full_content: None

        Returns:
            
        """
        try:
            logger.info(f"[{self.name}] : {query}")

            # 
            should_fetch_content = fetch_full_content if fetch_full_content is not None else self.extract_content

            # URL + 
            search_results = await self._get_search_results(query, max_results, force_duckduckgo, time_filter=time_filter, region=region)

            if not search_results:
                logger.warning(f"[{self.name}] ")
                return []

            logger.info(f"[{self.name}]  {len(search_results)} ")

            # 
            if should_fetch_content:
                logger.info(f"[{self.name}] ...")
                search_results = await self._fetch_full_content_with_browser(search_results)

                # 
                if self.extract_images and self.image_downloader:
                    logger.info(f"[{self.name}] ...")
                    search_results = await self._download_images_for_results(search_results)

                # 
                if self.extract_images and self.image_insert_mode != "none":
                    logger.info(f"[{self.name}]  (: {self.image_insert_mode})...")
                    search_results = ImageProcessor.enhance_search_results_with_images(
                        search_results,
                        mode=self.image_insert_mode
                    )

            return search_results

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return []

    async def _get_search_results(
        self,
        query: str,
        max_results: int = 10,
        force_duckduckgo: bool = False,
        time_filter: Optional[str] = None,
        region: str = "cn-zh"
    ) -> List[Dict[str, Any]]:
        """
        URL

        Args:
            query: 
            max_results: 
            force_duckduckgo: DuckDuckGo

        Returns:
            URL
        """
        # TODO: MCP
        # MCPDuckDuckGo
        # if self.prefer_mcp and not force_duckduckgo and self.mcp_manager and self.mcp_manager.has_enabled_clients():
        #     try:
        #         logger.info(f"[{self.name}] MCPURL")
        #         mcp_result = await self.mcp_manager.search(query, max_results)
        #
        #         if mcp_result.get("status") == "success":
        #             results = mcp_result.get("results", [])
        #             logger.info(f"[{self.name}] MCP {len(results)} URL")
        #             return results
        #         else:
        #             logger.warning(f"[{self.name}] MCP: {mcp_result.get('message', '')}")
        #             logger.info(f"[{self.name}] DuckDuckGo")
        #     except Exception as e:
        #         logger.error(f"[{self.name}] MCP: {e}")
        #         logger.info(f"[{self.name}] DuckDuckGo")

        # DuckDuckGo
        return await self._search_duckduckgo(query, max_results, time_filter=time_filter, region=region)

    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int = 10,
        time_filter: Optional[str] = None,
        region: str = "cn-zh"
    ) -> List[Dict[str, Any]]:
        """
        DuckDuckGo

        Args:
            query: 
            max_results: 

        Returns:
            
        """
        try:
            logger.info(f"[{self.name}] DuckDuckGo")

            # 
            self.duckduckgo_searcher.topk = max_results

            # Playwright
            async with async_playwright() as p:
                #  - 
                browser = await p.chromium.launch(
                    headless=False,  # 
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )

                try:
                    # 
                    page = await browser.new_page()

                    # 
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                     '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })

                    # 
                    search_results = await self.duckduckgo_searcher.search(page, query, time_filter=time_filter, region=region)

                    # 
                    formatted_results = []
                    for result in search_results:
                        formatted_result = {
                            "title": result.title,
                            "url": result.url,
                            "snippet": result.snippet or "",
                            "source": "duckduckgo"
                        }
                        formatted_results.append(formatted_result)

                    logger.info(f"[{self.name}] DuckDuckGo {len(formatted_results)} ")
                    return formatted_results

                finally:
                    # 
                    await browser.close()

        except Exception as e:
            logger.error(f"[{self.name}] DuckDuckGo: {e}")
            return []

    async def _fetch_full_content_with_browser(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        URL

        Args:
            search_results: URL

        Returns:
            
        """
        async with async_playwright() as p:
            # 
            browser = await p.chromium.launch(
                headless=True,  # 
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )

            try:
                # URL
                logger.info(f"[{self.name}]  {len(search_results)} URL...")
                tasks = [
                    self._fetch_single_url(browser, i, result, len(search_results))
                    for i, result in enumerate(search_results)
                ]

                enriched_results = await asyncio.gather(*tasks, return_exceptions=True)

                # 
                final_results = []
                for i, result in enumerate(enriched_results):
                    if isinstance(result, Exception):
                        logger.error(f"[{self.name}]  {i+1} : {result}")
                        final_results.append({
                            **search_results[i],
                            "full_content": search_results[i].get("snippet", ""),
                            "images": [],
                            "has_full_content": False,
                            "fetch_error": str(result)
                        })
                    else:
                        final_results.append(result)

                logger.info(f"[{self.name}] ")
                return final_results

            finally:
                await browser.close()

    async def _fetch_single_url(
        self,
        browser,
        index: int,
        result: Dict[str, Any],
        total: int
    ) -> Dict[str, Any]:
        """
        URL

        Args:
            browser: 
            index: 
            result: 
            total: 

        Returns:
            
        """
        url = result.get("url", "")
        if not url:
            return result

        logger.info(f"[{self.name}]  ({index+1}/{total}): {url}")

        try:
            # 
            page = await browser.new_page()

            # 
            page.set_default_timeout(30000)  # 30

            # 
            await page.goto(url, wait_until="domcontentloaded")

            # 
            await page.wait_for_timeout(1500)  # 1.5

            # 
            full_content = await self._extract_content_from_page(page)

            # 
            images = []
            if self.extract_images:
                images = await self._extract_images_from_page(page, url)

            # 
            await page.close()

            logger.info(f"[{self.name}]  ({index+1}/{total}): {len(full_content)} , {len(images)} ")

            # 
            return {
                **result,  # title, snippet
                "full_content": full_content,
                "images": images,
                "has_full_content": True,
                "image_count": len(images)
            }

        except Exception as e:
            logger.error(f"[{self.name}]  ({index+1}/{total}) {url}: {e}")
            # 
            return {
                **result,
                "full_content": result.get("snippet", ""),
                "images": [],
                "has_full_content": False,
                "fetch_error": str(e)
            }

    async def _extract_content_from_page(self, page) -> str:
        """
        

        Args:
            page: Playwright

        Returns:
            
        """
        try:
            # 
            content_selectors = [
                "article",
                "main",
                "[role='main']",
                ".content",
                ".article-content",
                ".post-content",
                "#content",
                ".main-content"
            ]

            content = ""

            # 
            for selector in content_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        if len(text) > len(content):
                            content = text
                except:
                    continue

            # body
            if not content:
                try:
                    content = await page.evaluate("document.body.innerText")
                except:
                    content = ""

            # 
            content = content.strip()

            # 
            if len(content) > 10000:
                content = content[:10000] + "..."

            return content

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return ""

    async def _extract_images_from_page(self, page, base_url: str) -> List[Dict[str, Any]]:
        """
        

        Args:
            page: Playwright
            base_url: URL

        Returns:
            url, alt, width, height
        """
        try:
            # 
            images_data = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images
                        .filter(img => {
                            // 
                            const width = img.naturalWidth || img.width;
                            const height = img.naturalHeight || img.height;
                            return width >= 200 && height >= 200;  // 
                        })
                        .map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth || img.width,
                            height: img.naturalHeight || img.height
                        }))
                        .slice(0, 10);  // 10
                }
            """)

            images = []
            for img_data in images_data:
                img_url = img_data.get("src", "")
                if not img_url or img_url.startswith("data:"):
                    continue

                # 
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif img_url.startswith("/"):
                    from urllib.parse import urlparse
                    parsed = urlparse(base_url)
                    img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"

                images.append({
                    "url": img_url,
                    "alt": img_data.get("alt", ""),
                    "width": img_data.get("width", 0),
                    "height": img_data.get("height", 0)
                })

            logger.info(f"[{self.name}]  {len(images)} ")
            return images

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return []

    async def _download_images_for_results(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        

        Args:
            search_results: 

        Returns:
            
        """
        try:
            updated_results = []

            for result in search_results:
                images = result.get('images', [])

                if images:
                    # 
                    downloaded_images = await self.image_downloader.download_images(
                        images,
                        optimize=True
                    )

                    # 
                    updated_result = result.copy()
                    updated_result['images'] = downloaded_images
                    updated_results.append(updated_result)

                    logger.info(
                        f"[{self.name}]  '{result.get('title', 'N/A')[:50]}' "
                        f" {len(downloaded_images)} "
                    )
                else:
                    updated_results.append(result)

            return updated_results

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return search_results

    def search_sync(
        self,
        query: str,
        max_results: int = 10,
        region: str = "cn-zh",
        time_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        try:
            # 
            try:
                loop = asyncio.get_running_loop()
                # 
                import concurrent.futures
                import threading
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.search(query, max_results, region, time_filter=time_filter))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
                    
            except RuntimeError:
                # asyncio.run
                return asyncio.run(self.search(query, max_results, region, time_filter=time_filter))
        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return []
