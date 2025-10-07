"""
图片搜索工具 - 支持多种图片来源API

集成:
1. Unsplash API - 高质量摄影作品
2. Pexels API - 免费图片库
3. 可扩展到其他图片源
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
import httpx
from pathlib import Path


class ImageSearcher:
    """图片搜索器 - 从专业图片库获取高质量配图"""

    def __init__(
        self,
        unsplash_access_key: Optional[str] = None,
        pexels_api_key: Optional[str] = None,
        prefer_source: str = "unsplash"  # unsplash 或 pexels
    ):
        """
        初始化图片搜索器

        Args:
            unsplash_access_key: Unsplash API密钥
            pexels_api_key: Pexels API密钥
            prefer_source: 优先使用的图片源
        """
        self.unsplash_access_key = unsplash_access_key or os.getenv("UNSPLASH_ACCESS_KEY")
        self.pexels_api_key = pexels_api_key or os.getenv("PEXELS_API_KEY")
        self.prefer_source = prefer_source
        self.name = "图片搜索器"

        # API端点
        self.unsplash_api_url = "https://api.unsplash.com"
        self.pexels_api_url = "https://api.pexels.com/v1"

        logger.info(
            f"[{self.name}] 初始化完成 "
            f"(Unsplash: {'✓' if self.unsplash_access_key else '✗'}, "
            f"Pexels: {'✓' if self.pexels_api_key else '✗'})"
        )

    async def search_images(
        self,
        query: str,
        count: int = 5,
        orientation: str = "landscape"  # landscape, portrait, squarish
    ) -> List[Dict[str, Any]]:
        """
        搜索相关图片

        Args:
            query: 搜索关键词
            count: 需要的图片数量
            orientation: 图片方向

        Returns:
            图片信息列表 [{"url": "", "download_url": "", "alt": "", ...}]
        """
        try:
            logger.info(f"[{self.name}] 搜索图片: {query} (数量: {count})")

            # 优先使用配置的图片源
            if self.prefer_source == "unsplash" and self.unsplash_access_key:
                images = await self._search_unsplash(query, count, orientation)
            elif self.prefer_source == "pexels" and self.pexels_api_key:
                images = await self._search_pexels(query, count, orientation)
            else:
                # 降级策略：尝试可用的API
                if self.unsplash_access_key:
                    images = await self._search_unsplash(query, count, orientation)
                elif self.pexels_api_key:
                    images = await self._search_pexels(query, count, orientation)
                else:
                    logger.warning(f"[{self.name}] 未配置任何图片API密钥")
                    return []

            logger.info(f"[{self.name}] 搜索完成，获得 {len(images)} 张图片")
            return images

        except Exception as e:
            logger.error(f"[{self.name}] 搜索图片失败: {e}")
            return []

    async def _search_unsplash(
        self,
        query: str,
        count: int,
        orientation: str
    ) -> List[Dict[str, Any]]:
        """
        使用Unsplash API搜索图片

        文档: https://unsplash.com/documentation
        """
        try:
            logger.info(f"[{self.name}] 使用Unsplash API搜索")

            async with httpx.AsyncClient() as client:
                # 搜索图片
                response = await client.get(
                    f"{self.unsplash_api_url}/search/photos",
                    params={
                        "query": query,
                        "per_page": count,
                        "orientation": orientation
                    },
                    headers={
                        "Authorization": f"Client-ID {self.unsplash_access_key}"
                    },
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"[{self.name}] Unsplash API错误: {response.status_code}")
                    return []

                data = response.json()
                results = data.get("results", [])

                # 格式化结果
                images = []
                for item in results:
                    images.append({
                        "source": "unsplash",
                        "id": item.get("id"),
                        "url": item.get("urls", {}).get("regular"),  # 显示URL
                        "download_url": item.get("urls", {}).get("raw"),  # 下载URL
                        "alt": item.get("alt_description") or item.get("description") or query,
                        "width": item.get("width"),
                        "height": item.get("height"),
                        "photographer": item.get("user", {}).get("name"),
                        "photographer_url": item.get("user", {}).get("links", {}).get("html"),
                        "color": item.get("color"),
                        "likes": item.get("likes", 0)
                    })

                return images

        except Exception as e:
            logger.error(f"[{self.name}] Unsplash搜索失败: {e}")
            return []

    async def _search_pexels(
        self,
        query: str,
        count: int,
        orientation: str
    ) -> List[Dict[str, Any]]:
        """
        使用Pexels API搜索图片

        文档: https://www.pexels.com/api/documentation/
        """
        try:
            logger.info(f"[{self.name}] 使用Pexels API搜索")

            async with httpx.AsyncClient() as client:
                # 搜索图片
                response = await client.get(
                    f"{self.pexels_api_url}/search",
                    params={
                        "query": query,
                        "per_page": count,
                        "orientation": orientation
                    },
                    headers={
                        "Authorization": self.pexels_api_key
                    },
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"[{self.name}] Pexels API错误: {response.status_code}")
                    return []

                data = response.json()
                results = data.get("photos", [])

                # 格式化结果
                images = []
                for item in results:
                    images.append({
                        "source": "pexels",
                        "id": item.get("id"),
                        "url": item.get("src", {}).get("large"),  # 显示URL
                        "download_url": item.get("src", {}).get("original"),  # 下载URL
                        "alt": item.get("alt") or query,
                        "width": item.get("width"),
                        "height": item.get("height"),
                        "photographer": item.get("photographer"),
                        "photographer_url": item.get("photographer_url"),
                        "avg_color": item.get("avg_color")
                    })

                return images

        except Exception as e:
            logger.error(f"[{self.name}] Pexels搜索失败: {e}")
            return []

    async def search_images_for_sections(
        self,
        sections: List[Dict[str, Any]],
        images_per_section: int = 2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        为多个章节批量搜索图片

        Args:
            sections: 章节列表 [{"title": "", "content": ""}, ...]
            images_per_section: 每个章节的图片数量

        Returns:
            章节ID到图片列表的映射
        """
        try:
            logger.info(f"[{self.name}] 为 {len(sections)} 个章节批量搜索图片")

            tasks = []
            for section in sections:
                # 使用章节标题作为搜索关键词
                query = section.get("title", "")
                if query:
                    tasks.append(self.search_images(query, images_per_section))

            # 并行搜索
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 构建映射
            section_images = {}
            for i, section in enumerate(sections):
                section_id = section.get("id") or f"section_{i}"
                if i < len(results) and not isinstance(results[i], Exception):
                    section_images[section_id] = results[i]
                else:
                    section_images[section_id] = []

            logger.info(f"[{self.name}] 批量搜索完成")
            return section_images

        except Exception as e:
            logger.error(f"[{self.name}] 批量搜索失败: {e}")
            return {}

    def is_available(self) -> bool:
        """检查是否有可用的API密钥"""
        return bool(self.unsplash_access_key or self.pexels_api_key)

    def get_available_sources(self) -> List[str]:
        """获取可用的图片源"""
        sources = []
        if self.unsplash_access_key:
            sources.append("unsplash")
        if self.pexels_api_key:
            sources.append("pexels")
        return sources
