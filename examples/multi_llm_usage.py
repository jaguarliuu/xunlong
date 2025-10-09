"""TODO: Add docstring."""

import asyncio
import sys
import os
from pathlib import Path

# Python
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.deep_search_agent import DeepSearchAgent
from src.llm import LLMConfig, LLMProvider, create_llm_config


async def test_different_providers():
    """LLM"""
    print("===  ===\n")
    
    # 
    test_configs = []
    
    # 
    if os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY"):
        test_configs.append({
            "name": "",
            "provider": LLMProvider.QWEN,
            "model": "qwen-turbo",
            "api_key": os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
        })
    
    # DeepSeek
    if os.getenv("DEEPSEEK_API_KEY"):
        test_configs.append({
            "name": "DeepSeek",
            "provider": LLMProvider.DEEPSEEK,
            "model": "deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY")
        })
    
    # AI
    if os.getenv("ZHIPU_API_KEY"):
        test_configs.append({
            "name": "AI",
            "provider": LLMProvider.ZHIPU,
            "model": "glm-4",
            "api_key": os.getenv("ZHIPU_API_KEY")
        })
    
    # OpenAI
    if os.getenv("OPENAI_API_KEY"):
        test_configs.append({
            "name": "OpenAI",
            "provider": LLMProvider.OPENAI,
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY")
        })
    
    # Ollama ()
    test_configs.append({
        "name": "Ollama",
        "provider": LLMProvider.OLLAMA,
        "model": "llama3",
        "api_key": None
    })
    
    if not test_configs:
        print(" LLM")
        print(":")
        print("  export DASHSCOPE_API_KEY='your-qwen-key'")
        print("  export DEEPSEEK_API_KEY='your-deepseek-key'")
        print("  export ZHIPU_API_KEY='your-zhipu-key'")
        print("  export OPENAI_API_KEY='your-openai-key'")
        return
    
    # 
    test_question = ""
    
    for config in test_configs:
        print(f"---  {config['name']} ---")
        
        try:
            # 
            llm_config = create_llm_config(
                provider=config['provider'],
                model_name=config['model'],
                api_key=config['api_key'],
                temperature=0.7,
                max_tokens=100
            )
            
            # 
            from src.llm.manager import LLMManager
            manager = LLMManager()
            manager.add_config("test", llm_config)
            
            client = manager.get_client("test")
            
            # 
            print(f" ...")
            answer = await client.simple_chat(test_question)
            
            print(f" {config['name']} :")
            print(f"   {answer}")
            print(f"   : {config['model']}")
            
        except Exception as e:
            print(f" {config['name']} : {e}")
        
        print()


async def compare_model_responses():
    """TODO: Add docstring."""
    print("===  ===\n")
    
    # 
    agent = DeepSearchAgent()
    
    # 
    status = agent.get_system_status()
    available_providers = status['llm_manager']['available_providers']
    
    # 
    usable_providers = [
        name for name, info in available_providers.items() 
        if info['status'] == ""
    ]
    
    if not usable_providers:
        print(" LLM")
        return
    
    print(f"  {len(usable_providers)} ")
    print(f": {', '.join(usable_providers)}\n")
    
    # 
    questions = [
        "",
        "PythonJava",
        ""
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"---  {i}: {question} ---")
        
        for provider in usable_providers[:3]:  # 
            try:
                # 
                manager = agent.llm_manager
                config = manager.get_config("default")
                
                # 
                temp_config = create_llm_config(
                    provider=LLMProvider(provider),
                    model_name=available_providers[provider]['default_model'],
                    temperature=0.7,
                    max_tokens=150
                )
                
                manager.add_config(f"temp_{provider}", temp_config)
                client = manager.get_client(f"temp_{provider}")
                
                answer = await client.simple_chat(question)
                
                print(f" {provider}:")
                print(f"   {answer[:100]}{'...' if len(answer) > 100 else ''}")
                
            except Exception as e:
                print(f" {provider} : {e}")
        
        print()


async def test_agent_with_different_models():
    """TODO: Add docstring."""
    print("===  ===\n")
    
    # 
    test_queries = [
        "",
        ""
    ]
    
    for query in test_queries:
        print(f" : {query}")
        
        try:
            # 
            agent = DeepSearchAgent()
            
            # 
            answer = await agent.quick_answer(query)
            print(f" : {answer[:100]}...")
            
            # 
            status = agent.get_system_status()
            available_count = sum(
                1 for info in status['llm_manager']['available_providers'].values()
                if info['status'] == ""
            )
            
            if available_count > 0:
                print(" ...")
                result = await agent.search(query, config={"timeout_seconds": 60})
                print(f" : {result['status']}")
                
                if result.get('final_report'):
                    report = result['final_report']['report_content']
                    print(f" : {report[:150]}...")
            
        except Exception as e:
            print(f" : {e}")
        
        print("-" * 50)


async def main():
    """TODO: Add docstring."""
    print("DeepSearch\n")
    
    try:
        # 
        await test_different_providers()
        
        print("\n" + "="*60 + "\n")
        
        # 
        await compare_model_responses()
        
        print("\n" + "="*60 + "\n")
        
        # 
        await test_agent_with_different_models()
        
    except KeyboardInterrupt:
        print("\n")
    except Exception as e:
        print(f"\n: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())