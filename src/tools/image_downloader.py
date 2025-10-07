"""
图片下载管理器

负责:
1. 下载图片到本地
2. 图片缓存管理
3. 格式转换和压缩
4. URL到本地路径的映射
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
    """图片下载管理器"""

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        max_image_size: int = 2048,  # 最大尺寸（宽或高）
        quality: int = 85,  # JPEG质量
        max_concurrent_downloads: int = 5
    ):
        """
        初始化图片下载管理器

        Args:
            storage_dir: 图片存储目录
            max_image_size: 图片最大尺寸（像素）
            quality: JPEG压缩质量 (1-100)
            max_concurrent_downloads: 最大并发下载数
        """
        self.storage_dir = storage_dir or Path("storage/images")
        self.max_image_size = max_image_size
        self.quality = quality
        self.max_concurrent_downloads = max_concurrent_downloads
        self.name = "图片下载器"

        # 创建存储目录
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 并发控制
        self.semaphore = asyncio.Semaphore(max_concurrent_downloads)

        logger.info(
            f"[{self.name}] 初始化完成 "
            f"(存储目录: {self.storage_dir}, 最大并发: {max_concurrent_downloads})"
        )

    async def download_image(
        self,
        url: str,
        filename: Optional[str] = None,
        optimize: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        下载单张图片

        Args:
            url: 图片URL
            filename: 自定义文件名（可选）
            optimize: 是否优化图片（压缩、调整大小）

        Returns:
            图片信息字典，包含本地路径
        """
        async with self.semaphore:
            try:
                logger.debug(f"[{self.name}] 下载图片: {url[:100]}")

                # 生成文件名（基于URL哈希）
                if not filename:
                    url_hash = hashlib.md5(url.encode()).hexdigest()
                    filename = f"{url_hash}.jpg"

                local_path = self.storage_dir / filename

                # 检查是否已存在
                if local_path.exists():
                    logger.debug(f"[{self.name}] 图片已存在，跳过下载: {filename}")
                    return {
                        "url": url,
                        "local_path": str(local_path),
                        "filename": filename,
                        "cached": True
                    }

                # 下载图片
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=30.0, follow_redirects=True)

                    if response.status_code != 200:
                        logger.warning(f"[{self.name}] 下载失败 ({response.status_code}): {url}")
                        return None

                    image_data = response.content

                # 优化图片（可选）
                if optimize:
                    image_data = await self._optimize_image(image_data)

                # 保存到本地
                async with aiofiles.open(local_path, "wb") as f:
                    await f.write(image_data)

                logger.debug(f"[{self.name}] 下载完成: {filename}")

                return {
                    "url": url,
                    "local_path": str(local_path),
                    "filename": filename,
                    "size": len(image_data),
                    "cached": False
                }

            except Exception as e:
                logger.error(f"[{self.name}] 下载图片失败 {url[:100]}: {e}")
                return None

    async def download_images(
        self,
        images: List[Dict[str, Any]],
        optimize: bool = True
    ) -> List[Dict[str, Any]]:
        """
        批量下载图片

        Args:
            images: 图片列表 [{"url": "", "alt": "", ...}, ...]
            optimize: 是否优化图片

        Returns:
            增强后的图片列表（包含本地路径）
        """
        try:
            logger.info(f"[{self.name}] 批量下载 {len(images)} 张图片")

            # 并行下载
            tasks = []
            for img in images:
                url = img.get("download_url") or img.get("url")
                if url:
                    tasks.append(self.download_image(url, optimize=optimize))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 合并结果
            downloaded_images = []
            for i, img in enumerate(images):
                if i < len(results) and results[i] and not isinstance(results[i], Exception):
                    # 保留原始信息，添加本地路径
                    enhanced_img = {
                        **img,
                        **results[i]
                    }
                    downloaded_images.append(enhanced_img)
                else:
                    # 下载失败，仍保留原始信息
                    downloaded_images.append(img)

            success_count = sum(1 for r in results if r and not isinstance(r, Exception))
            logger.info(f"[{self.name}] 下载完成: {success_count}/{len(images)} 成功")

            return downloaded_images

        except Exception as e:
            logger.error(f"[{self.name}] 批量下载失败: {e}")
            return images

    async def _optimize_image(self, image_data: bytes) -> bytes:
        """
        优化图片（调整大小、压缩）

        Args:
            image_data: 原始图片数据

        Returns:
            优化后的图片数据
        """
        try:
            # 打开图片
            img = Image.open(io.BytesIO(image_data))

            # 转换为RGB（处理RGBA等格式）
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 调整大小（保持宽高比）
            if max(img.width, img.height) > self.max_image_size:
                if img.width > img.height:
                    new_width = self.max_image_size
                    new_height = int(img.height * (self.max_image_size / img.width))
                else:
                    new_height = self.max_image_size
                    new_width = int(img.width * (self.max_image_size / img.height))

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 保存为JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=self.quality, optimize=True)
            optimized_data = output.getvalue()

            logger.debug(
                f"[{self.name}] 图片优化: "
                f"{len(image_data)} -> {len(optimized_data)} bytes "
                f"({img.width}x{img.height})"
            )

            return optimized_data

        except Exception as e:
            logger.warning(f"[{self.name}] 图片优化失败，使用原始数据: {e}")
            return image_data

    async def download_for_project(
        self,
        project_id: str,
        images: List[Dict[str, Any]],
        optimize: bool = True
    ) -> List[Dict[str, Any]]:
        """
        为特定项目下载图片

        Args:
            project_id: 项目ID
            images: 图片列表
            optimize: 是否优化

        Returns:
            包含本地路径的图片列表
        """
        # 为项目创建独立的图片目录
        project_image_dir = self.storage_dir / project_id
        project_image_dir.mkdir(parents=True, exist_ok=True)

        # 临时修改存储目录
        original_dir = self.storage_dir
        self.storage_dir = project_image_dir

        try:
            result = await self.download_images(images, optimize)
            return result
        finally:
            # 恢复原始目录
            self.storage_dir = original_dir

    def clean_old_images(self, days: int = 30):
        """
        清理旧图片

        Args:
            days: 保留天数
        """
        try:
            import time
            current_time = time.time()
            max_age = days * 86400  # 转换为秒

            cleaned_count = 0
            for file_path in self.storage_dir.glob("**/*.jpg"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age:
                    file_path.unlink()
                    cleaned_count += 1

            logger.info(f"[{self.name}] 清理了 {cleaned_count} 个旧图片文件")

        except Exception as e:
            logger.error(f"[{self.name}] 清理旧图片失败: {e}")

    def get_storage_size(self) -> int:
        """获取存储目录大小（字节）"""
        total_size = 0
        for file_path in self.storage_dir.glob("**/*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
