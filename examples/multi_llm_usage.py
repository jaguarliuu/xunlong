"""多种大模型使用示例"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.deep_search_agent import DeepSearchAgent
from src.llm import LLMConfig, LLMProvider, create_llm_config


async def test_different_providers():
    """测试不同的LLM提供商"""
    print("=== 多种大模型提供商测试 ===\n")
    
    # 测试配置
    test_configs = []
    
    # 通义千问
    if os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY"):
        test_configs.append({
            "name": "通义千问",
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
    
    # 智谱AI
    if os.getenv("ZHIPU_API_KEY"):
        test_configs.append({
            "name": "智谱AI",
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
    
    # Ollama (本地)
    test_configs.append({
        "name": "Ollama本地",
        "provider": LLMProvider.OLLAMA,
        "model": "llama3",
        "api_key": None
    })
    
    if not test_configs:
        print("❌ 未找到任何可用的LLM配置")
        print("请设置相应的环境变量:")
        print("  export DASHSCOPE_API_KEY='your-qwen-key'")
        print("  export DEEPSEEK_API_KEY='your-deepseek-key'")
        print("  export ZHIPU_API_KEY='your-zhipu-key'")
        print("  export OPENAI_API_KEY='your-openai-key'")
        return
    
    # 测试问题
    test_question = "什么是人工智能？请用一句话回答。"
    
    for config in test_configs:
        print(f"--- 测试 {config['name']} ---")
        
        try:
            # 创建自定义配置
            llm_config = create_llm_config(
                provider=config['provider'],
                model_name=config['model'],
                api_key=config['api_key'],
                temperature=0.7,
                max_tokens=100
            )
            
            # 创建智能体（使用自定义配置）
            from src.llm.manager import LLMManager
            manager = LLMManager()
            manager.add_config("test", llm_config)
            
            client = manager.get_client("test")
            
            # 测试连接
            print(f"🔍 测试连接...")
            answer = await client.simple_chat(test_question)
            
            print(f"✅ {config['name']} 响应:")
            print(f"   {answer}")
            print(f"   模型: {config['model']}")
            
        except Exception as e:
            print(f"❌ {config['name']} 测试失败: {e}")
        
        print()


async def compare_model_responses():
    """比较不同模型的响应"""
    print("=== 模型响应比较 ===\n")
    
    # 创建默认智能体
    agent = DeepSearchAgent()
    
    # 获取可用提供商
    status = agent.get_system_status()
    available_providers = status['llm_manager']['available_providers']
    
    # 筛选可用的提供商
    usable_providers = [
        name for name, info in available_providers.items() 
        if info['status'] == "可用"
    ]
    
    if not usable_providers:
        print("❌ 没有可用的LLM提供商")
        return
    
    print(f"📊 比较 {len(usable_providers)} 个可用提供商的响应")
    print(f"可用提供商: {', '.join(usable_providers)}\n")
    
    # 测试问题
    questions = [
        "用一句话解释什么是机器学习",
        "Python和Java的主要区别是什么？",
        "如何提高工作效率？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"--- 问题 {i}: {question} ---")
        
        for provider in usable_providers[:3]:  # 限制测试数量
            try:
                # 更新配置使用特定提供商
                manager = agent.llm_manager
                config = manager.get_config("default")
                
                # 创建临时配置
                temp_config = create_llm_config(
                    provider=LLMProvider(provider),
                    model_name=available_providers[provider]['default_model'],
                    temperature=0.7,
                    max_tokens=150
                )
                
                manager.add_config(f"temp_{provider}", temp_config)
                client = manager.get_client(f"temp_{provider}")
                
                answer = await client.simple_chat(question)
                
                print(f"🤖 {provider}:")
                print(f"   {answer[:100]}{'...' if len(answer) > 100 else ''}")
                
            except Exception as e:
                print(f"❌ {provider} 失败: {e}")
        
        print()


async def test_agent_with_different_models():
    """测试智能体使用不同模型"""
    print("=== 智能体多模型测试 ===\n")
    
    # 测试不同的智能体配置
    test_queries = [
        "人工智能的发展历史",
        "区块链技术的应用场景"
    ]
    
    for query in test_queries:
        print(f"🔍 查询: {query}")
        
        try:
            # 使用默认配置
            agent = DeepSearchAgent()
            
            # 快速回答测试
            answer = await agent.quick_answer(query)
            print(f"✅ 快速回答: {answer[:100]}...")
            
            # 如果有多个可用提供商，可以测试深度搜索
            status = agent.get_system_status()
            available_count = sum(
                1 for info in status['llm_manager']['available_providers'].values()
                if info['status'] == "可用"
            )
            
            if available_count > 0:
                print("🔍 执行深度搜索...")
                result = await agent.search(query, config={"timeout_seconds": 60})
                print(f"✅ 搜索状态: {result['status']}")
                
                if result.get('final_report'):
                    report = result['final_report']['report_content']
                    print(f"📄 报告预览: {report[:150]}...")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print("-" * 50)


async def main():
    """主函数"""
    print("DeepSearch多种大模型支持演示\n")
    
    try:
        # 测试不同提供商
        await test_different_providers()
        
        print("\n" + "="*60 + "\n")
        
        # 比较模型响应
        await compare_model_responses()
        
        print("\n" + "="*60 + "\n")
        
        # 测试智能体
        await test_agent_with_different_models()
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"\n执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())