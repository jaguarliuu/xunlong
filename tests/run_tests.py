#!/usr/bin/env python3
"""
寻龙探索 - 测试运行器
运行所有测试用例的统一入口
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - 成功")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} - 失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            if result.stdout:
                print(f"输出信息: {result.stdout}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - 异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🐉 寻龙探索 - 测试套件")
    print("=" * 60)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, str(project_root))
    
    success_count = 0
    total_count = 0
    
    # 运行单元测试
    print("\n🔬 运行单元测试...")
    unit_tests = [
        ("python tests/unit/minimal_test.py", "最小化测试"),
        ("python tests/unit/simple_test.py", "简单功能测试"),
        ("python tests/unit/test_agents.py", "智能体单元测试"),
        ("python tests/unit/test_simple_search.py", "搜索功能单元测试"),
    ]
    
    for cmd, desc in unit_tests:
        total_count += 1
        if run_command(cmd, desc):
            success_count += 1
    
    # 运行集成测试
    print("\n🔗 运行集成测试...")
    integration_tests = [
        ("python tests/integration/basic_test.py", "基础集成测试"),
        ("python tests/integration/basic_test_fixed.py", "修复版基础测试"),
        ("python tests/integration/debug_search.py", "搜索调试测试"),
        ("python tests/integration/test_deepsearch.py", "深度搜索测试"),
        ("python tests/integration/test_fixed_search.py", "修复版搜索测试"),
        ("python tests/integration/test_headless_issue.py", "浏览器模式测试"),
        ("python tests/integration/test_system_integration.py", "系统集成测试"),
    ]
    
    for cmd, desc in integration_tests:
        total_count += 1
        if run_command(cmd, desc):
            success_count += 1
    
    # 显示测试结果汇总
    print(f"\n{'='*60}")
    print("📊 测试结果汇总")
    print(f"{'='*60}")
    print(f"总测试数: {total_count}")
    print(f"成功: {success_count}")
    print(f"失败: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())