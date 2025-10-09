"""


Markdown
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import re


class ImageProcessor:
    """TODO: Add docstring."""

    @staticmethod
    def insert_images_to_content(
        content: str,
        images: List[Dict[str, Any]],
        mode: str = "smart"
    ) -> str:
        """
        

        Args:
            content: Markdown
            images:  [{"url": "", "alt": "", "width": 0, "height": 0}, ...]
            mode: 
                - "smart": alt
                - "top": 
                - "bottom": 
                - "distribute": 
                - "none": 

        Returns:
            Markdown
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
            logger.warning(f": {mode}(bottom)")
            return ImageProcessor._insert_images_at_bottom(content, images)

    @staticmethod
    def _insert_images_at_top(content: str, images: List[Dict[str, Any]]) -> str:
        """TODO: Add docstring."""
        image_markdown = ImageProcessor._generate_image_gallery(images, title="")
        return f"{image_markdown}\n\n{content}"

    @staticmethod
    def _insert_images_at_bottom(content: str, images: List[Dict[str, Any]]) -> str:
        """TODO: Add docstring."""
        image_markdown = ImageProcessor._generate_image_gallery(images, title="")
        return f"{content}\n\n{image_markdown}"

    @staticmethod
    def _distribute_images(content: str, images: List[Dict[str, Any]]) -> str:
        """TODO: Add docstring."""
        if not images:
            return content

        # 
        paragraphs = content.split('\n\n')

        if len(paragraphs) <= 1:
            # 
            return ImageProcessor._insert_images_at_bottom(content, images)

        # 
        interval = max(1, len(paragraphs) // (len(images) + 1))

        result_parts = []
        image_index = 0

        for i, para in enumerate(paragraphs):
            result_parts.append(para)

            # interval
            if image_index < len(images) and (i + 1) % interval == 0:
                img = images[image_index]
                img_md = ImageProcessor._format_single_image(img)
                result_parts.append(img_md)
                image_index += 1

        # 
        while image_index < len(images):
            img_md = ImageProcessor._format_single_image(images[image_index])
            result_parts.append(img_md)
            image_index += 1

        return '\n\n'.join(result_parts)

    @staticmethod
    def _smart_insert_images(content: str, images: List[Dict[str, Any]]) -> str:
        """
        

        
        1. alt
        2. 
        """
        if not images:
            return content

        # 
        paragraphs = content.split('\n\n')

        if len(paragraphs) <= 1:
            return ImageProcessor._insert_images_at_bottom(content, images)

        inserted_images = set()  # 
        result_parts = []

        for para in paragraphs:
            result_parts.append(para)

            # 
            for i, img in enumerate(images):
                if i in inserted_images:
                    continue

                # alt
                alt = img.get('alt', '').lower()
                para_lower = para.lower()

                if alt and len(alt) > 3:
                    # alt
                    keywords = [w for w in re.findall(r'\w+', alt) if len(w) > 2]

                    # 
                    if keywords and any(kw.lower() in para_lower for kw in keywords):
                        # 
                        img_md = ImageProcessor._format_single_image(img)
                        result_parts.append(img_md)
                        inserted_images.add(i)
                        break  # 

        # 
        remaining_images = [img for i, img in enumerate(images) if i not in inserted_images]
        if remaining_images:
            gallery = ImageProcessor._generate_image_gallery(
                remaining_images,
                title=""
            )
            result_parts.append(gallery)

        return '\n\n'.join(result_parts)

    @staticmethod
    def _format_single_image(img: Dict[str, Any]) -> str:
        """Markdown"""
        # URL
        local_path = img.get('local_path', '')
        url = img.get('url', '')
        image_url = local_path if local_path else url

        alt = img.get('alt', '')
        width = img.get('width', 0)
        height = img.get('height', 0)

        # 
        source = img.get('source', '')
        photographer = img.get('photographer', '')

        # Markdown
        img_md = f"![{alt}]({image_url})"

        # 
        metadata_parts = []
        if width and height:
            metadata_parts.append(f": {width}x{height}")
        if photographer:
            metadata_parts.append(f": {photographer}")
        if source:
            metadata_parts.append(f": {source}")

        if metadata_parts:
            img_md += f"\n*{' | '.join(metadata_parts)}*"

        return img_md

    @staticmethod
    def _generate_image_gallery(
        images: List[Dict[str, Any]],
        title: str = ""
    ) -> str:
        """TODO: Add docstring."""
        if not images:
            return ""

        parts = [f"## {title}\n"]

        for i, img in enumerate(images, 1):
            # 
            local_path = img.get('local_path', '')
            url = img.get('url', '')
            image_url = local_path if local_path else url

            alt = img.get('alt', f'{i}')
            width = img.get('width', 0)
            height = img.get('height', 0)
            photographer = img.get('photographer', '')
            photographer_url = img.get('photographer_url', '')

            parts.append(f"### {i}. {alt if alt else f'{i}'}")
            parts.append(f"![{alt}]({image_url})")

            # 
            metadata_parts = []
            if width and height:
                metadata_parts.append(f": {width}x{height}")
            if photographer:
                if photographer_url:
                    metadata_parts.append(f": [{photographer}]({photographer_url})")
                else:
                    metadata_parts.append(f": {photographer}")

            if metadata_parts:
                parts.append(f"*{' | '.join(metadata_parts)}*")

            parts.append("")  # 

        return '\n'.join(parts)

    @staticmethod
    def enhance_search_results_with_images(
        results: List[Dict[str, Any]],
        mode: str = "smart"
    ) -> List[Dict[str, Any]]:
        """
        

        Args:
            results: 
            mode: 

        Returns:
            
        """
        enhanced_results = []

        for result in results:
            enhanced_result = result.copy()

            # 
            full_content = result.get('full_content', '')
            images = result.get('images', [])

            if full_content and images:
                # 
                enhanced_content = ImageProcessor.insert_images_to_content(
                    full_content,
                    images,
                    mode=mode
                )
                enhanced_result['full_content'] = enhanced_content
                enhanced_result['images_inserted'] = True
                enhanced_result['image_insert_mode'] = mode

                logger.info(
                    f" {len(images)}  "
                    f"({result.get('title', 'N/A')[:50]}...)"
                )
            else:
                enhanced_result['images_inserted'] = False

            enhanced_results.append(enhanced_result)

        return enhanced_results
