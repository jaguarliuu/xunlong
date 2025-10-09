"""TODO: Add docstring."""

import re
from typing import Optional, Tuple
from playwright.async_api import Page
from bs4 import BeautifulSoup
import trafilatura
from loguru import logger

from .models import PageExtract


class ContentExtractor:
    """TODO: Add docstring."""
    
    async def extract_page_content(
        self, 
        page: Page, 
        url: str, 
        screenshot_path: Optional[str] = None
    ) -> PageExtract:
        """
        
        
        Args:
            page: Playwright
            url: URL
            screenshot_path: 
            
        Returns:
            
        """
        try:
            logger.debug(f": {url}")
            
            # HTML
            html_content = await page.content()
            
            # 
            title = await self._extract_title(page, html_content)
            
            # 
            text = self._extract_main_text(html_content)
            
            # 
            og_image_url, first_image_url = await self._extract_images(page, html_content)
            
            result = PageExtract(
                url=url,
                title=title,
                text=text,
                length=len(text),
                screenshot_path=screenshot_path,
                og_image_url=og_image_url,
                first_image_url=first_image_url
            )
            
            logger.debug(f": {title[:50]}... ({len(text)} )")
            return result
            
        except Exception as e:
            logger.error(f" {url}: {e}")
            return PageExtract(
                url=url,
                title="",
                text="",
                length=0,
                screenshot_path=screenshot_path,
                error=str(e)
            )
    
    async def _extract_title(self, page: Page, html_content: str) -> str:
        """TODO: Add docstring."""
        try:
            # 
            title = await page.title()
            if title and title.strip():
                return title.strip()
            
            # HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag and title_tag.text.strip():
                return title_tag.text.strip()
            
            # og:title
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()
            
            return ""
            
        except Exception as e:
            logger.warning(f": {e}")
            return ""
    
    def _extract_main_text(self, html_content: str) -> str:
        """TODO: Add docstring."""
        try:
            # trafilatura
            text = trafilatura.extract(html_content)
            
            if text and text.strip():
                # 
                text = self._clean_text(text)
                return text
            
            # BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # 
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            return self._clean_text(text)
            
        except Exception as e:
            logger.warning(f": {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """TODO: Add docstring."""
        if not text:
            return ""
        
        # 
        text = re.sub(r'\s+', ' ', text)
        
        # 
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    async def _extract_images(self, page: Page, html_content: str) -> Tuple[Optional[str], Optional[str]]:
        """TODO: Add docstring."""
        og_image_url = None
        first_image_url = None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # og:image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                og_image_url = og_image['content']
                if og_image_url.startswith('//'):
                    og_image_url = 'https:' + og_image_url
                elif og_image_url.startswith('/'):
                    base_url = await page.evaluate('window.location.origin')
                    og_image_url = base_url + og_image_url
            
            # 
            img_tags = soup.find_all('img', src=True)
            for img in img_tags:
                src = img['src']
                if src and not src.startswith('data:'):  # base64
                    if src.startswith('//'):
                        first_image_url = 'https:' + src
                    elif src.startswith('/'):
                        base_url = await page.evaluate('window.location.origin')
                        first_image_url = base_url + src
                    elif src.startswith('http'):
                        first_image_url = src
                    
                    if first_image_url:
                        break
            
        except Exception as e:
            logger.warning(f": {e}")
        
        return og_image_url, first_image_url
    
    def extract_content(self, html_content: str, url: str) -> dict:
        """HTML"""
        try:
            logger.debug(f": {url}")
            
            # 
            title = self._extract_title_from_html(html_content)
            
            # 
            text = self._extract_main_text(html_content)
            
            # 
            og_image_url, first_image_url = self._extract_images_from_html(html_content, url)
            
            # 200
            summary = text[:200] + "..." if len(text) > 200 else text
            
            result = {
                'content': text,
                'summary': summary,
                'metadata': {
                    'title': title,
                    'url': url,
                    'length': len(text),
                    'og_image_url': og_image_url,
                    'first_image_url': first_image_url
                }
            }
            
            logger.debug(f": {title[:50]}... ({len(text)} )")
            return result
            
        except Exception as e:
            logger.error(f" {url}: {e}")
            return {
                'content': '',
                'summary': '',
                'metadata': {
                    'title': '',
                    'url': url,
                    'length': 0,
                    'error': str(e)
                }
            }
    
    def _extract_title_from_html(self, html_content: str) -> str:
        """HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # title
            title_tag = soup.find('title')
            if title_tag and title_tag.text.strip():
                return title_tag.text.strip()
            
            # og:title
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()
            
            return ""
            
        except Exception as e:
            logger.warning(f": {e}")
            return ""
    
    def _extract_images_from_html(self, html_content: str, url: str) -> Tuple[Optional[str], Optional[str]]:
        """HTML"""
        og_image_url = None
        first_image_url = None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # og:image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                og_image_url = og_image['content']
                if og_image_url.startswith('//'):
                    og_image_url = 'https:' + og_image_url
                elif og_image_url.startswith('/'):
                    from urllib.parse import urljoin
                    og_image_url = urljoin(url, og_image_url)
            
            # 
            img_tags = soup.find_all('img', src=True)
            for img in img_tags:
                src = img['src']
                if src and not src.startswith('data:'):  # base64
                    if src.startswith('//'):
                        first_image_url = 'https:' + src
                    elif src.startswith('/'):
                        from urllib.parse import urljoin
                        first_image_url = urljoin(url, src)
                    elif src.startswith('http'):
                        first_image_url = src
                    
                    if first_image_url:
                        break
            
        except Exception as e:
            logger.warning(f": {e}")
        
        return og_image_url, first_image_url