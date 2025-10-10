"""
测试新的多页HTML PPT生成架构 (V3)
"""

import asyncio
from pathlib import Path
from src.agents.ppt.multi_slide_generator import MultiSlidePPTGenerator, create_slide_data
from src.llm.manager import LLMManager
from src.llm.prompts import PromptManager


async def test_multi_slide_ppt():
    """测试多页HTML PPT生成"""

    print("=" * 60)
    print("测试多页HTML PPT生成器 (V3架构)")
    print("=" * 60)

    # 创建生成器
    # 注意: 这个测试不调用LLM（因为slide内容已经准备好了）
    # 在实际使用中，llm_manager 会用于生成页面内容
    generator = MultiSlidePPTGenerator(llm_manager=None, prompt_manager=None)

    # 准备测试数据
    slides_data = [
        create_slide_data(
            slide_type='cover',
            title='多页HTML PPT测试',
            content={
                'title': '多页HTML PPT测试',
                'subtitle': '新架构演示',
                'author': 'XunLong AI',
                'date': '2025-10-10'
            }
        ),
        create_slide_data(
            slide_type='toc',
            title='目录',
            content={
                'sections': [
                    {'number': 1, 'title': '第一章节', 'subtitle': '章节介绍'},
                    {'number': 2, 'title': '第二章节', 'subtitle': '详细内容'},
                    {'number': 3, 'title': '第三章节', 'subtitle': '数据展示'},
                    {'number': 4, 'title': '第四章节', 'subtitle': '总结'}
                ]
            }
        ),
        create_slide_data(
            slide_type='content',
            title='第一章节 - 内容展示',
            content={
                'title': '第一章节',
                'layout': 'bullets',
                'points': [
                    '这是第一个要点',
                    '这是第二个要点',
                    '这是第三个要点',
                    '这是第四个要点'
                ],
                'details': '这里是详细说明文本...'
            }
        ),
        create_slide_data(
            slide_type='chart',
            title='数据图表展示',
            content={
                'title': '年度数据趋势',
                'chart_type': 'bar',
                'categories': ['2022', '2023', '2024', '2025'],
                'data': [100, 150, 200, 250],
                'series_name': '增长趋势',
                'y_axis_name': '数值',
                'data_source': '测试数据来源'
            }
        ),
        create_slide_data(
            slide_type='summary',
            title='总结',
            content={
                'title': '总结',
                'points': [
                    {'text': '完成了多页HTML架构设计', 'icon': 'check'},
                    {'text': '实现了模板系统', 'icon': 'check'},
                    {'text': '添加了导航功能', 'icon': 'check'},
                    {'text': '支持演示模式', 'icon': 'check'}
                ],
                'closing': '感谢观看！'
            }
        )
    ]

    ppt_config = {
        'ppt_title': '多页HTML PPT测试',
        'subtitle': '新架构演示',
        'colors': {
            'primary': '#2E8B57',
            'accent': '#FF8C00',
            'background': '#FFFFFF',
            'text': '#333333',
            'secondary': '#666666'
        },
        'style': 'business',
        'theme': 'default',
        'author': 'XunLong AI',
        'date': '2025-10-10'
    }

    # 输出目录
    output_dir = Path(__file__).parent / 'storage' / 'test_ppt_v3'

    print(f"\n输出目录: {output_dir}")
    print(f"幻灯片数量: {len(slides_data)}")
    print("\n开始生成PPT...\n")

    try:
        # 生成PPT
        result = await generator.generate_ppt(
            slides_data=slides_data,
            ppt_config=ppt_config,
            output_dir=output_dir
        )

        # 打印结果
        print("=" * 60)
        print("生成完成！")
        print("=" * 60)
        print(f"\n状态: {result['status']}")
        print(f"PPT目录: {result['ppt_dir']}")
        print(f"总页数: {result['total_slides']}")
        print(f"\n导航页: {result['index_page']}")
        print(f"演示模式页: {result['presenter_page']}")

        print(f"\n生成的幻灯片文件:")
        for slide_file in result['slide_files']:
            print(f"  - {slide_file}")

        print("\n" + "=" * 60)
        print("测试成功！请在浏览器中打开以下文件查看效果:")
        print(f"  {result['index_page']}")
        print("=" * 60 + "\n")

        return result

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(test_multi_slide_ppt())
