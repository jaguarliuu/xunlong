"""DeepSearch智能体系统主入口"""

import asyncio
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from src.deep_search_agent import DeepSearchAgent


async def main():
    """主演示函数"""
    print("=== DeepSearch智能体系统演示 ===\n")
    
    try:
        # 创建智能体
        agent = DeepSearchAgent()
        print("✓ DeepSearch智能体系统初始化完成\n")
        
        # 演示查询
        query = "人工智能在医疗领域的应用"
        print(f"查询: {query}\n")
        
        # 执行深度搜索
        print("正在执行深度搜索...")
        result = await agent.search(query)
        
        print(f"搜索状态: {result['status']}")
        
        # 显示执行步骤
        if result.get('messages'):
            print("执行步骤: ")
            for msg in result['messages']:
                if msg.get('agent'):
                    print(f"  ✓ {msg.get('agent', 'Unknown')}: {msg.get('content', '')[:50]}...")
        
        # 显示最终报告
        if result.get('final_report') and result['final_report'].get('result'):
            final_result = result['final_report']['result']
            if final_result.get('report_content'):
                report = final_result['report_content']
                print(f"\n=== 综合报告 ===")
                print(f"{report[:500]}...")
                
                # 保存报告
                output_file = f"results/demo_report_{query[:10].replace(' ', '_')}.txt"
                Path("results").mkdir(exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"查询: {query}\n")
                    f.write(f"状态: {result['status']}\n")
                    f.write(f"时间: {asyncio.get_event_loop().time()}\n\n")
                    f.write("=== 完整报告 ===\n")
                    f.write(report)
                    
                    if result.get('search_results'):
                        f.write(f"\n\n=== 搜索结果 ({len(result['search_results'])} 个) ===\n")
                        for i, search_result in enumerate(result['search_results'], 1):
                            f.write(f"\n{i}. {search_result.get('title', 'No Title')}\n")
                            f.write(f"   URL: {search_result.get('url', 'No URL')}\n")
                            if search_result.get('content'):
                                f.write(f"   内容: {search_result['content'][:200]}...\n")
                
                print(f"✓ 报告已保存到: {output_file}")
            else:
                print("\n⚠️ 未生成完整报告，但搜索过程已完成")
        else:
            print("\n⚠️ 搜索完成但未生成最终报告")
        
        # 显示搜索结果统计
        if result.get('search_results'):
            print(f"\n✓ 找到 {len(result['search_results'])} 个搜索结果")
        
        # 显示错误信息（如果有）
        if result.get('errors'):
            print(f"\n⚠️ 执行过程中的警告:")
            for error in result['errors']:
                print(f"  - {error}")
        
        print("\n=== 快速问答演示 ===")
        
        # 快速问答演示
        quick_query = "什么是深度学习？"
        print(f"问题: {quick_query}")
        
        answer = await agent.quick_answer(quick_query)
        print(f"回答: {answer}\n")
        
        # 系统状态
        print("=== 系统状态 ===")
        status = agent.get_system_status()
        
        print(f"系统: {status.get('system', 'Unknown')}")
        print(f"状态: {status.get('status', 'Unknown')}")
        
        if status.get('llm_manager'):
            llm_info = status['llm_manager']
            print(f"LLM配置: {llm_info.get('total_configs', 0)} 个")
            
            available_providers = llm_info.get('available_providers', {})
            available_count = sum(1 for info in available_providers.values() if info.get('status') == '可用')
            print(f"可用提供商: {available_count} 个")
        
        print("\n✓ 演示完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


def show_usage():
    """显示使用说明"""
    print("DeepSearch智能体系统使用说明:")
    print("  python main_agent.py                    # 运行完整演示")
    print("  python -m src.cli_agent search '查询'   # CLI搜索")
    print("  python -m src.cli_agent quick '问题'    # 快速问答")
    print("  python -m src.cli_agent status          # 查看状态")
    print("  python -m src.api_agent                 # 启动API服务")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_usage()
    else:
        asyncio.run(main())