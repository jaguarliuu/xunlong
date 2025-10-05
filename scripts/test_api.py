#!/usr/bin/env python
"""测试XunLong API是否正常工作"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from examples.async_api_client import XunLongAsyncClient


def test_health_check():
    """测试健康检查"""
    print("\n1️⃣  测试健康检查...")
    client = XunLongAsyncClient()

    try:
        import requests
        response = requests.get(f"{client.base_url}/health", timeout=5)
        response.raise_for_status()
        result = response.json()

        print(f"   ✅ API服务正常")
        print(f"   状态: {result['status']}")
        print(f"   版本: {result['version']}")
        return True
    except Exception as e:
        print(f"   ❌ API服务不可用: {e}")
        print("\n   请先启动API服务:")
        print("   python run_api.py")
        print("   或")
        print("   ./scripts/start_all.sh")
        return False


def test_task_creation():
    """测试任务创建"""
    print("\n2️⃣  测试任务创建...")
    client = XunLongAsyncClient()

    try:
        # 创建一个简单的报告任务
        task = client.create_report(
            query="测试报告",
            search_depth="surface",
            max_results=5
        )

        print(f"   ✅ 任务创建成功")
        print(f"   任务ID: {task['task_id']}")
        print(f"   状态: {task['status']}")

        return task['task_id']
    except Exception as e:
        print(f"   ❌ 任务创建失败: {e}")
        return None


def test_task_status(task_id):
    """测试任务状态查询"""
    print("\n3️⃣  测试任务状态查询...")
    client = XunLongAsyncClient()

    try:
        status = client.get_task_status(task_id)

        print(f"   ✅ 状态查询成功")
        print(f"   任务类型: {status['task_type']}")
        print(f"   状态: {status['status']}")
        print(f"   进度: {status['progress']}%")
        print(f"   当前步骤: {status['current_step']}")

        return True
    except Exception as e:
        print(f"   ❌ 状态查询失败: {e}")
        return False


def test_task_list():
    """测试任务列表"""
    print("\n4️⃣  测试任务列表...")
    client = XunLongAsyncClient()

    try:
        tasks = client.list_tasks(limit=5)

        print(f"   ✅ 任务列表查询成功")
        print(f"   总任务数: {tasks['total']}")

        if tasks['tasks']:
            print(f"\n   最近的任务:")
            for i, task in enumerate(tasks['tasks'][:3], 1):
                print(f"   {i}. {task['task_id'][:8]}... - {task['status']} ({task['progress']}%)")

        return True
    except Exception as e:
        print(f"   ❌ 任务列表查询失败: {e}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("  XunLong API 测试脚本")
    print("=" * 60)

    # 测试1: 健康检查
    if not test_health_check():
        sys.exit(1)

    time.sleep(1)

    # 测试2: 创建任务
    task_id = test_task_creation()
    if not task_id:
        print("\n⚠️  警告: 任务创建失败，跳过后续测试")
    else:
        time.sleep(1)

        # 测试3: 查询状态
        test_task_status(task_id)
        time.sleep(1)

    # 测试4: 列出任务
    test_task_list()

    print("\n" + "=" * 60)
    print("  ✅ 测试完成")
    print("=" * 60)
    print("\n💡 提示:")
    print("   - API服务器运行正常")
    print("   - 如需执行任务，请启动worker: python start_worker.py")
    print("   - 查看完整示例: python examples/async_api_client.py")
    print()


if __name__ == "__main__":
    main()
