"""


:
1.  (Unsplash/Pexels)
2. 
3. Markdown
4. 
"""

import asyncio
import sys
from pathlib import Path

# 
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.tools.image_searcher import ImageSearcher
from src.tools.image_downloader import ImageDownloader
from src.utils.image_processor import ImageProcessor


async def test_image_search():
    """TODO: Add docstring."""
    logger.info("=" * 60)
    logger.info("1: ")
    logger.info("=" * 60)

    searcher = ImageSearcher()

    if not searcher.is_available():
        logger.warning("API")
        logger.info(" .env  UNSPLASH_ACCESS_KEY  PEXELS_API_KEY")
        return None

    logger.info(f": {searcher.get_available_sources()}")

    # 
    query = "artificial intelligence technology"
    logger.info(f": {query}")

    images = await searcher.search_images(query, count=3)

    if images:
        logger.success(f"  {len(images)} ")
        for i, img in enumerate(images, 1):
            logger.info(
                f"  {i}. {img.get('alt', 'N/A')[:50]} "
                f"({img.get('width')}x{img.get('height')}) "
                f"- {img.get('source', 'unknown')}"
            )
        return images
    else:
        logger.error(" ")
        return None


async def test_image_download(images):
    """TODO: Add docstring."""
    logger.info("\n" + "=" * 60)
    logger.info("2: ")
    logger.info("=" * 60)

    if not images:
        logger.warning("")
        return None

    downloader = ImageDownloader(
        storage_dir=Path("storage/test_images"),
        max_image_size=1024,
        quality=80
    )

    logger.info(f" {len(images)} ...")
    downloaded_images = await downloader.download_images(images[:2], optimize=True)

    if downloaded_images:
        logger.success(f"  {len(downloaded_images)} ")
        for img in downloaded_images:
            if img.get('local_path'):
                logger.info(f"  - {img.get('local_path')} ({img.get('size', 0)} bytes)")
        return downloaded_images
    else:
        logger.error(" ")
        return None


def test_image_insertion(images):
    """TODO: Add docstring."""
    logger.info("\n" + "=" * 60)
    logger.info("3: Markdown")
    logger.info("=" * 60)

    if not images:
        logger.warning("")
        return

    # 
    sample_content = """
# 

(Artificial Intelligence, AI)

## 

John McCarthy1956AI

## 



## 

AI
"""

    # 
    modes = ["smart", "top", "bottom", "distribute"]

    for mode in modes:
        logger.info(f"\n: {mode}")
        result = ImageProcessor.insert_images_to_content(
            sample_content, images, mode=mode
        )

        # 
        output_file = Path(f"storage/test_images/result_{mode}.md")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result, encoding='utf-8')

        logger.success(f"  '{mode}' : {output_file}")
        logger.info(f"  : {len(result)} ")


async def test_batch_search():
    """TODO: Add docstring."""
    logger.info("\n" + "=" * 60)
    logger.info("4: ")
    logger.info("=" * 60)

    searcher = ImageSearcher()

    if not searcher.is_available():
        logger.warning("API")
        return

    # 
    sections = [
        {"id": "section_1", "title": "Machine Learning Basics"},
        {"id": "section_2", "title": "Deep Learning Networks"},
        {"id": "section_3", "title": "Natural Language Processing"},
    ]

    logger.info(f" {len(sections)} ...")
    section_images = await searcher.search_images_for_sections(sections, images_per_section=2)

    for section in sections:
        section_id = section['id']
        images = section_images.get(section_id, [])
        logger.info(f"  {section['title']}: {len(images)} ")

    logger.success(" ")


async def main():
    """TODO: Add docstring."""
    logger.info("" + "" * 58 + "")
    logger.info("" + " " * 15 + "" + " " * 25 + "")
    logger.info("" + "" * 58 + "\n")

    try:
        # 1: 
        images = await test_image_search()

        # 2: 
        if images:
            downloaded_images = await test_image_download(images)

            # 3: 
            if downloaded_images:
                test_image_insertion(downloaded_images)

        # 4: 
        await test_batch_search()

        logger.info("\n" + "=" * 60)
        logger.success(" !")
        logger.info("=" * 60)

        logger.info("\n :")
        logger.info("  - : ")
        logger.info("  - : ")
        logger.info("  - : ")
        logger.info("  - : ")

        logger.info("\n :")
        logger.info("  1.  storage/test_images/ ")
        logger.info("  2. ")
        logger.info("  3.  .env API")

    except Exception as e:
        logger.error(f" : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
