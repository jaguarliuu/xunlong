"""DeepSearch"""

import asyncio
import sys
import os
from pathlib import Path

# Python
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.deep_search_agent import DeepSearchAgent


async def basic_search_example():
    """TODO: Add docstring."""
    print("=== DeepSearch ===\n")
    
    # 
    agent = DeepSearchAgent()
    print(" DeepSearch\n")
    
    # 
    queries = [
        "",
        "Python",
        ""
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"---  {i}: {query} ---")
        
        try:
            # 
            result = await agent.search(query)
            
            print(f": {result['status']}")
            print(f": {', '.join(result.get('execution_steps', []))}")
            
            if result['status'] in ['success', 'partial_success']:
                # 
                if result.get('optimization_result'):
                    optimized_queries = result['optimization_result'].get('optimized_queries', [])
                    print(f": {len(optimized_queries)}")
                
                # 
                if result.get('search_results'):
                    search_results = result['search_results']
                    print(f": {search_results.get('success_count', 0)} ")
                
                # 
                if result.get('final_report'):
                    report = result['final_report']['report_content']
                    print(f": {len(report)} ")
                    print(f":\n{report[:300]}...\n")
                
            else:
                print(f": {result.get('error', '')}\n")
                
        except Exception as e:
            print(f": {e}\n")
        
        print("-" * 50 + "\n")


async def quick_answer_example():
    """TODO: Add docstring."""
    print("===  ===\n")
    
    agent = DeepSearchAgent()
    
    questions = [
        "",
        "Python",
        ""
    ]
    
    for question in questions:
        print(f": {question}")
        
        try:
            answer = await agent.quick_answer(question)
            print(f": {answer}\n")
            
        except Exception as e:
            print(f": {e}\n")


async def system_status_example():
    """TODO: Add docstring."""
    print("===  ===\n")
    
    agent = DeepSearchAgent()
    
    # 
    status = agent.get_system_status()
    
    print("LLM:")
    llm_status = status['llm_manager']
    print(f"  : {llm_status['config_path']}")
    print(f"  : {llm_status['total_configs']}")
    print(f"  : {llm_status['active_clients']}")
    print(f"  : {', '.join(llm_status['available_configs'])}")
    
    print(f"\n:")
    prompt_info = llm_status['prompt_manager_info']
    print(f"  : {prompt_info['prompts_count']}")
    print(f"  : {prompt_info['prompts_dir']}")
    
    print(f"\n:")
    agents_status = status['agents_status']
    for agent_name, agent_info in agents_status.items():
        print(f"  {agent_name}: {agent_info['status']} ({agent_info['llm_model']['model_name']})")
    
    print(f"\n:")
    coord_config = status['coordinator_config']
    print(f"  : {coord_config['max_search_results']}")
    print(f"  : {coord_config['enable_parallel_analysis']}")
    print(f"  : {coord_config['timeout_seconds']}")


async def custom_config_example():
    """TODO: Add docstring."""
    print("===  ===\n")
    
    agent = DeepSearchAgent()
    
    # 
    custom_config = {
        "max_search_results": 3,
        "synthesis_config": {
            "report_type": "",
            "target_audience": "",
            "detail_level": ""
        },
        "timeout_seconds": 120
    }
    
    query = "Docker"
    print(f": {query}")
    
    try:
        result = await agent.search(query, config=custom_config)
        
        print(f": {result['status']}")
        
        if result['status'] in ['success', 'partial_success']:
            if result.get('final_report'):
                metadata = result['final_report']['metadata']
                print(f": {metadata['report_type']}")
                print(f": {metadata['target_audience']}")
                print(f": {metadata['detail_level']}")
                
                report = result['final_report']['report_content']
                print(f"\n:\n{report}")
        
    except Exception as e:
        print(f": {e}")


async def main():
    """TODO: Add docstring."""
    print("DeepSearch\n")
    
    # API
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  : API (LLM_API_KEY  OPENAI_API_KEY)")
        print("   \n")
    
    try:
        # 
        await system_status_example()
        print("\n" + "="*60 + "\n")
        
        await quick_answer_example()
        print("\n" + "="*60 + "\n")
        
        await basic_search_example()
        print("\n" + "="*60 + "\n")
        
        await custom_config_example()
        
    except KeyboardInterrupt:
        print("\n")
    except Exception as e:
        print(f"\n: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())