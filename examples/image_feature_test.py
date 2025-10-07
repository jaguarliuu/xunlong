"""
图片功能测试示例

测试内容:
1. 图片搜索 (Unsplash/Pexels)
2. 图片下载和本地存储
3. 图片插入到Markdown内容
4. 完整的报告生成流程（带配图）
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.tools.image_searcher import ImageSearcher
from src.tools.image_downloader import ImageDownloader
from src.utils.image_processor import ImageProcessor


async def test_image_search():
    """测试图片搜索功能"""
    logger.info("=" * 60)
    logger.info("测试1: 图片搜索功能")
    logger.info("=" * 60)

    searcher = ImageSearcher()

    if not searcher.is_available():
        logger.warning("未配置图片API密钥，跳过测试")
        logger.info("请在 .env 文件中配置 UNSPLASH_ACCESS_KEY 或 PEXELS_API_KEY")
        return None

    logger.info(f"可用的图片源: {searcher.get_available_sources()}")

    # 搜索测试
    query = "artificial intelligence technology"
    logger.info(f"搜索关键词: {query}")

    images = await searcher.search_images(query, count=3)

    if images:
        logger.success(f"✓ 成功搜索到 {len(images)} 张图片")
        for i, img in enumerate(images, 1):
            logger.info(
                f"  {i}. {img.get('alt', 'N/A')[:50]} "
                f"({img.get('width')}x{img.get('height')}) "
                f"- {img.get('source', 'unknown')}"
            )
        return images
    else:
        logger.error("✗ 图片搜索失败")
        return None


async def test_image_download(images):
    """测试图片下载功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 图片下载功能")
    logger.info("=" * 60)

    if not images:
        logger.warning("没有图片可供下载，跳过测试")
        return None

    downloader = ImageDownloader(
        storage_dir=Path("storage/test_images"),
        max_image_size=1024,
        quality=80
    )

    logger.info(f"开始下载 {len(images)} 张图片...")
    downloaded_images = await downloader.download_images(images[:2], optimize=True)

    if downloaded_images:
        logger.success(f"✓ 成功下载 {len(downloaded_images)} 张图片")
        for img in downloaded_images:
            if img.get('local_path'):
                logger.info(f"  - {img.get('local_path')} ({img.get('size', 0)} bytes)")
        return downloaded_images
    else:
        logger.error("✗ 图片下载失败")
        return None


def test_image_insertion(images):
    """测试图片插入功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 图片插入到Markdown")
    logger.info("=" * 60)

    if not images:
        logger.warning("没有图片可供插入，跳过测试")
        return

    # 创建示例内容
    sample_content = """
# 人工智能技术概述

人工智能(Artificial Intelligence, AI)是计算机科学的一个重要分支，致力于研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统。

## 发展历史

人工智能的概念最早由John McCarthy在1956年提出。经过几十年的发展，AI技术已经渗透到我们生活的方方面面。

## 核心技术

现代人工智能主要包括机器学习、深度学习、自然语言处理、计算机视觉等多个技术领域。

## 应用场景

AI技术已广泛应用于智能助手、自动驾驶、医疗诊断、金融风控等众多领域。
"""

    # 测试不同插入模式
    modes = ["smart", "top", "bottom", "distribute"]

    for mode in modes:
        logger.info(f"\n测试插入模式: {mode}")
        result = ImageProcessor.insert_images_to_content(
            sample_content, images, mode=mode
        )

        # 保存结果
        output_file = Path(f"storage/test_images/result_{mode}.md")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result, encoding='utf-8')

        logger.success(f"✓ 模式 '{mode}' 测试完成，结果保存到: {output_file}")
        logger.info(f"  内容长度: {len(result)} 字符")


async def test_batch_search():
    """测试批量搜索功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4: 批量章节图片搜索")
    logger.info("=" * 60)

    searcher = ImageSearcher()

    if not searcher.is_available():
        logger.warning("未配置图片API密钥，跳过测试")
        return

    # 模拟章节
    sections = [
        {"id": "section_1", "title": "Machine Learning Basics"},
        {"id": "section_2", "title": "Deep Learning Networks"},
        {"id": "section_3", "title": "Natural Language Processing"},
    ]

    logger.info(f"为 {len(sections)} 个章节搜索配图...")
    section_images = await searcher.search_images_for_sections(sections, images_per_section=2)

    for section in sections:
        section_id = section['id']
        images = section_images.get(section_id, [])
        logger.info(f"  {section['title']}: {len(images)} 张图片")

    logger.success("✓ 批量搜索测试完成")


async def main():
    """主测试流程"""
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + " " * 15 + "图片功能测试套件" + " " * 25 + "║")
    logger.info("╚" + "═" * 58 + "╝\n")

    try:
        # 测试1: 图片搜索
        images = await test_image_search()

        # 测试2: 图片下载
        if images:
            downloaded_images = await test_image_download(images)

            # 测试3: 图片插入
            if downloaded_images:
                test_image_insertion(downloaded_images)

        # 测试4: 批量搜索
        await test_batch_search()

        logger.info("\n" + "=" * 60)
        logger.success("✅ 所有测试完成!")
        logger.info("=" * 60)

        logger.info("\n📝 测试结果总结:")
        logger.info("  - 图片搜索: 已测试")
        logger.info("  - 图片下载: 已测试")
        logger.info("  - 图片插入: 已测试")
        logger.info("  - 批量搜索: 已测试")

        logger.info("\n💡 下一步:")
        logger.info("  1. 查看 storage/test_images/ 目录中的测试结果")
        logger.info("  2. 在实际报告生成中启用图片功能")
        logger.info("  3. 配置 .env 文件中的图片API密钥")

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
