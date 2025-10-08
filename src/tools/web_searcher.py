"""
Web搜索工具 - 支持多源搜索（DuckDuckGo + MCP服务）+ 内容抓取
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from playwright.async_api import async_playwright
import base64
from pathlib import Path

from ..searcher.duckduckgo import DuckDuckGoSearcher
# from ..mcp.mcp_manager import get_mcp_manager  # MCP暂时禁用
from ..utils.image_processor import ImageProcessor
from .image_downloader import ImageDownloader

class WebSearcher:
    """Web搜索器 - 支持MCP搜索 + 浏览器内容抓取"""

    def __init__(
        self,
        prefer_mcp: bool = False,
        extract_content: bool = True,
        extract_images: bool = True,  # 启用图片采集
        image_insert_mode: str = "smart"
    ):
        """
        初始化Web搜索器

        Args:
            prefer_mcp: 是否优先使用MCP搜索服务（如果可用）- 暂时禁用
            extract_content: 是否提取完整内容（使用浏览器）
            extract_images: 是否提取图片
            image_insert_mode: 图片插入模式
                - "smart": 智能插入（根据图片alt和内容相关性）
                - "top": 所有图片放在开头
                - "bottom": 所有图片放在末尾（附录）
                - "distribute": 均匀分布在段落之间
                - "none": 不插入
        """
        self.duckduckgo_searcher = DuckDuckGoSearcher()
        # TODO: MCP功能暂时禁用，待后续优化
        # self.mcp_manager = get_mcp_manager()
        self.mcp_manager = None
        self.prefer_mcp = False  # 强制禁用MCP
        self.extract_content = extract_content
        self.extract_images = extract_images  # 根据参数决定是否采集图片
        self.image_insert_mode = image_insert_mode
        self.name = "Web搜索器"

        # 初始化图片下载器
        if extract_images:
            self.image_downloader = ImageDownloader()
        else:
            self.image_downloader = None

        logger.info(
            f"[{self.name}] 初始化完成 "
            f"(MCP暂时禁用，图片采集: {'启用' if extract_images else '禁用'})"
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
        执行搜索（MCP获取URL列表 + 浏览器抓取完整内容）

        工作流程:
        1. 使用MCP/DuckDuckGo获取搜索结果（标题、摘要、URL）
        2. 使用浏览器访问每个URL，提取完整内容和图片

        Args:
            query: 搜索查询
            max_results: 最大结果数
            region: 搜索区域
            force_duckduckgo: 强制使用DuckDuckGo（忽略MCP）
            fetch_full_content: 是否抓取完整内容，None时使用初始化配置

        Returns:
            搜索结果列表，包含完整内容和图片
        """
        try:
            logger.info(f"[{self.name}] 搜索查询: {query}")

            # 确定是否抓取完整内容
            should_fetch_content = fetch_full_content if fetch_full_content is not None else self.extract_content

            # 第一步：获取搜索结果列表（URL + 摘要）
            search_results = await self._get_search_results(query, max_results, force_duckduckgo, time_filter=time_filter, region=region)

            if not search_results:
                logger.warning(f"[{self.name}] 未获得搜索结果")
                return []

            logger.info(f"[{self.name}] 获得 {len(search_results)} 个搜索结果")

            # 第二步：如果需要，使用浏览器抓取完整内容
            if should_fetch_content:
                logger.info(f"[{self.name}] 开始抓取完整内容...")
                search_results = await self._fetch_full_content_with_browser(search_results)

                # 第三步：下载图片到本地
                if self.extract_images and self.image_downloader:
                    logger.info(f"[{self.name}] 下载图片到本地...")
                    search_results = await self._download_images_for_results(search_results)

                # 第四步：将图片插入到内容中
                if self.extract_images and self.image_insert_mode != "none":
                    logger.info(f"[{self.name}] 将图片插入到内容中 (模式: {self.image_insert_mode})...")
                    search_results = ImageProcessor.enhance_search_results_with_images(
                        search_results,
                        mode=self.image_insert_mode
                    )

            return search_results

        except Exception as e:
            logger.error(f"[{self.name}] 搜索失败: {e}")
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
        第一步：获取搜索结果列表（仅URL和摘要）

        Args:
            query: 搜索查询
            max_results: 最大结果数
            force_duckduckgo: 强制使用DuckDuckGo

        Returns:
            搜索结果列表（URL、标题、摘要）
        """
        # TODO: MCP功能暂时禁用
        # 优先使用MCP搜索（如果启用且未强制使用DuckDuckGo）
        # if self.prefer_mcp and not force_duckduckgo and self.mcp_manager and self.mcp_manager.has_enabled_clients():
        #     try:
        #         logger.info(f"[{self.name}] 使用MCP搜索服务获取URL列表")
        #         mcp_result = await self.mcp_manager.search(query, max_results)
        #
        #         if mcp_result.get("status") == "success":
        #             results = mcp_result.get("results", [])
        #             logger.info(f"[{self.name}] MCP搜索完成，获得 {len(results)} 个URL")
        #             return results
        #         else:
        #             logger.warning(f"[{self.name}] MCP搜索失败: {mcp_result.get('message', '未知错误')}")
        #             logger.info(f"[{self.name}] 降级到DuckDuckGo搜索")
        #     except Exception as e:
        #         logger.error(f"[{self.name}] MCP搜索异常: {e}")
        #         logger.info(f"[{self.name}] 降级到DuckDuckGo搜索")

        # 使用DuckDuckGo搜索
        return await self._search_duckduckgo(query, max_results, time_filter=time_filter, region=region)

    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int = 10,
        time_filter: Optional[str] = None,
        region: str = "cn-zh"
    ) -> List[Dict[str, Any]]:
        """
        使用DuckDuckGo搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"[{self.name}] 使用DuckDuckGo搜索")

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
                    search_results = await self.duckduckgo_searcher.search(page, query, time_filter=time_filter, region=region)

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

                    logger.info(f"[{self.name}] DuckDuckGo搜索完成，获得 {len(formatted_results)} 个结果")
                    return formatted_results

                finally:
                    # 关闭浏览器
                    await browser.close()

        except Exception as e:
            logger.error(f"[{self.name}] DuckDuckGo搜索失败: {e}")
            return []

    async def _fetch_full_content_with_browser(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        第二步：使用浏览器并行访问URL，抓取完整内容

        Args:
            search_results: 搜索结果列表（包含URL）

        Returns:
            增强后的搜索结果（包含完整内容）
        """
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=True,  # 无头模式，更快
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )

            try:
                # 并行抓取所有URL
                logger.info(f"[{self.name}] 开始并行抓取 {len(search_results)} 个URL...")
                tasks = [
                    self._fetch_single_url(browser, i, result, len(search_results))
                    for i, result in enumerate(search_results)
                ]

                enriched_results = await asyncio.gather(*tasks, return_exceptions=True)

                # 处理异常结果
                final_results = []
                for i, result in enumerate(enriched_results):
                    if isinstance(result, Exception):
                        logger.error(f"[{self.name}] 抓取任务 {i+1} 异常: {result}")
                        final_results.append({
                            **search_results[i],
                            "full_content": search_results[i].get("snippet", ""),
                            "images": [],
                            "has_full_content": False,
                            "fetch_error": str(result)
                        })
                    else:
                        final_results.append(result)

                logger.info(f"[{self.name}] 并行抓取完成")
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
        抓取单个URL的内容

        Args:
            browser: 浏览器实例
            index: 索引
            result: 搜索结果
            total: 总数

        Returns:
            增强后的结果
        """
        url = result.get("url", "")
        if not url:
            return result

        logger.info(f"[{self.name}] 抓取内容 ({index+1}/{total}): {url}")

        try:
            # 创建新页面
            page = await browser.new_page()

            # 设置超时
            page.set_default_timeout(30000)  # 30秒

            # 访问页面
            await page.goto(url, wait_until="domcontentloaded")

            # 等待一小段时间让页面加载
            await page.wait_for_timeout(1500)  # 减少到1.5秒

            # 提取完整内容
            full_content = await self._extract_content_from_page(page)

            # 提取图片（如果启用）
            images = []
            if self.extract_images:
                images = await self._extract_images_from_page(page, url)

            # 关闭页面
            await page.close()

            logger.info(f"[{self.name}] 完成 ({index+1}/{total}): {len(full_content)} 字符, {len(images)} 张图片")

            # 合并结果
            return {
                **result,  # 保留原有的title, snippet等
                "full_content": full_content,
                "images": images,
                "has_full_content": True,
                "image_count": len(images)
            }

        except Exception as e:
            logger.error(f"[{self.name}] 抓取失败 ({index+1}/{total}) {url}: {e}")
            # 即使失败也保留原始结果
            return {
                **result,
                "full_content": result.get("snippet", ""),
                "images": [],
                "has_full_content": False,
                "fetch_error": str(e)
            }

    async def _extract_content_from_page(self, page) -> str:
        """
        从页面提取文本内容

        Args:
            page: Playwright页面对象

        Returns:
            提取的文本内容
        """
        try:
            # 尝试多个选择器提取主要内容
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

            # 尝试每个选择器
            for selector in content_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        if len(text) > len(content):
                            content = text
                except:
                    continue

            # 如果没找到主要内容，提取body
            if not content:
                try:
                    content = await page.evaluate("document.body.innerText")
                except:
                    content = ""

            # 清理内容
            content = content.strip()

            # 限制长度
            if len(content) > 10000:
                content = content[:10000] + "..."

            return content

        except Exception as e:
            logger.error(f"[{self.name}] 提取内容失败: {e}")
            return ""

    async def _extract_images_from_page(self, page, base_url: str) -> List[Dict[str, Any]]:
        """
        从页面提取图片

        Args:
            page: Playwright页面对象
            base_url: 页面URL（用于处理相对路径）

        Returns:
            图片列表，每个包含url, alt, width, height等信息
        """
        try:
            # 提取所有图片
            images_data = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images
                        .filter(img => {
                            // 过滤掉小图标和装饰性图片
                            const width = img.naturalWidth || img.width;
                            const height = img.naturalHeight || img.height;
                            return width >= 200 && height >= 200;  // 只要大图
                        })
                        .map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth || img.width,
                            height: img.naturalHeight || img.height
                        }))
                        .slice(0, 10);  // 最多10张图片
                }
            """)

            images = []
            for img_data in images_data:
                img_url = img_data.get("src", "")
                if not img_url or img_url.startswith("data:"):
                    continue

                # 处理相对路径
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

            logger.info(f"[{self.name}] 提取到 {len(images)} 张图片")
            return images

        except Exception as e:
            logger.error(f"[{self.name}] 提取图片失败: {e}")
            return []

    async def _download_images_for_results(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        为搜索结果下载图片到本地

        Args:
            search_results: 搜索结果列表

        Returns:
            更新后的搜索结果（图片包含本地路径）
        """
        try:
            updated_results = []

            for result in search_results:
                images = result.get('images', [])

                if images:
                    # 下载图片
                    downloaded_images = await self.image_downloader.download_images(
                        images,
                        optimize=True
                    )

                    # 更新结果
                    updated_result = result.copy()
                    updated_result['images'] = downloaded_images
                    updated_results.append(updated_result)

                    logger.info(
                        f"[{self.name}] 为 '{result.get('title', 'N/A')[:50]}' "
                        f"下载了 {len(downloaded_images)} 张图片"
                    )
                else:
                    updated_results.append(result)

            return updated_results

        except Exception as e:
            logger.error(f"[{self.name}] 下载图片失败: {e}")
            return search_results

    def search_sync(
        self,
        query: str,
        max_results: int = 10,
        region: str = "cn-zh",
        time_filter: Optional[str] = None
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
                        return new_loop.run_until_complete(self.search(query, max_results, region, time_filter=time_filter))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
                    
            except RuntimeError:
                # 没有运行的事件循环，可以直接使用asyncio.run
                return asyncio.run(self.search(query, max_results, region, time_filter=time_filter))
        except Exception as e:
            logger.error(f"[{self.name}] 同步搜索失败: {e}")
            return []
