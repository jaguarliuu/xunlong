"""XunLong API"""

import requests
import time
import json
from typing import Dict, Any, Optional


class XunLongAsyncClient:
    """XunLongAPI"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        

        Args:
            base_url: API
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
        

        Args:
            query: 
            report_type: 
            search_depth: 
            max_results: 
            output_format: 

        Returns:
            
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
        

        Args:
            query: 
            genre: 
            length: 
            viewpoint: 
            output_format: 

        Returns:
            
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
        PPT

        Args:
            query: PPT
            slides: 
            style: 
            theme: 

        Returns:
            
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
        

        Args:
            task_id: ID

        Returns:
            
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        

        Args:
            task_id: ID

        Returns:
            
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}/result"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def download_file(self, task_id: str, file_type: str = "html", save_path: str = None):
        """
        

        Args:
            task_id: ID
            file_type: 
            save_path: 

        Returns:
            
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}/download"
        params = {"file_type": file_type}

        response = self.session.get(url, params=params, stream=True)
        response.raise_for_status()

        # 
        if not save_path:
            filename = response.headers.get('content-disposition', '').split('filename=')[-1].strip('"')
            if not filename:
                filename = f"{task_id}.{file_type}"
            save_path = filename

        # 
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return save_path

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        

        Args:
            task_id: ID

        Returns:
            
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
        

        Args:
            status: 
            task_type: 
            limit: 

        Returns:
            
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
        

        Args:
            task_id: ID
            poll_interval: ()
            timeout: ()
            verbose: 

        Returns:
            
        """
        start_time = time.time()
        last_progress = -1

        while True:
            # 
            if time.time() - start_time > timeout:
                raise TimeoutError(f": {task_id}")

            # 
            status = self.get_task_status(task_id)

            # 
            if verbose and status['progress'] != last_progress:
                print(f": {status['progress']}% - {status['current_step']}")
                last_progress = status['progress']

            # 
            if status['status'] == 'completed':
                if verbose:
                    print(" !")
                return self.get_task_result(task_id)

            if status['status'] == 'failed':
                raise Exception(f": {status.get('error', '')}")

            if status['status'] == 'cancelled':
                raise Exception("")

            # 
            time.sleep(poll_interval)


def example_report_generation():
    """"""
    print("\n" + "=" * 60)
    print(" 1: ")
    print("=" * 60)

    client = XunLongAsyncClient()

    # 
    print("\n1. ...")
    task = client.create_report(
        query="",
        report_type="comprehensive",
        search_depth="deep"
    )
    task_id = task['task_id']
    print(f" : {task_id}")
    print(f"   : {task['status']}")
    print(f"   : {task['message']}")

    # 
    print("\n2. ...")
    try:
        result = client.wait_for_completion(task_id, poll_interval=5)

        print("\n3. :")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 
        print("\n4. ...")
        file_path = client.download_file(task_id, file_type="html")
        print(f" : {file_path}")

    except Exception as e:
        print(f" : {e}")


def example_fiction_creation():
    """"""
    print("\n" + "=" * 60)
    print(" 2: ")
    print("=" * 60)

    client = XunLongAsyncClient()

    # 
    print("\n1. ...")
    task = client.create_fiction(
        query="",
        genre="scifi",
        length="short"
    )
    task_id = task['task_id']
    print(f" : {task_id}")

    # 
    print("\n2. ...")
    try:
        result = client.wait_for_completion(task_id)
        print("\n !")
        print(f"   ID: {result['project_id']}")

    except Exception as e:
        print(f" : {e}")


def example_task_management():
    """"""
    print("\n" + "=" * 60)
    print(" 3: ")
    print("=" * 60)

    client = XunLongAsyncClient()

    # 
    print("\n1. ...")
    tasks = client.list_tasks(limit=10)
    print(f": {tasks['total']}")

    for task in tasks['tasks'][:5]:
        print(f"\n  ID: {task['task_id']}")
        print(f"  : {task['task_type']}")
        print(f"  : {task['status']}")
        print(f"  : {task['query']}")
        print(f"  : {task['progress']}%")

    # 
    print("\n2. ...")
    pending = client.list_tasks(status="pending")
    print(f": {pending['total']}")


def main():
    """"""
    print(" XunLong API")
    print("=" * 60)

    # API
    client = XunLongAsyncClient()
    try:
        response = requests.get(f"{client.base_url}/health", timeout=5)
        response.raise_for_status()
        print(" API")
    except:
        print(" API")
        print("API: python run_api.py")
        print(": python start_worker.py")
        return

    # 
    # example_report_generation()
    # example_fiction_creation()
    example_task_management()


if __name__ == "__main__":
    main()
