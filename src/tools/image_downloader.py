"""


:
1. 
2. 
3. 
4. URL
"""

import os
import hashlib
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
import httpx
import aiofiles
from PIL import Image
import io


class ImageDownloader:
    """TODO: Add docstring."""

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        max_image_size: int = 2048,  # 
        quality: int = 85,  # JPEG
        max_concurrent_downloads: int = 5
    ):
        """
        

        Args:
            storage_dir: 
            max_image_size: 
            quality: JPEG (1-100)
            max_concurrent_downloads: 
        """
        self.storage_dir = storage_dir or Path("storage/images")
        self.max_image_size = max_image_size
        self.quality = quality
        self.max_concurrent_downloads = max_concurrent_downloads
        self.name = ""

        # 
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 
        self.semaphore = asyncio.Semaphore(max_concurrent_downloads)

        logger.info(
            f"[{self.name}]  "
            f"(: {self.storage_dir}, : {max_concurrent_downloads})"
        )

    async def download_image(
        self,
        url: str,
        filename: Optional[str] = None,
        optimize: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        

        Args:
            url: URL
            filename: 
            optimize: 

        Returns:
            
        """
        async with self.semaphore:
            try:
                logger.debug(f"[{self.name}] : {url[:100]}")

                # URL
                if not filename:
                    url_hash = hashlib.md5(url.encode()).hexdigest()
                    filename = f"{url_hash}.jpg"

                local_path = self.storage_dir / filename

                # 
                if local_path.exists():
                    logger.debug(f"[{self.name}] : {filename}")
                    return {
                        "url": url,
                        "local_path": str(local_path),
                        "filename": filename,
                        "cached": True
                    }

                # 
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=30.0, follow_redirects=True)

                    if response.status_code != 200:
                        logger.warning(f"[{self.name}]  ({response.status_code}): {url}")
                        return None

                    image_data = response.content

                # 
                if optimize:
                    image_data = await self._optimize_image(image_data)

                # 
                async with aiofiles.open(local_path, "wb") as f:
                    await f.write(image_data)

                logger.debug(f"[{self.name}] : {filename}")

                return {
                    "url": url,
                    "local_path": str(local_path),
                    "filename": filename,
                    "size": len(image_data),
                    "cached": False
                }

            except Exception as e:
                logger.error(f"[{self.name}]  {url[:100]}: {e}")
                return None

    async def download_images(
        self,
        images: List[Dict[str, Any]],
        optimize: bool = True
    ) -> List[Dict[str, Any]]:
        """
        

        Args:
            images:  [{"url": "", "alt": "", ...}, ...]
            optimize: 

        Returns:
            
        """
        try:
            logger.info(f"[{self.name}]  {len(images)} ")

            # 
            tasks = []
            for img in images:
                url = img.get("download_url") or img.get("url")
                if url:
                    tasks.append(self.download_image(url, optimize=optimize))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 
            downloaded_images = []
            for i, img in enumerate(images):
                if i < len(results) and results[i] and not isinstance(results[i], Exception):
                    # 
                    enhanced_img = {
                        **img,
                        **results[i]
                    }
                    downloaded_images.append(enhanced_img)
                else:
                    # 
                    downloaded_images.append(img)

            success_count = sum(1 for r in results if r and not isinstance(r, Exception))
            logger.info(f"[{self.name}] : {success_count}/{len(images)} ")

            return downloaded_images

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")
            return images

    async def _optimize_image(self, image_data: bytes) -> bytes:
        """
        

        Args:
            image_data: 

        Returns:
            
        """
        try:
            # 
            img = Image.open(io.BytesIO(image_data))

            # RGBRGBA
            if img.mode in ('RGBA', 'LA', 'P'):
                # 
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 
            if max(img.width, img.height) > self.max_image_size:
                if img.width > img.height:
                    new_width = self.max_image_size
                    new_height = int(img.height * (self.max_image_size / img.width))
                else:
                    new_height = self.max_image_size
                    new_width = int(img.width * (self.max_image_size / img.height))

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=self.quality, optimize=True)
            optimized_data = output.getvalue()

            logger.debug(
                f"[{self.name}] : "
                f"{len(image_data)} -> {len(optimized_data)} bytes "
                f"({img.width}x{img.height})"
            )

            return optimized_data

        except Exception as e:
            logger.warning(f"[{self.name}] : {e}")
            return image_data

    async def download_for_project(
        self,
        project_id: str,
        images: List[Dict[str, Any]],
        optimize: bool = True
    ) -> List[Dict[str, Any]]:
        """
        

        Args:
            project_id: ID
            images: 
            optimize: 

        Returns:
            
        """
        # 
        project_image_dir = self.storage_dir / project_id
        project_image_dir.mkdir(parents=True, exist_ok=True)

        # 
        original_dir = self.storage_dir
        self.storage_dir = project_image_dir

        try:
            result = await self.download_images(images, optimize)
            return result
        finally:
            # 
            self.storage_dir = original_dir

    def clean_old_images(self, days: int = 30):
        """
        

        Args:
            days: 
        """
        try:
            import time
            current_time = time.time()
            max_age = days * 86400  # 

            cleaned_count = 0
            for file_path in self.storage_dir.glob("**/*.jpg"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age:
                    file_path.unlink()
                    cleaned_count += 1

            logger.info(f"[{self.name}]  {cleaned_count} ")

        except Exception as e:
            logger.error(f"[{self.name}] : {e}")

    def get_storage_size(self) -> int:
        """TODO: Add docstring."""
        total_size = 0
        for file_path in self.storage_dir.glob("**/*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
