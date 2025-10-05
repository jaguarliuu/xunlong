"""启动后台任务执行器"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from src.task_worker import TaskWorker
from loguru import logger


async def main():
    """启动任务执行器"""
    logger.info("=" * 60)
    logger.info("XunLong 后台任务执行器")
    logger.info("=" * 60)
    logger.info("")
    logger.info("该进程将持续运行，监听并执行异步任务")
    logger.info("请保持此进程运行，按Ctrl+C停止")
    logger.info("")
    logger.info("=" * 60)

    worker = TaskWorker()

    try:
        await worker.run_forever(interval=5)
    except KeyboardInterrupt:
        logger.info("\n接收到退出信号")
        worker.stop()
        logger.info("任务执行器已停止")


if __name__ == "__main__":
    asyncio.run(main())
