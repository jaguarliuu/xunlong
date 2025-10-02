#!/usr/bin/env python
"""直接运行小说创作测试，避免shell参数解析问题"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from src.deep_search_agent import DeepSearchAgent


async def main():
    """小说创作测试"""

    # 直接在代码中定义查询，避免shell参数问题
    query = '搜集资料写一篇密室杀人类型的本格短篇推理小说;要求小说从凶手视角展开,但是直到最后才揭晓"我是凶手"'

    print("=== 小说创作测试 ===\n")
    print(f"查询: {query}\n")

    # 创建智能体
    agent = DeepSearchAgent()
    print("✓ DeepSearch智能体系统初始化完成\n")

    # 执行搜索
    print("正在执行小说创作...")
    result = await agent.search(query)

    print(f"\n搜索状态: {result['status']}")

    # 显示项目信息
    if result.get('project_id'):
        print(f"项目ID: {result['project_id']}")
    if result.get('project_dir'):
        print(f"项目目录: {result['project_dir']}")

    # 显示执行步骤
    if result.get('messages'):
        print("\n执行步骤:")
        for msg in result['messages']:
            if msg.get('agent'):
                content = msg.get('content', '')
                print(f"  ✓ {msg.get('agent')}: {content[:80]}...")

    # 显示最终报告预览
    if result.get('final_report') and result['final_report'].get('result'):
        final_result = result['final_report']['result']
        if final_result.get('report'):
            report_data = final_result['report']
            report_content = report_data.get('content', '')
            print(f"\n=== 小说预览 ===")
            print(f"{report_content[:800]}...")
            print(f"\n✓ 完整小说已保存到: {result['project_dir']}/reports/FINAL_REPORT.md")

            # 显示元数据
            metadata = report_data.get('metadata', {})
            print(f"\n=== 小说信息 ===")
            print(f"类型: {metadata.get('type', 'unknown')}")
            print(f"类别: {metadata.get('genre', 'unknown')}")
            print(f"总章节数: {metadata.get('total_chapters', 0)}")
            print(f"成功写作: {metadata.get('successful_chapters', 0)} 章")
            print(f"总字数: {report_data.get('word_count', 0)}")

    print("\n✓ 测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
