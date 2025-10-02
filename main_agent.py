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

        # 调试：显示命令行参数
        print(f"[DEBUG] 命令行参数数量: {len(sys.argv)}")
        print(f"[DEBUG] 所有参数: {sys.argv}")

        # 获取查询参数
        if len(sys.argv) > 1:
            if sys.argv[1] == "search":
                if len(sys.argv) > 2:
                    # 有查询参数
                    if len(sys.argv) > 3:
                        # 多个参数，合并（可能是引号问题）
                        query = ' '.join(sys.argv[2:])
                        print(f"[DEBUG] 检测到多个参数，已合并为: {query}")
                    else:
                        # 单个参数
                        query = sys.argv[2]
                        print(f"[DEBUG] 使用提供的查询")
                else:
                    # search命令但没有参数
                    print(f"[DEBUG] 检测到search命令但缺少查询参数")
                    print(f"[DEBUG] 提示：使用方式 python main_agent.py search '你的查询'")
                    print(f"[DEBUG] 如果查询包含特殊字符，建议使用 run_fiction_test.py 脚本")
                    query = "人工智能在医疗领域的应用"
                    print(f"[DEBUG] 使用默认查询代替")
            else:
                # 不是search命令
                query = "人工智能在医疗领域的应用"
                print(f"[DEBUG] 未识别的命令，使用默认查询")
        else:
            # 没有任何参数
            query = "人工智能在医疗领域的应用"
            print(f"[DEBUG] 无参数，使用默认查询")

        print(f"\n查询: {query}\n")
        
        # 执行深度搜索
        print("正在执行深度搜索...")
        result = await agent.search(query)
        
        print(f"搜索状态: {result['status']}")

        # 显示项目信息
        if result.get('project_id'):
            print(f"项目ID: {result['project_id']}")
        if result.get('project_dir'):
            print(f"项目目录: {result['project_dir']}")

        # 显示执行步骤
        if result.get('messages'):
            print("\n执行步骤: ")
            for msg in result['messages']:
                if msg.get('agent'):
                    print(f"  ✓ {msg.get('agent', 'Unknown')}: {msg.get('content', '')[:50]}...")
        
        # 显示最终报告预览
        if result.get('final_report') and result['final_report'].get('result'):
            final_result = result['final_report']['result']
            if final_result.get('report'):
                report_data = final_result['report']
                report_content = report_data.get('content', '')
                print(f"\n=== 报告预览 ===")
                print(f"{report_content[:500]}...")
                print(f"\n✓ 完整报告已保存到项目目录")
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

        # 系统状态
        print("=== 系统状态 ===")
        status = agent.get_status()
        
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
    print("  python main_agent.py search '查询'      # 搜索指定内容")
    print("  python -m src.cli_agent search '查询'   # CLI搜索")
    print("  python -m src.cli_agent quick '问题'    # 快速问答")
    print("  python -m src.cli_agent status          # 查看状态")
    print("  python -m src.api_agent                 # 启动API服务")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_usage()
    else:
        asyncio.run(main())