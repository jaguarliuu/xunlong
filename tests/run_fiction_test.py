#!/usr/bin/env python
"""shell"""

import asyncio
import sys
from pathlib import Path

# srcPython
sys.path.append(str(Path(__file__).parent / "src"))

from src.deep_search_agent import DeepSearchAgent


async def main():
    """"""

    # shell
    query = ';,""'

    print("===  ===\n")
    print(f": {query}\n")

    # 
    agent = DeepSearchAgent()
    print(" DeepSearch\n")

    # 
    print("...")
    result = await agent.search(query)

    print(f"\n: {result['status']}")

    # 
    if result.get('project_id'):
        print(f"ID: {result['project_id']}")
    if result.get('project_dir'):
        print(f": {result['project_dir']}")

    # 
    if result.get('messages'):
        print("\n:")
        for msg in result['messages']:
            if msg.get('agent'):
                content = msg.get('content', '')
                print(f"   {msg.get('agent')}: {content[:80]}...")

    # 
    if result.get('final_report') and result['final_report'].get('result'):
        final_result = result['final_report']['result']
        if final_result.get('report'):
            report_data = final_result['report']
            report_content = report_data.get('content', '')
            print(f"\n===  ===")
            print(f"{report_content[:800]}...")
            print(f"\n : {result['project_dir']}/reports/FINAL_REPORT.md")

            # 
            metadata = report_data.get('metadata', {})
            print(f"\n===  ===")
            print(f": {metadata.get('type', 'unknown')}")
            print(f": {metadata.get('genre', 'unknown')}")
            print(f": {metadata.get('total_chapters', 0)}")
            print(f": {metadata.get('successful_chapters', 0)} ")
            print(f": {report_data.get('word_count', 0)}")

    print("\n ")


if __name__ == "__main__":
    asyncio.run(main())
