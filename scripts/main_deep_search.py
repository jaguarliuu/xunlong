"""DeepSearch"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.deep_search_agent import DeepSearchAgent
from src.agents.coordinator import DeepSearchConfig


async def save_report(report_data: dict, query: str):
    """TODO: Add docstring."""
    try:
        # 
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        # 
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        filename = f"deep_search_report_{safe_query}_{timestamp}.txt"
        filepath = results_dir / filename
        
        # 
        final_report = report_data.get("final_report", {})
        report = final_report.get("report", {})
        
        if not report:
            print(" : ")
            return None
        
        # 
        content = f"""# DeepSearch

## 
- : {query}
- : {datetime.now().strftime('%Y%m%d %H:%M:%S')}
- ID: {report_data.get('workflow_id', 'unknown')}

## 
- : {report_data.get('status', 'unknown')}
- : {report_data.get('statistics', {}).get('total_search_results', 0)}
- : {report_data.get('statistics', {}).get('subtasks_count', 0)}

## 
{chr(10).join(f"- {step}" for step in report_data.get('execution_steps', []))}

## 

{report.get('content', '')}

## 
"""
        
        # 
        sources = report.get('sources', [])
        if sources:
            for i, source in enumerate(sources[:10], 1):
                content += f"\n{i}. {source.get('title', '')} ({source.get('type', '')})\n   {source.get('url', '')}"
        else:
            content += "\n"
        
        # 
        errors = report_data.get('errors', [])
        if errors:
            content += f"\n\n## \n"
            for error in errors:
                content += f"- {error}\n"
        
        # 
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f" : {filepath}")
        return filepath
        
    except Exception as e:
        print(f" : {e}")
        return None


async def main():
    """TODO: Add docstring."""
    print("=== DeepSearch ===\n")
    
    try:
        # 
        config = DeepSearchConfig(
            search_depth="deep",  # 
            max_search_results=15,  # 15
            timeout_seconds=600  # 10
        )
        
        # DeepSearch
        agent = DeepSearchAgent(config=config)
        
        # 
        status = agent.get_status()
        print(" DeepSearch")
        print(f"  - LLM: {status['llm_manager']['available_configs']} ")
        print(f"  - : {status['llm_manager']['available_providers']} ")
        print(f"  - : {len(status['coordinator']['agents'])} ")
        print(f"  - : {status['coordinator']['workflow_type']}")
        print()
        
        # 
        test_queries = [
            "2025924AIGCAI",
            "",
            ""
        ]
        
        # 
        print(":")
        for i, query in enumerate(test_queries, 1):
            print(f"{i}. {query}")
        print("4. ")
        
        try:
            choice = input("\n (1-4): ").strip()
            
            if choice == "4":
                query = input(": ").strip()
                if not query:
                    print(" ")
                    return
            elif choice in ["1", "2", "3"]:
                query = test_queries[int(choice) - 1]
            else:
                print(" ")
                query = test_queries[0]
                
        except (ValueError, KeyboardInterrupt):
            print(" ")
            query = test_queries[0]
        
        print(f"\n: {query}")
        print("\n...")
        
        # 
        complexity_analysis = await agent.analyze_query_complexity(query)
        if complexity_analysis.get("status") == "success":
            print(f" :")
            print(f"  - : {complexity_analysis.get('complexity', 'unknown')}")
            print(f"  - : {complexity_analysis.get('intent', 'unknown')}")
            print(f"  - : {'' if complexity_analysis.get('time_sensitive') else ''}")
            print(f"  - : {complexity_analysis.get('domain', 'unknown')}")
            print()
        
        # 
        result = await agent.search(query)
        
        # 
        print(f"\n: {result.get('status')}")
        print(":")
        for step in result.get('execution_steps', []):
            print(f"  {step}")
        
        # 
        stats = result.get('statistics', {})
        if stats:
            print(f"\n :")
            print(f"  - : {stats.get('total_search_results', 0)} ")
            print(f"  - : {stats.get('subtasks_count', 0)} ")
            print(f"  - : {stats.get('errors_count', 0)} ")
        
        # 
        if result.get('status') in ['success', 'partial_success']:
            filepath = await save_report(result, query)
            
            # 
            final_report = result.get('final_report', {})
            report = final_report.get('report', {})
            
            if report:
                print(f"\n :")
                print(f"  - : {report.get('type', 'unknown')}")
                print(f"  - : {len(report.get('content', ''))} ")
                print(f"  - : {len(report.get('sources', []))} ")
                
                # 
                content = report.get('content', '')
                if content:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"\n :\n{preview}")
            
        else:
            print(f"\n ")
            errors = result.get('errors', [])
            if errors:
                print(":")
                for error in errors:
                    print(f"  - {error}")
        
        print(f"\n ")
        
    except KeyboardInterrupt:
        print("\n\n ")
    except Exception as e:
        print(f"\n : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())