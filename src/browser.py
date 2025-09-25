"""浏览器控制模块"""

import os
import hashlib
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger

from .config import DeepSearchConfig


class BrowserManager:
    """浏览器管理器"""
    
    def __init__(self, config: DeepSearchConfig):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def start(self):
        """启动浏览器"""
        try:
            logger.info(f"启动浏览器 (headless={self.config.headless})")
            
            self.playwright = await async_playwright().start()
            
            # 启动Chromium浏览器 - 增强反检测
            launch_args = [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # 加快加载速度
                '--disable-javascript-harmony-shipping',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-ipc-flooding-protection',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=launch_args
            )
            
            # 创建浏览器上下文 - 增强反检测
            self.context = await self.browser.new_context(
                user_agent=self.config.user_agent,
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            # 添加反检测脚本
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
            """)
            
            # 设置默认超时
            self.context.set_default_timeout(self.config.browser_timeout)
            
            logger.info("浏览器启动成功")
            
        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            raise
    
    async def close(self):
        """关闭浏览器"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.warning(f"关闭浏览器时出错: {e}")
    
    async def get_page_content(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            logger.debug(f"访问页面: {url}")
            
            page = await self.new_page()
            
            # 访问页面
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # 等待页面加载
            await self.wait_for_page_load(page)
            
            # 获取页面HTML内容
            content = await page.content()
            
            # 关闭页面
            await page.close()
            
            logger.debug(f"页面内容获取成功: {url}")
            return content
            
        except Exception as e:
            logger.error(f"获取页面内容失败 {url}: {e}")
            return None
    
    async def new_page(self) -> Page:
        """创建新页面"""
        if not self.context:
            raise RuntimeError("浏览器上下文未初始化")
        
        page = await self.context.new_page()
        
        # 设置页面事件监听
        page.on("console", lambda msg: logger.debug(f"Console: {msg.text}"))
        
        return page
    
    async def take_screenshot(self, page: Page, url: str) -> Optional[str]:
        """
        截取页面截图
        
        Args:
            page: 页面对象
            url: 页面URL
            
        Returns:
            截图文件路径
        """
        try:
            # 确保截图目录存在
            os.makedirs(self.config.shots_dir, exist_ok=True)
            
            # 生成截图文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            screenshot_path = os.path.join(self.config.shots_dir, f"{url_hash}.png")
            
            # 截图
            await page.screenshot(path=screenshot_path, full_page=False)
            
            logger.debug(f"截图已保存: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"截图失败 {url}: {e}")
            return None
    
    async def wait_for_page_load(self, page: Page):
        """等待页面完全加载"""
        try:
            # 等待网络空闲
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # 额外等待时间
            import asyncio
            await asyncio.sleep(self.config.page_wait_time / 1000)
            
            # 滚动页面以触发懒加载
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 4)")
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 0)")
            
        except Exception as e:
            logger.warning(f"等待页面加载时出错: {e}")