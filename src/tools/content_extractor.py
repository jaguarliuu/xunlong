"""
内容提取工具 - 从网页提取内容
"""
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from loguru import logger
from bs4 import BeautifulSoup
import re

class ContentExtractor:
    """内容提取器"""
    
    def __init__(self):
        self.name = "内容提取器"
        self.timeout = 30
        
    async def extract_content(self, url: str) -> Dict[str, Any]:
        """从URL提取内容"""

        try:
            logger.debug(f"[{self.name}] 提取内容: {url}")

            # 检查是否是PDF或其他二进制文件
            if url.lower().endswith('.pdf') or url.lower().endswith('.doc') or url.lower().endswith('.docx'):
                logger.warning(f"[{self.name}] 跳过二进制文件: {url}")
                return {"url": url, "title": "", "content": "", "error": "不支持的文件类型（PDF/DOC）"}

            # 获取网页内容
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }

                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status != 200:
                        logger.warning(f"[{self.name}] HTTP {response.status}: {url}")
                        return {"url": url, "title": "", "content": "", "error": f"HTTP {response.status}"}

                    # 检查Content-Type，如果是PDF则跳过
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'pdf' in content_type or 'application/octet-stream' in content_type:
                        logger.warning(f"[{self.name}] 跳过二进制内容: {url} (Content-Type: {content_type})")
                        return {"url": url, "title": "", "content": "", "error": "二进制文件类型"}

                    html = await response.text(errors='ignore')  # 忽略编码错误
            
            # 解析HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取标题
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # 移除脚本和样式
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # 提取主要内容
            content = ""
            
            # 尝试找到主要内容区域
            main_selectors = [
                'main', 'article', '.content', '.post', '.entry',
                '#content', '#main', '.main-content', '.article-content'
            ]
            
            main_content = None
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                content = main_content.get_text()
            else:
                # 如果没找到主要内容区域，提取body内容
                body = soup.find('body')
                if body:
                    content = body.get_text()
                else:
                    content = soup.get_text()
            
            # 清理内容
            content = self._clean_text(content)
            
            # 限制内容长度
            if len(content) > 5000:
                content = content[:5000] + "..."
            
            result = {
                "url": url,
                "title": title,
                "content": content,
                "content_length": len(content),
                "extraction_time": asyncio.get_event_loop().time()
            }
            
            logger.debug(f"[{self.name}] 提取完成: {len(content)} 字符")
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"[{self.name}] 提取超时: {url}")
            return {"url": url, "title": "", "content": "", "error": "timeout"}
        except Exception as e:
            logger.error(f"[{self.name}] 提取失败 {url}: {e}")
            return {"url": url, "title": "", "content": "", "error": str(e)}
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()""''—\\-]', '', text)
        
        # 移除过短的行
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        return '\n'.join(cleaned_lines).strip()