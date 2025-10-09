"""DeepSearch"""

import asyncio
import sys
import os
from pathlib import Path

# srcPython
sys.path.append(str(Path(__file__).parent / "src"))

from src.deep_search_agent import DeepSearchAgent


async def main():
    """TODO: Add docstring."""
    print("=== DeepSearch ===\n")

    try:
        # 
        agent = DeepSearchAgent()
        print(" DeepSearch\n")

        # 
        print(f"[DEBUG] : {len(sys.argv)}")
        print(f"[DEBUG] : {sys.argv}")

        # 
        if len(sys.argv) > 1:
            if sys.argv[1] == "search":
                if len(sys.argv) > 2:
                    # 
                    if len(sys.argv) > 3:
                        # 
                        query = ' '.join(sys.argv[2:])
                        print(f"[DEBUG] : {query}")
                    else:
                        # 
                        query = sys.argv[2]
                        print(f"[DEBUG] ")
                else:
                    # search
                    print(f"[DEBUG] search")
                    print(f"[DEBUG]  python main_agent.py search ''")
                    print(f"[DEBUG]  run_fiction_test.py ")
                    query = ""
                    print(f"[DEBUG] ")
            else:
                # search
                query = ""
                print(f"[DEBUG] ")
        else:
            # 
            query = ""
            print(f"[DEBUG] ")

        print(f"\n: {query}\n")
        
        # 
        print("...")
        result = await agent.search(query)
        
        print(f": {result['status']}")

        # 
        if result.get('project_id'):
            print(f"ID: {result['project_id']}")
        if result.get('project_dir'):
            print(f": {result['project_dir']}")

        # 
        if result.get('messages'):
            print("\n: ")
            for msg in result['messages']:
                if msg.get('agent'):
                    print(f"   {msg.get('agent', 'Unknown')}: {msg.get('content', '')[:50]}...")
        
        # 
        if result.get('final_report') and result['final_report'].get('result'):
            final_result = result['final_report']['result']
            if final_result.get('report'):
                report_data = final_result['report']
                report_content = report_data.get('content', '')
                print(f"\n===  ===")
                print(f"{report_content[:500]}...")
                print(f"\n ")
            else:
                print("\n ")
        else:
            print("\n ")
        
        # 
        if result.get('search_results'):
            print(f"\n  {len(result['search_results'])} ")
        
        # 
        if result.get('errors'):
            print(f"\n :")
            for error in result['errors']:
                print(f"  - {error}")

        # 
        print("===  ===")
        status = agent.get_status()
        
        print(f": {status.get('system', 'Unknown')}")
        print(f": {status.get('status', 'Unknown')}")
        
        if status.get('llm_manager'):
            llm_info = status['llm_manager']
            print(f"LLM: {llm_info.get('total_configs', 0)} ")
            
            available_providers = llm_info.get('available_providers', {})
            available_count = sum(1 for info in available_providers.values() if info.get('status') == '')
            print(f": {available_count} ")
        
        print("\n ")
        
    except KeyboardInterrupt:
        print("\n ")
    except Exception as e:
        print(f"\n : {e}")
        import traceback
        traceback.print_exc()


def show_usage():
    """TODO: Add docstring."""
    print("DeepSearch:")
    print("  python main_agent.py                    # ")
    print("  python main_agent.py search ''      # ")
    print("  python -m src.cli_agent search ''   # CLI")
    print("  python -m src.cli_agent quick ''    # ")
    print("  python -m src.cli_agent status          # ")
    print("  python -m src.api_agent                 # API")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_usage()
    else:
        asyncio.run(main())