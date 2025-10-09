"""TODO: Add docstring."""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import Dict, Any
from loguru import logger

# 
sys.path.append(str(Path(__file__).parent.parent))

from src.task_manager import TaskManager, TaskStatus, TaskType, get_task_manager
from src.deep_search_agent import DeepSearchAgent


class TaskWorker:
    """TODO: Add docstring."""

    def __init__(self, task_manager: TaskManager = None):
        """
        

        Args:
            task_manager: 
        """
        self.task_manager = task_manager or get_task_manager()
        self.is_running = False
        logger.info("")

    async def execute_task(self, task_id: str) -> bool:
        """
        

        Args:
            task_id: ID

        Returns:
            
        """
        task_info = self.task_manager.get_task(task_id)
        if not task_info:
            logger.error(f": {task_id}")
            return False

        logger.info(f": {task_id} ({task_info.task_type.value})")

        try:
            # 
            self.task_manager.update_task_status(task_id, TaskStatus.RUNNING)

            # 
            if task_info.task_type == TaskType.REPORT:
                result = await self._execute_report_task(task_id, task_info)
            elif task_info.task_type == TaskType.FICTION:
                result = await self._execute_fiction_task(task_id, task_info)
            elif task_info.task_type == TaskType.PPT:
                result = await self._execute_ppt_task(task_id, task_info)
            else:
                raise ValueError(f": {task_info.task_type}")

            # 
            if result.get('success'):
                self.task_manager.complete_task(
                    task_id,
                    result=result,
                    project_id=result.get('project_id', ''),
                    output_dir=result.get('output_dir', '')
                )
                logger.info(f": {task_id}")
                return True
            else:
                self.task_manager.fail_task(task_id, result.get('error', ''))
                logger.error(f": {task_id}")
                return False

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f" {task_id}: {error_msg}")
            self.task_manager.fail_task(task_id, error_msg)
            return False

    async def _execute_report_task(
        self,
        task_id: str,
        task_info
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        query = task_info.query
        context = task_info.context

        logger.info(f": {query}")

        try:
            # 
            self.task_manager.update_task_progress(task_id, 10, "")

            # 
            agent = DeepSearchAgent()

            # 
            self.task_manager.update_task_progress(task_id, 20, "")

            # 
            # : DeepSearchAgent
            result = await agent.search(query, context=context)

            # 
            self.task_manager.update_task_progress(task_id, 90, "")

            # 
            return {
                'success': True,
                'project_id': result.get('project_id', ''),
                'output_dir': result.get('output_dir', ''),
                'output_format': context.get('output_format', 'html'),
                'files': result.get('files', []),
                'stats': result.get('stats', {})
            }

        except Exception as e:
            logger.error(f": {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _execute_fiction_task(
        self,
        task_id: str,
        task_info
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        query = task_info.query
        context = task_info.context

        logger.info(f": {query}")

        try:
            # 
            self.task_manager.update_task_progress(task_id, 10, "")

            # 
            agent = DeepSearchAgent()

            # 
            self.task_manager.update_task_progress(task_id, 20, "")

            # 
            result = await agent.search(query, context=context)

            # 
            self.task_manager.update_task_progress(task_id, 90, "")

            return {
                'success': True,
                'project_id': result.get('project_id', ''),
                'output_dir': result.get('output_dir', ''),
                'chapters': result.get('chapters', 0),
                'files': result.get('files', []),
                'stats': result.get('stats', {})
            }

        except Exception as e:
            logger.error(f": {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _execute_ppt_task(
        self,
        task_id: str,
        task_info
    ) -> Dict[str, Any]:
        """PPT"""
        query = task_info.query
        context = task_info.context

        logger.info(f"PPT: {query}")

        try:
            # 
            self.task_manager.update_task_progress(task_id, 10, "PPT")

            # 
            agent = DeepSearchAgent()

            # 
            self.task_manager.update_task_progress(task_id, 20, "")

            # 
            result = await agent.search(query, context=context)

            # 
            self.task_manager.update_task_progress(task_id, 90, "")

            return {
                'success': True,
                'project_id': result.get('project_id', ''),
                'output_dir': result.get('output_dir', ''),
                'slides': result.get('slides', 0),
                'files': result.get('files', []),
                'stats': result.get('stats', {})
            }

        except Exception as e:
            logger.error(f"PPT: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def process_pending_tasks(self, max_tasks: int = 1) -> int:
        """
        

        Args:
            max_tasks: 

        Returns:
            
        """
        pending_tasks = self.task_manager.get_pending_tasks(limit=max_tasks)

        if not pending_tasks:
            return 0

        logger.info(f" {len(pending_tasks)} ")

        processed = 0
        for task_info in pending_tasks:
            success = await self.execute_task(task_info.task_id)
            if success:
                processed += 1

        return processed

    async def run_forever(self, interval: int = 5):
        """
        

        Args:
            interval: ()
        """
        self.is_running = True
        logger.info(f" (: {interval})")

        while self.is_running:
            try:
                # 
                processed = await self.process_pending_tasks(max_tasks=1)

                if processed > 0:
                    logger.info(f" {processed} ")

                # 
                await asyncio.sleep(interval)

            except KeyboardInterrupt:
                logger.info("")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f": {e}")
                await asyncio.sleep(interval)

        logger.info("")

    def stop(self):
        """TODO: Add docstring."""
        self.is_running = False


async def main():
    """ - """
    logger.info("=" * 50)
    logger.info("XunLong ")
    logger.info("=" * 50)

    worker = TaskWorker()

    try:
        await worker.run_forever(interval=5)
    except KeyboardInterrupt:
        logger.info("")
        worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
