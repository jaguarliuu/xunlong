"""DeepSearch深度搜索系统演示"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.deep_search_agent import DeepSearchAgent
from src.agents.coordinator import DeepSearchConfig


async def save_report(report_data: dict, query: str):
    """保存报告到文件"""
    try:
        # 创建结果目录
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        filename = f"deep_search_report_{safe_query}_{timestamp}.txt"
        filepath = results_dir / filename
        
        # 提取报告内容
        final_report = report_data.get("final_report", {})
        report = final_report.get("report", {})
        
        if not report:
            print("⚠️ 警告: 没有找到报告内容")
            return None
        
        # 格式化报告内容
        content = f"""# DeepSearch深度搜索报告

## 查询信息
- 查询: {query}
- 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
- 工作流ID: {report_data.get('workflow_id', 'unknown')}

## 执行统计
- 状态: {report_data.get('status', 'unknown')}
- 搜索结果数: {report_data.get('statistics', {}).get('total_search_results', 0)}
- 子任务数: {report_data.get('statistics', {}).get('subtasks_count', 0)}

## 执行步骤
{chr(10).join(f"- {step}" for step in report_data.get('execution_steps', []))}

## 详细报告

{report.get('content', '报告内容生成失败')}

## 信息来源
"""
        
        # 添加信息来源
        sources = report.get('sources', [])
        if sources:
            for i, source in enumerate(sources[:10], 1):
                content += f"\n{i}. {source.get('title', '无标题')} ({source.get('type', '未知类型')})\n   {source.get('url', '无链接')}"
        else:
            content += "\n暂无信息来源"
        
        # 添加错误信息（如果有）
        errors = report_data.get('errors', [])
        if errors:
            content += f"\n\n## 执行错误\n"
            for error in errors:
                content += f"- {error}\n"
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 报告已保存到: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return None


async def main():
    """主函数"""
    print("=== DeepSearch深度搜索系统演示 ===\n")
    
    try:
        # 初始化深度搜索配置
        config = DeepSearchConfig(
            search_depth="deep",  # 深度搜索
            max_search_results=15,  # 最多15个结果
            timeout_seconds=600  # 10分钟超时
        )
        
        # 初始化DeepSearch智能体系统
        agent = DeepSearchAgent(config=config)
        
        # 获取系统状态
        status = agent.get_status()
        print("✓ DeepSearch智能体系统初始化完成")
        print(f"  - LLM配置: {status['llm_manager']['available_configs']} 个")
        print(f"  - 提供商: {status['llm_manager']['available_providers']} 个")
        print(f"  - 智能体: {len(status['coordinator']['agents'])} 个")
        print(f"  - 工作流: {status['coordinator']['workflow_type']}")
        print()
        
        # 测试查询列表
        test_queries = [
            "获取2024年9月24日AIGC领域发生的大事件，输出AI日报",
            "分析当前电动汽车市场竞争格局和发展趋势",
            "人工智能在医疗领域的最新应用和突破"
        ]
        
        # 让用户选择查询或输入自定义查询
        print("请选择测试查询或输入自定义查询:")
        for i, query in enumerate(test_queries, 1):
            print(f"{i}. {query}")
        print("4. 输入自定义查询")
        
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "4":
                query = input("请输入您的查询: ").strip()
                if not query:
                    print("❌ 查询不能为空")
                    return
            elif choice in ["1", "2", "3"]:
                query = test_queries[int(choice) - 1]
            else:
                print("❌ 无效选择，使用默认查询")
                query = test_queries[0]
                
        except (ValueError, KeyboardInterrupt):
            print("❌ 输入无效，使用默认查询")
            query = test_queries[0]
        
        print(f"\n查询: {query}")
        print("\n正在执行深度搜索...")
        
        # 分析查询复杂度
        complexity_analysis = await agent.analyze_query_complexity(query)
        if complexity_analysis.get("status") == "success":
            print(f"📊 查询分析:")
            print(f"  - 复杂度: {complexity_analysis.get('complexity', 'unknown')}")
            print(f"  - 意图: {complexity_analysis.get('intent', 'unknown')}")
            print(f"  - 时效性: {'是' if complexity_analysis.get('time_sensitive') else '否'}")
            print(f"  - 领域: {complexity_analysis.get('domain', 'unknown')}")
            print()
        
        # 执行深度搜索
        result = await agent.search(query)
        
        # 显示结果
        print(f"\n搜索状态: {result.get('status')}")
        print("执行步骤:")
        for step in result.get('execution_steps', []):
            print(f"  {step}")
        
        # 显示统计信息
        stats = result.get('statistics', {})
        if stats:
            print(f"\n📊 执行统计:")
            print(f"  - 搜索结果: {stats.get('total_search_results', 0)} 个")
            print(f"  - 子任务: {stats.get('subtasks_count', 0)} 个")
            print(f"  - 错误: {stats.get('errors_count', 0)} 个")
        
        # 保存报告
        if result.get('status') in ['success', 'partial_success']:
            filepath = await save_report(result, query)
            
            # 显示报告摘要
            final_report = result.get('final_report', {})
            report = final_report.get('report', {})
            
            if report:
                print(f"\n📋 报告摘要:")
                print(f"  - 类型: {report.get('type', 'unknown')}")
                print(f"  - 字数: {len(report.get('content', ''))} 字")
                print(f"  - 来源: {len(report.get('sources', []))} 个")
                
                # 显示报告开头
                content = report.get('content', '')
                if content:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"\n📄 报告预览:\n{preview}")
            
        else:
            print(f"\n❌ 搜索失败")
            errors = result.get('errors', [])
            if errors:
                print("错误信息:")
                for error in errors:
                    print(f"  - {error}")
        
        print(f"\n✅ 深度搜索演示完成")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())