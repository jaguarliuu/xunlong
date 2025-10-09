"""TODO: Add docstring."""

import os
import hashlib
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger

from .config import DeepSearchConfig


class BrowserManager:
    """TODO: Add docstring."""
    
    def __init__(self, config: DeepSearchConfig):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def __aenter__(self):
        """TODO: Add docstring."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """TODO: Add docstring."""
        await self.close()
    
    async def start(self):
        """TODO: Add docstring."""
        try:
            logger.info(f" (headless={self.config.headless})")
            
            self.playwright = await async_playwright().start()
            
            # Chromium - 
            launch_args = [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # 
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
            
            #  - 
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
            
            # 
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
            
            # 
            self.context.set_default_timeout(self.config.browser_timeout)
            
            logger.info("")
            
        except Exception as e:
            logger.error(f": {e}")
            raise
    
    async def close(self):
        """TODO: Add docstring."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("")
        except Exception as e:
            logger.warning(f": {e}")
    
    async def get_page_content(self, url: str) -> Optional[str]:
        """TODO: Add docstring."""
        try:
            logger.debug(f": {url}")
            
            page = await self.new_page()
            
            # 
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # 
            await self.wait_for_page_load(page)
            
            # HTML
            content = await page.content()
            
            # 
            await page.close()
            
            logger.debug(f": {url}")
            return content
            
        except Exception as e:
            logger.error(f" {url}: {e}")
            return None
    
    async def new_page(self) -> Page:
        """TODO: Add docstring."""
        if not self.context:
            raise RuntimeError("")
        
        page = await self.context.new_page()
        
        # 
        page.on("console", lambda msg: logger.debug(f"Console: {msg.text}"))
        
        return page
    
    async def take_screenshot(self, page: Page, url: str) -> Optional[str]:
        """
        
        
        Args:
            page: 
            url: URL
            
        Returns:
            
        """
        try:
            # 
            os.makedirs(self.config.shots_dir, exist_ok=True)
            
            # 
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            screenshot_path = os.path.join(self.config.shots_dir, f"{url_hash}.png")
            
            # 
            await page.screenshot(path=screenshot_path, full_page=False)
            
            logger.debug(f": {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f" {url}: {e}")
            return None
    
    async def wait_for_page_load(self, page: Page):
        """TODO: Add docstring."""
        try:
            # 
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # 
            import asyncio
            await asyncio.sleep(self.config.page_wait_time / 1000)
            
            # 
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 4)")
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 0)")
            
        except Exception as e:
            logger.warning(f": {e}")