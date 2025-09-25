"""内容抽取模块"""

import re
from typing import Optional, Tuple
from playwright.async_api import Page
from bs4 import BeautifulSoup
import trafilatura
from loguru import logger

from .models import PageExtract


class ContentExtractor:
    """内容抽取器"""
    
    async def extract_page_content(
        self, 
        page: Page, 
        url: str, 
        screenshot_path: Optional[str] = None
    ) -> PageExtract:
        """
        抽取页面内容
        
        Args:
            page: Playwright页面对象
            url: 页面URL
            screenshot_path: 截图路径
            
        Returns:
            页面抽取结果
        """
        try:
            logger.debug(f"开始抽取页面内容: {url}")
            
            # 获取页面HTML
            html_content = await page.content()
            
            # 获取页面标题
            title = await self._extract_title(page, html_content)
            
            # 抽取正文
            text = self._extract_main_text(html_content)
            
            # 抽取图片信息
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
            
            logger.debug(f"内容抽取完成: {title[:50]}... ({len(text)} 字符)")
            return result
            
        except Exception as e:
            logger.error(f"抽取页面内容失败 {url}: {e}")
            return PageExtract(
                url=url,
                title="抽取失败",
                text="",
                length=0,
                screenshot_path=screenshot_path,
                error=str(e)
            )
    
    async def _extract_title(self, page: Page, html_content: str) -> str:
        """抽取页面标题"""
        try:
            # 优先使用页面标题
            title = await page.title()
            if title and title.strip():
                return title.strip()
            
            # 备用：从HTML中提取
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag and title_tag.text.strip():
                return title_tag.text.strip()
            
            # 最后备用：从og:title提取
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()
            
            return "无标题"
            
        except Exception as e:
            logger.warning(f"提取标题失败: {e}")
            return "标题提取失败"
    
    def _extract_main_text(self, html_content: str) -> str:
        """抽取正文内容"""
        try:
            # 使用trafilatura抽取正文
            text = trafilatura.extract(html_content)
            
            if text and text.strip():
                # 清理文本
                text = self._clean_text(text)
                return text
            
            # 备用方案：使用BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # 提取主要内容区域
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            return self._clean_text(text)
            
        except Exception as e:
            logger.warning(f"抽取正文失败: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    async def _extract_images(self, page: Page, html_content: str) -> Tuple[Optional[str], Optional[str]]:
        """抽取图片信息"""
        og_image_url = None
        first_image_url = None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取og:image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                og_image_url = og_image['content']
                if og_image_url.startswith('//'):
                    og_image_url = 'https:' + og_image_url
                elif og_image_url.startswith('/'):
                    base_url = await page.evaluate('window.location.origin')
                    og_image_url = base_url + og_image_url
            
            # 提取第一个图片
            img_tags = soup.find_all('img', src=True)
            for img in img_tags:
                src = img['src']
                if src and not src.startswith('data:'):  # 排除base64图片
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
            logger.warning(f"提取图片信息失败: {e}")
        
        return og_image_url, first_image_url
    
    def extract_content(self, html_content: str, url: str) -> dict:
        """从HTML内容中提取结构化内容"""
        try:
            logger.debug(f"开始提取内容: {url}")
            
            # 获取页面标题
            title = self._extract_title_from_html(html_content)
            
            # 抽取正文
            text = self._extract_main_text(html_content)
            
            # 抽取图片信息
            og_image_url, first_image_url = self._extract_images_from_html(html_content, url)
            
            # 生成摘要（取前200字符）
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
            
            logger.debug(f"内容提取完成: {title[:50]}... ({len(text)} 字符)")
            return result
            
        except Exception as e:
            logger.error(f"提取内容失败 {url}: {e}")
            return {
                'content': '',
                'summary': '',
                'metadata': {
                    'title': '提取失败',
                    'url': url,
                    'length': 0,
                    'error': str(e)
                }
            }
    
    def _extract_title_from_html(self, html_content: str) -> str:
        """从HTML中抽取页面标题"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 从title标签提取
            title_tag = soup.find('title')
            if title_tag and title_tag.text.strip():
                return title_tag.text.strip()
            
            # 从og:title提取
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()
            
            return "无标题"
            
        except Exception as e:
            logger.warning(f"提取标题失败: {e}")
            return "标题提取失败"
    
    def _extract_images_from_html(self, html_content: str, url: str) -> Tuple[Optional[str], Optional[str]]:
        """从HTML中抽取图片信息"""
        og_image_url = None
        first_image_url = None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取og:image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                og_image_url = og_image['content']
                if og_image_url.startswith('//'):
                    og_image_url = 'https:' + og_image_url
                elif og_image_url.startswith('/'):
                    from urllib.parse import urljoin
                    og_image_url = urljoin(url, og_image_url)
            
            # 提取第一个图片
            img_tags = soup.find_all('img', src=True)
            for img in img_tags:
                src = img['src']
                if src and not src.startswith('data:'):  # 排除base64图片
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
            logger.warning(f"提取图片信息失败: {e}")
        
        return og_image_url, first_image_url