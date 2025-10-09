#!/usr/bin/env python
"""XunLong API"""

import sys
import time
from pathlib import Path

# 
sys.path.append(str(Path(__file__).parent.parent))

from examples.async_api_client import XunLongAsyncClient


def test_health_check():
    """TODO: Add docstring."""
    print("\n1  ...")
    client = XunLongAsyncClient()

    try:
        import requests
        response = requests.get(f"{client.base_url}/health", timeout=5)
        response.raise_for_status()
        result = response.json()

        print(f"    API")
        print(f"   : {result['status']}")
        print(f"   : {result['version']}")
        return True
    except Exception as e:
        print(f"    API: {e}")
        print("\n   API:")
        print("   python run_api.py")
        print("   ")
        print("   ./scripts/start_all.sh")
        return False


def test_task_creation():
    """TODO: Add docstring."""
    print("\n2  ...")
    client = XunLongAsyncClient()

    try:
        # 
        task = client.create_report(
            query="",
            search_depth="surface",
            max_results=5
        )

        print(f"    ")
        print(f"   ID: {task['task_id']}")
        print(f"   : {task['status']}")

        return task['task_id']
    except Exception as e:
        print(f"    : {e}")
        return None


def test_task_status(task_id):
    """TODO: Add docstring."""
    print("\n3  ...")
    client = XunLongAsyncClient()

    try:
        status = client.get_task_status(task_id)

        print(f"    ")
        print(f"   : {status['task_type']}")
        print(f"   : {status['status']}")
        print(f"   : {status['progress']}%")
        print(f"   : {status['current_step']}")

        return True
    except Exception as e:
        print(f"    : {e}")
        return False


def test_task_list():
    """TODO: Add docstring."""
    print("\n4  ...")
    client = XunLongAsyncClient()

    try:
        tasks = client.list_tasks(limit=5)

        print(f"    ")
        print(f"   : {tasks['total']}")

        if tasks['tasks']:
            print(f"\n   :")
            for i, task in enumerate(tasks['tasks'][:3], 1):
                print(f"   {i}. {task['task_id'][:8]}... - {task['status']} ({task['progress']}%)")

        return True
    except Exception as e:
        print(f"    : {e}")
        return False


def main():
    """TODO: Add docstring."""
    print("=" * 60)
    print("  XunLong API ")
    print("=" * 60)

    # 1: 
    if not test_health_check():
        sys.exit(1)

    time.sleep(1)

    # 2: 
    task_id = test_task_creation()
    if not task_id:
        print("\n  : ")
    else:
        time.sleep(1)

        # 3: 
        test_task_status(task_id)
        time.sleep(1)

    # 4: 
    test_task_list()

    print("\n" + "=" * 60)
    print("   ")
    print("=" * 60)
    print("\n :")
    print("   - API")
    print("   - worker: python start_worker.py")
    print("   - : python examples/async_api_client.py")
    print()


if __name__ == "__main__":
    main()
