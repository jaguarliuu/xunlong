"""后台任务执行器"""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import Dict, Any
from loguru import logger

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from src.task_manager import TaskManager, TaskStatus, TaskType, get_task_manager
from src.deep_search_agent import DeepSearchAgent


class TaskWorker:
    """任务执行器"""

    def __init__(self, task_manager: TaskManager = None):
        """
        初始化任务执行器

        Args:
            task_manager: 任务管理器实例
        """
        self.task_manager = task_manager or get_task_manager()
        self.is_running = False
        logger.info("任务执行器初始化完成")

    async def execute_task(self, task_id: str) -> bool:
        """
        执行单个任务

        Args:
            task_id: 任务ID

        Returns:
            是否执行成功
        """
        task_info = self.task_manager.get_task(task_id)
        if not task_info:
            logger.error(f"任务不存在: {task_id}")
            return False

        logger.info(f"开始执行任务: {task_id} ({task_info.task_type.value})")

        try:
            # 更新状态为运行中
            self.task_manager.update_task_status(task_id, TaskStatus.RUNNING)

            # 根据任务类型执行
            if task_info.task_type == TaskType.REPORT:
                result = await self._execute_report_task(task_id, task_info)
            elif task_info.task_type == TaskType.FICTION:
                result = await self._execute_fiction_task(task_id, task_info)
            elif task_info.task_type == TaskType.PPT:
                result = await self._execute_ppt_task(task_id, task_info)
            else:
                raise ValueError(f"不支持的任务类型: {task_info.task_type}")

            # 标记完成
            if result.get('success'):
                self.task_manager.complete_task(
                    task_id,
                    result=result,
                    project_id=result.get('project_id', ''),
                    output_dir=result.get('output_dir', '')
                )
                logger.info(f"任务完成: {task_id}")
                return True
            else:
                self.task_manager.fail_task(task_id, result.get('error', '未知错误'))
                logger.error(f"任务失败: {task_id}")
                return False

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"任务执行异常 {task_id}: {error_msg}")
            self.task_manager.fail_task(task_id, error_msg)
            return False

    async def _execute_report_task(
        self,
        task_id: str,
        task_info
    ) -> Dict[str, Any]:
        """执行报告生成任务"""
        query = task_info.query
        context = task_info.context

        logger.info(f"生成报告: {query}")

        try:
            # 更新进度
            self.task_manager.update_task_progress(task_id, 10, "初始化智能体系统")

            # 创建智能体
            agent = DeepSearchAgent()

            # 更新进度
            self.task_manager.update_task_progress(task_id, 20, "开始深度搜索")

            # 执行搜索和生成
            # 注意: 需要修改DeepSearchAgent以支持进度回调
            result = await agent.search(query, context=context)

            # 更新进度
            self.task_manager.update_task_progress(task_id, 90, "生成完成，保存结果")

            # 提取结果信息
            return {
                'success': True,
                'project_id': result.get('project_id', ''),
                'output_dir': result.get('output_dir', ''),
                'output_format': context.get('output_format', 'html'),
                'files': result.get('files', []),
                'stats': result.get('stats', {})
            }

        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _execute_fiction_task(
        self,
        task_id: str,
        task_info
    ) -> Dict[str, Any]:
        """执行小说创作任务"""
        query = task_info.query
        context = task_info.context

        logger.info(f"创作小说: {query}")

        try:
            # 更新进度
            self.task_manager.update_task_progress(task_id, 10, "初始化创作系统")

            # 创建智能体
            agent = DeepSearchAgent()

            # 更新进度
            self.task_manager.update_task_progress(task_id, 20, "开始创作")

            # 执行创作
            result = await agent.search(query, context=context)

            # 更新进度
            self.task_manager.update_task_progress(task_id, 90, "创作完成，保存作品")

            return {
                'success': True,
                'project_id': result.get('project_id', ''),
                'output_dir': result.get('output_dir', ''),
                'chapters': result.get('chapters', 0),
                'files': result.get('files', []),
                'stats': result.get('stats', {})
            }

        except Exception as e:
            logger.error(f"小说创作失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _execute_ppt_task(
        self,
        task_id: str,
        task_info
    ) -> Dict[str, Any]:
        """执行PPT生成任务"""
        query = task_info.query
        context = task_info.context

        logger.info(f"生成PPT: {query}")

        try:
            # 更新进度
            self.task_manager.update_task_progress(task_id, 10, "初始化PPT生成系统")

            # 创建智能体
            agent = DeepSearchAgent()

            # 更新进度
            self.task_manager.update_task_progress(task_id, 20, "研究主题内容")

            # 执行生成
            result = await agent.search(query, context=context)

            # 更新进度
            self.task_manager.update_task_progress(task_id, 90, "生成完成，保存文件")

            return {
                'success': True,
                'project_id': result.get('project_id', ''),
                'output_dir': result.get('output_dir', ''),
                'slides': result.get('slides', 0),
                'files': result.get('files', []),
                'stats': result.get('stats', {})
            }

        except Exception as e:
            logger.error(f"PPT生成失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def process_pending_tasks(self, max_tasks: int = 1) -> int:
        """
        处理待执行任务

        Args:
            max_tasks: 一次处理的最大任务数

        Returns:
            处理的任务数
        """
        pending_tasks = self.task_manager.get_pending_tasks(limit=max_tasks)

        if not pending_tasks:
            return 0

        logger.info(f"发现 {len(pending_tasks)} 个待执行任务")

        processed = 0
        for task_info in pending_tasks:
            success = await self.execute_task(task_info.task_id)
            if success:
                processed += 1

        return processed

    async def run_forever(self, interval: int = 5):
        """
        持续运行，定期检查并执行任务

        Args:
            interval: 检查间隔(秒)
        """
        self.is_running = True
        logger.info(f"任务执行器开始运行 (检查间隔: {interval}秒)")

        while self.is_running:
            try:
                # 处理待执行任务
                processed = await self.process_pending_tasks(max_tasks=1)

                if processed > 0:
                    logger.info(f"本轮处理了 {processed} 个任务")

                # 等待下一次检查
                await asyncio.sleep(interval)

            except KeyboardInterrupt:
                logger.info("收到中断信号，停止执行器")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"执行器异常: {e}")
                await asyncio.sleep(interval)

        logger.info("任务执行器已停止")

    def stop(self):
        """停止执行器"""
        self.is_running = False


async def main():
    """主函数 - 启动任务执行器"""
    logger.info("=" * 50)
    logger.info("XunLong 任务执行器")
    logger.info("=" * 50)

    worker = TaskWorker()

    try:
        await worker.run_forever(interval=5)
    except KeyboardInterrupt:
        logger.info("接收到退出信号")
        worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
