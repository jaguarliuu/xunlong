"""
 - API

:
1. Unsplash API - 
2. Pexels API - 
3. 
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
import httpx
from pathlib import Path


class ImageSearcher:
    """ - """

    def __init__(
        self,
        unsplash_access_key: Optional[str] = None,
        pexels_api_key: Optional[str] = None,
        prefer_source: str = "unsplash"  # unsplash  pexels
    ):
        """
        

        Args:
            unsplash_access_key: Unsplash API
            pexels_api_key: Pexels API
            prefer_source: 
        """
        self.unsplash_access_key = unsplash_access_key or os.getenv("UNSPLASH_ACCESS_KEY")
        self.pexels_api_key = pexels_api_key or os.getenv("PEXELS_API_KEY")
        self.prefer_source = prefer_source
        self.name = ""

        # API
        self.unsplash_api_url = "https://api.unsplash.com"
        self.pexels_api_url = "https://api.pexels.com/v1"

        logger.info(
            f"[{self.name}]  "
            f"(Unsplash: {'' if self.unsplash_access_key else ''}, "
            f"Pexels: {'' if self.pexels_api_key else ''})"
        )

    async def search_images(
        self,
        query: str,
        count: int = 5,
        orientation: str = "landscape"  # landscape, portrait, squarish
    ) -> List[Dict[str, Any]]:
        """
        

        Args:
            query: 
            count: 
            orientation: 

        Returns:
             [{"url": "", "download_url": "", "alt": "", ...}]
        """
        try:
            logger.info(f"[{self.name}] : {query} (: {count})")

            # 
            if self.prefer_source == "unsplash" and self.unsplash_access_key:
                images = await self._search_unsplash(query, count, orientation)
            elif self.prefer_source == "pexels" and self.pexels_api_key:
                images = await self._search_pexels(query, count, orientation)
            else:
                # API
                if self.unsplash_access_key:
                    images = await self._search_unsplash(query, count, orientation)
                elif self.pexels_api_key:
                    images = await self._search_pexels(query, count, orientation)
                else:
                    logger.warning(f"[{self.name}] API")
                    return []

            logger.info(f"[{self.name}]  {len(images)} ")
            return images

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return []

    async def _search_unsplash(
        self,
        query: str,
        count: int,
        orientation: str
    ) -> List[Dict[str, Any]]:
        """
        Unsplash API

        : https://unsplash.com/documentation
        """
        try:
            logger.info(f"[{self.name}] Unsplash API")

            async with httpx.AsyncClient() as client:
                # 
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
                    logger.error(f"[{self.name}] Unsplash API: {response.status_code}")
                    return []

                data = response.json()
                results = data.get("results", [])

                # 
                images = []
                for item in results:
                    images.append({
                        "source": "unsplash",
                        "id": item.get("id"),
                        "url": item.get("urls", {}).get("regular"),  # URL
                        "download_url": item.get("urls", {}).get("raw"),  # URL
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
            logger.error(f"[{self.name}] Unsplash: {e}")
            return []

    async def _search_pexels(
        self,
        query: str,
        count: int,
        orientation: str
    ) -> List[Dict[str, Any]]:
        """
        Pexels API

        : https://www.pexels.com/api/documentation/
        """
        try:
            logger.info(f"[{self.name}] Pexels API")

            async with httpx.AsyncClient() as client:
                # 
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
                    logger.error(f"[{self.name}] Pexels API: {response.status_code}")
                    return []

                data = response.json()
                results = data.get("photos", [])

                # 
                images = []
                for item in results:
                    images.append({
                        "source": "pexels",
                        "id": item.get("id"),
                        "url": item.get("src", {}).get("large"),  # URL
                        "download_url": item.get("src", {}).get("original"),  # URL
                        "alt": item.get("alt") or query,
                        "width": item.get("width"),
                        "height": item.get("height"),
                        "photographer": item.get("photographer"),
                        "photographer_url": item.get("photographer_url"),
                        "avg_color": item.get("avg_color")
                    })

                return images

        except Exception as e:
            logger.error(f"[{self.name}] Pexels: {e}")
            return []

    async def search_images_for_sections(
        self,
        sections: List[Dict[str, Any]],
        images_per_section: int = 2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        

        Args:
            sections:  [{"title": "", "content": ""}, ...]
            images_per_section: 

        Returns:
            ID
        """
        try:
            logger.info(f"[{self.name}]  {len(sections)} ")

            tasks = []
            for section in sections:
                # 
                query = section.get("title", "")
                if query:
                    tasks.append(self.search_images(query, images_per_section))

            # 
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 
            section_images = {}
            for i, section in enumerate(sections):
                section_id = section.get("id") or f"section_{i}"
                if i < len(results) and not isinstance(results[i], Exception):
                    section_images[section_id] = results[i]
                else:
                    section_images[section_id] = []

            logger.info(f"[{self.name}] ")
            return section_images

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return {}

    def is_available(self) -> bool:
        """API"""
        return bool(self.unsplash_access_key or self.pexels_api_key)

    def get_available_sources(self) -> List[str]:
        """TODO: Add docstring."""
        sources = []
        if self.unsplash_access_key:
            sources.append("unsplash")
        if self.pexels_api_key:
            sources.append("pexels")
        return sources
