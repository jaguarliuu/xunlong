"""DeepSearch智能体系统基础使用示例"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.deep_search_agent import DeepSearchAgent


async def basic_search_example():
    """基础搜索示例"""
    print("=== DeepSearch智能体系统基础使用示例 ===\n")
    
    # 创建智能体实例
    agent = DeepSearchAgent()
    print("✓ DeepSearch智能体系统初始化完成\n")
    
    # 示例查询
    queries = [
        "人工智能的发展历史",
        "Python编程语言的优势",
        "区块链技术的应用场景"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"--- 示例 {i}: {query} ---")
        
        try:
            # 执行深度搜索
            result = await agent.search(query)
            
            print(f"搜索状态: {result['status']}")
            print(f"执行步骤: {', '.join(result.get('execution_steps', []))}")
            
            if result['status'] in ['success', 'partial_success']:
                # 显示优化查询
                if result.get('optimization_result'):
                    optimized_queries = result['optimization_result'].get('optimized_queries', [])
                    print(f"优化查询数量: {len(optimized_queries)}")
                
                # 显示搜索结果
                if result.get('search_results'):
                    search_results = result['search_results']
                    print(f"搜索结果: {search_results.get('success_count', 0)} 个成功")
                
                # 显示最终报告
                if result.get('final_report'):
                    report = result['final_report']['report_content']
                    print(f"报告长度: {len(report)} 字符")
                    print(f"报告预览:\n{report[:300]}...\n")
                
            else:
                print(f"搜索失败: {result.get('error', '未知错误')}\n")
                
        except Exception as e:
            print(f"执行失败: {e}\n")
        
        print("-" * 50 + "\n")


async def quick_answer_example():
    """快速回答示例"""
    print("=== 快速回答示例 ===\n")
    
    agent = DeepSearchAgent()
    
    questions = [
        "什么是机器学习？",
        "如何学习Python编程？",
        "云计算的主要优势是什么？"
    ]
    
    for question in questions:
        print(f"问题: {question}")
        
        try:
            answer = await agent.quick_answer(question)
            print(f"回答: {answer}\n")
            
        except Exception as e:
            print(f"回答失败: {e}\n")


async def system_status_example():
    """系统状态示例"""
    print("=== 系统状态示例 ===\n")
    
    agent = DeepSearchAgent()
    
    # 获取系统状态
    status = agent.get_system_status()
    
    print("LLM管理器状态:")
    llm_status = status['llm_manager']
    print(f"  配置文件路径: {llm_status['config_path']}")
    print(f"  总配置数量: {llm_status['total_configs']}")
    print(f"  活跃客户端: {llm_status['active_clients']}")
    print(f"  可用配置: {', '.join(llm_status['available_configs'])}")
    
    print(f"\n提示词管理器状态:")
    prompt_info = llm_status['prompt_manager_info']
    print(f"  提示词数量: {prompt_info['prompts_count']}")
    print(f"  提示词目录: {prompt_info['prompts_dir']}")
    
    print(f"\n智能体状态:")
    agents_status = status['agents_status']
    for agent_name, agent_info in agents_status.items():
        print(f"  {agent_name}: {agent_info['status']} ({agent_info['llm_model']['model_name']})")
    
    print(f"\n协调器配置:")
    coord_config = status['coordinator_config']
    print(f"  最大搜索结果: {coord_config['max_search_results']}")
    print(f"  并行分析: {coord_config['enable_parallel_analysis']}")
    print(f"  超时时间: {coord_config['timeout_seconds']}秒")


async def custom_config_example():
    """自定义配置示例"""
    print("=== 自定义配置示例 ===\n")
    
    agent = DeepSearchAgent()
    
    # 自定义搜索配置
    custom_config = {
        "max_search_results": 3,
        "synthesis_config": {
            "report_type": "简要报告",
            "target_audience": "技术人员",
            "detail_level": "简要"
        },
        "timeout_seconds": 120
    }
    
    query = "Docker容器技术介绍"
    print(f"使用自定义配置搜索: {query}")
    
    try:
        result = await agent.search(query, config=custom_config)
        
        print(f"搜索状态: {result['status']}")
        
        if result['status'] in ['success', 'partial_success']:
            if result.get('final_report'):
                metadata = result['final_report']['metadata']
                print(f"报告类型: {metadata['report_type']}")
                print(f"目标受众: {metadata['target_audience']}")
                print(f"详细程度: {metadata['detail_level']}")
                
                report = result['final_report']['report_content']
                print(f"\n报告内容:\n{report}")
        
    except Exception as e:
        print(f"搜索失败: {e}")


async def main():
    """主函数"""
    print("DeepSearch智能体系统使用示例\n")
    
    # 检查API配置
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  警告: 未检测到API密钥环境变量 (LLM_API_KEY 或 OPENAI_API_KEY)")
        print("   某些功能可能无法正常工作\n")
    
    try:
        # 运行各种示例
        await system_status_example()
        print("\n" + "="*60 + "\n")
        
        await quick_answer_example()
        print("\n" + "="*60 + "\n")
        
        await basic_search_example()
        print("\n" + "="*60 + "\n")
        
        await custom_config_example()
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"\n执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())