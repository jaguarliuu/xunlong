"""XunLong 异步API客户端示例"""

import requests
import time
import json
from typing import Dict, Any, Optional


class XunLongAsyncClient:
    """XunLong异步API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端

        Args:
            base_url: API服务地址
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def create_report(
        self,
        query: str,
        report_type: str = "comprehensive",
        search_depth: str = "deep",
        max_results: int = 20,
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        创建报告生成任务

        Args:
            query: 查询主题
            report_type: 报告类型
            search_depth: 搜索深度
            max_results: 最大搜索结果数
            output_format: 输出格式

        Returns:
            任务信息
        """
        url = f"{self.base_url}/api/v1/tasks/report"
        data = {
            "query": query,
            "report_type": report_type,
            "search_depth": search_depth,
            "max_results": max_results,
            "output_format": output_format
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def create_fiction(
        self,
        query: str,
        genre: str = "mystery",
        length: str = "short",
        viewpoint: str = "first",
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        创建小说创作任务

        Args:
            query: 小说主题
            genre: 体裁
            length: 篇幅
            viewpoint: 视角
            output_format: 输出格式

        Returns:
            任务信息
        """
        url = f"{self.base_url}/api/v1/tasks/fiction"
        data = {
            "query": query,
            "genre": genre,
            "length": length,
            "viewpoint": viewpoint,
            "output_format": output_format
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def create_ppt(
        self,
        query: str,
        slides: int = 15,
        style: str = "business",
        theme: str = "corporate-blue"
    ) -> Dict[str, Any]:
        """
        创建PPT生成任务

        Args:
            query: PPT主题
            slides: 幻灯片数量
            style: 风格
            theme: 主题

        Returns:
            任务信息
        """
        url = f"{self.base_url}/api/v1/tasks/ppt"
        data = {
            "query": query,
            "slides": slides,
            "style": style,
            "theme": theme
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务结果

        Args:
            task_id: 任务ID

        Returns:
            任务结果
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}/result"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def download_file(self, task_id: str, file_type: str = "html", save_path: str = None):
        """
        下载任务生成的文件

        Args:
            task_id: 任务ID
            file_type: 文件类型
            save_path: 保存路径

        Returns:
            保存的文件路径
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}/download"
        params = {"file_type": file_type}

        response = self.session.get(url, params=params, stream=True)
        response.raise_for_status()

        # 确定保存路径
        if not save_path:
            filename = response.headers.get('content-disposition', '').split('filename=')[-1].strip('"')
            if not filename:
                filename = f"{task_id}.{file_type}"
            save_path = filename

        # 保存文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return save_path

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            取消结果
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.json()

    def list_tasks(
        self,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        列出任务

        Args:
            status: 筛选状态
            task_type: 筛选类型
            limit: 最大数量

        Returns:
            任务列表
        """
        url = f"{self.base_url}/api/v1/tasks"
        params = {"limit": limit}
        if status:
            params["status"] = status
        if task_type:
            params["task_type"] = task_type

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 5,
        timeout: int = 3600,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        等待任务完成

        Args:
            task_id: 任务ID
            poll_interval: 轮询间隔(秒)
            timeout: 超时时间(秒)
            verbose: 是否显示进度

        Returns:
            任务结果
        """
        start_time = time.time()
        last_progress = -1

        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise TimeoutError(f"任务超时: {task_id}")

            # 获取状态
            status = self.get_task_status(task_id)

            # 显示进度
            if verbose and status['progress'] != last_progress:
                print(f"进度: {status['progress']}% - {status['current_step']}")
                last_progress = status['progress']

            # 检查状态
            if status['status'] == 'completed':
                if verbose:
                    print("✅ 任务完成!")
                return self.get_task_result(task_id)

            if status['status'] == 'failed':
                raise Exception(f"任务失败: {status.get('error', '未知错误')}")

            if status['status'] == 'cancelled':
                raise Exception("任务已被取消")

            # 等待下次轮询
            time.sleep(poll_interval)


def example_report_generation():
    """示例：生成报告"""
    print("\n" + "=" * 60)
    print("示例 1: 报告生成")
    print("=" * 60)

    client = XunLongAsyncClient()

    # 创建任务
    print("\n1. 创建报告生成任务...")
    task = client.create_report(
        query="人工智能在医疗领域的应用",
        report_type="comprehensive",
        search_depth="deep"
    )
    task_id = task['task_id']
    print(f"✅ 任务已创建: {task_id}")
    print(f"   状态: {task['status']}")
    print(f"   消息: {task['message']}")

    # 等待完成
    print("\n2. 等待任务完成...")
    try:
        result = client.wait_for_completion(task_id, poll_interval=5)

        print("\n3. 任务结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 下载文件
        print("\n4. 下载生成的文件...")
        file_path = client.download_file(task_id, file_type="html")
        print(f"✅ 文件已下载: {file_path}")

    except Exception as e:
        print(f"❌ 错误: {e}")


def example_fiction_creation():
    """示例：小说创作"""
    print("\n" + "=" * 60)
    print("示例 2: 小说创作")
    print("=" * 60)

    client = XunLongAsyncClient()

    # 创建任务
    print("\n1. 创建小说创作任务...")
    task = client.create_fiction(
        query="一个关于时间旅行的科幻短篇小说",
        genre="scifi",
        length="short"
    )
    task_id = task['task_id']
    print(f"✅ 任务已创建: {task_id}")

    # 等待完成
    print("\n2. 等待任务完成...")
    try:
        result = client.wait_for_completion(task_id)
        print("\n✅ 小说创作完成!")
        print(f"   项目ID: {result['project_id']}")

    except Exception as e:
        print(f"❌ 错误: {e}")


def example_task_management():
    """示例：任务管理"""
    print("\n" + "=" * 60)
    print("示例 3: 任务管理")
    print("=" * 60)

    client = XunLongAsyncClient()

    # 列出所有任务
    print("\n1. 列出所有任务...")
    tasks = client.list_tasks(limit=10)
    print(f"总任务数: {tasks['total']}")

    for task in tasks['tasks'][:5]:
        print(f"\n  任务ID: {task['task_id']}")
        print(f"  类型: {task['task_type']}")
        print(f"  状态: {task['status']}")
        print(f"  查询: {task['query']}")
        print(f"  进度: {task['progress']}%")

    # 列出待执行任务
    print("\n2. 列出待执行任务...")
    pending = client.list_tasks(status="pending")
    print(f"待执行任务数: {pending['total']}")


def main():
    """主函数"""
    print("🌐 XunLong 异步API客户端示例")
    print("=" * 60)

    # 检查API服务
    client = XunLongAsyncClient()
    try:
        response = requests.get(f"{client.base_url}/health", timeout=5)
        response.raise_for_status()
        print("✅ API服务正常")
    except:
        print("❌ API服务不可用")
        print("请先启动API服务: python run_api.py")
        print("并启动任务执行器: python start_worker.py")
        return

    # 运行示例（取消注释以运行）
    # example_report_generation()
    # example_fiction_creation()
    example_task_management()


if __name__ == "__main__":
    main()
