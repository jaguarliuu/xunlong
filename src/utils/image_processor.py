"""
图片处理工具

处理搜索结果中的图片，智能插入到Markdown内容中
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import re


class ImageProcessor:
    """图片处理器"""

    @staticmethod
    def insert_images_to_content(
        content: str,
        images: List[Dict[str, Any]],
        mode: str = "smart"
    ) -> str:
        """
        将图片插入到内容中

        Args:
            content: 原始Markdown内容
            images: 图片列表 [{"url": "", "alt": "", "width": 0, "height": 0}, ...]
            mode: 插入模式
                - "smart": 智能插入（根据图片alt和内容相关性）
                - "top": 所有图片放在开头
                - "bottom": 所有图片放在末尾（附录）
                - "distribute": 均匀分布在段落之间
                - "none": 不插入

        Returns:
            插入图片后的Markdown内容
        """
        if not images or mode == "none":
            return content

        if mode == "top":
            return ImageProcessor._insert_images_at_top(content, images)
        elif mode == "bottom":
            return ImageProcessor._insert_images_at_bottom(content, images)
        elif mode == "distribute":
            return ImageProcessor._distribute_images(content, images)
        elif mode == "smart":
            return ImageProcessor._smart_insert_images(content, images)
        else:
            logger.warning(f"未知的图片插入模式: {mode}，使用默认模式(bottom)")
            return ImageProcessor._insert_images_at_bottom(content, images)

    @staticmethod
    def _insert_images_at_top(content: str, images: List[Dict[str, Any]]) -> str:
        """在内容开头插入所有图片"""
        image_markdown = ImageProcessor._generate_image_gallery(images, title="相关图片")
        return f"{image_markdown}\n\n{content}"

    @staticmethod
    def _insert_images_at_bottom(content: str, images: List[Dict[str, Any]]) -> str:
        """在内容末尾插入所有图片（附录模式）"""
        image_markdown = ImageProcessor._generate_image_gallery(images, title="相关图片")
        return f"{content}\n\n{image_markdown}"

    @staticmethod
    def _distribute_images(content: str, images: List[Dict[str, Any]]) -> str:
        """将图片均匀分布在段落之间"""
        if not images:
            return content

        # 按段落分割内容（双换行符分割）
        paragraphs = content.split('\n\n')

        if len(paragraphs) <= 1:
            # 内容太短，直接放在末尾
            return ImageProcessor._insert_images_at_bottom(content, images)

        # 计算插入间隔
        interval = max(1, len(paragraphs) // (len(images) + 1))

        result_parts = []
        image_index = 0

        for i, para in enumerate(paragraphs):
            result_parts.append(para)

            # 每隔interval个段落插入一张图片
            if image_index < len(images) and (i + 1) % interval == 0:
                img = images[image_index]
                img_md = ImageProcessor._format_single_image(img)
                result_parts.append(img_md)
                image_index += 1

        # 剩余的图片放在末尾
        while image_index < len(images):
            img_md = ImageProcessor._format_single_image(images[image_index])
            result_parts.append(img_md)
            image_index += 1

        return '\n\n'.join(result_parts)

    @staticmethod
    def _smart_insert_images(content: str, images: List[Dict[str, Any]]) -> str:
        """
        智能插入图片

        策略：
        1. 如果图片有alt文本，尝试在包含相关关键词的段落后插入
        2. 否则均匀分布
        """
        if not images:
            return content

        # 按段落分割
        paragraphs = content.split('\n\n')

        if len(paragraphs) <= 1:
            return ImageProcessor._insert_images_at_bottom(content, images)

        inserted_images = set()  # 记录已插入的图片索引
        result_parts = []

        for para in paragraphs:
            result_parts.append(para)

            # 尝试找到与当前段落相关的图片
            for i, img in enumerate(images):
                if i in inserted_images:
                    continue

                # 检查图片alt是否与段落内容相关
                alt = img.get('alt', '').lower()
                para_lower = para.lower()

                if alt and len(alt) > 3:
                    # 提取alt中的关键词（简单分词）
                    keywords = [w for w in re.findall(r'\w+', alt) if len(w) > 2]

                    # 检查段落中是否包含这些关键词
                    if keywords and any(kw.lower() in para_lower for kw in keywords):
                        # 插入这张图片
                        img_md = ImageProcessor._format_single_image(img)
                        result_parts.append(img_md)
                        inserted_images.add(i)
                        break  # 每个段落最多插入一张图片

        # 剩余未插入的图片放在末尾
        remaining_images = [img for i, img in enumerate(images) if i not in inserted_images]
        if remaining_images:
            gallery = ImageProcessor._generate_image_gallery(
                remaining_images,
                title="其他相关图片"
            )
            result_parts.append(gallery)

        return '\n\n'.join(result_parts)

    @staticmethod
    def _format_single_image(img: Dict[str, Any]) -> str:
        """格式化单张图片为Markdown"""
        # 优先使用本地路径，其次是URL
        local_path = img.get('local_path', '')
        url = img.get('url', '')
        image_url = local_path if local_path else url

        alt = img.get('alt', '图片')
        width = img.get('width', 0)
        height = img.get('height', 0)

        # 来源信息
        source = img.get('source', '')
        photographer = img.get('photographer', '')

        # 基础Markdown图片语法
        img_md = f"![{alt}]({image_url})"

        # 添加元数据（作为注释）
        metadata_parts = []
        if width and height:
            metadata_parts.append(f"尺寸: {width}x{height}")
        if photographer:
            metadata_parts.append(f"摄影师: {photographer}")
        if source:
            metadata_parts.append(f"来源: {source}")

        if metadata_parts:
            img_md += f"\n*{' | '.join(metadata_parts)}*"

        return img_md

    @staticmethod
    def _generate_image_gallery(
        images: List[Dict[str, Any]],
        title: str = "相关图片"
    ) -> str:
        """生成图片画廊"""
        if not images:
            return ""

        parts = [f"## {title}\n"]

        for i, img in enumerate(images, 1):
            # 优先使用本地路径
            local_path = img.get('local_path', '')
            url = img.get('url', '')
            image_url = local_path if local_path else url

            alt = img.get('alt', f'图片{i}')
            width = img.get('width', 0)
            height = img.get('height', 0)
            photographer = img.get('photographer', '')
            photographer_url = img.get('photographer_url', '')

            parts.append(f"### {i}. {alt if alt else f'图片{i}'}")
            parts.append(f"![{alt}]({image_url})")

            # 添加元数据
            metadata_parts = []
            if width and height:
                metadata_parts.append(f"尺寸: {width}x{height}")
            if photographer:
                if photographer_url:
                    metadata_parts.append(f"摄影师: [{photographer}]({photographer_url})")
                else:
                    metadata_parts.append(f"摄影师: {photographer}")

            if metadata_parts:
                parts.append(f"*{' | '.join(metadata_parts)}*")

            parts.append("")  # 空行

        return '\n'.join(parts)

    @staticmethod
    def enhance_search_results_with_images(
        results: List[Dict[str, Any]],
        mode: str = "smart"
    ) -> List[Dict[str, Any]]:
        """
        增强搜索结果，将图片插入到内容中

        Args:
            results: 搜索结果列表
            mode: 图片插入模式

        Returns:
            增强后的搜索结果
        """
        enhanced_results = []

        for result in results:
            enhanced_result = result.copy()

            # 获取完整内容和图片
            full_content = result.get('full_content', '')
            images = result.get('images', [])

            if full_content and images:
                # 插入图片
                enhanced_content = ImageProcessor.insert_images_to_content(
                    full_content,
                    images,
                    mode=mode
                )
                enhanced_result['full_content'] = enhanced_content
                enhanced_result['images_inserted'] = True
                enhanced_result['image_insert_mode'] = mode

                logger.info(
                    f"已将 {len(images)} 张图片插入到内容中 "
                    f"({result.get('title', 'N/A')[:50]}...)"
                )
            else:
                enhanced_result['images_inserted'] = False

            enhanced_results.append(enhanced_result)

        return enhanced_results
