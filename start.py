#!/usr/bin/env python
"""XunLong 统一启动脚本 - 同时启动API服务器和任务执行器"""

import sys
import time
import signal
import subprocess
from pathlib import Path
from loguru import logger


class XunLongServer:
    """XunLong服务管理器"""

    def __init__(self):
        self.api_process = None
        self.worker_process = None
        self.is_running = False

    def start_api(self):
        """启动API服务器"""
        logger.info("正在启动API服务器...")

        self.api_process = subprocess.Popen(
            [sys.executable, "run_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # 等待API启动
        time.sleep(2)

        if self.api_process.poll() is None:
            logger.success("✓ API服务器已启动 (PID: {})", self.api_process.pid)
            return True
        else:
            logger.error("✗ API服务器启动失败")
            return False

    def start_worker(self):
        """启动任务执行器"""
        logger.info("正在启动任务执行器...")

        self.worker_process = subprocess.Popen(
            [sys.executable, "start_worker.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # 等待Worker启动
        time.sleep(2)

        if self.worker_process.poll() is None:
            logger.success("✓ 任务执行器已启动 (PID: {})", self.worker_process.pid)
            return True
        else:
            logger.error("✗ 任务执行器启动失败")
            return False

    def start_all(self):
        """启动所有服务"""
        logger.info("=" * 60)
        logger.info("XunLong 服务启动器")
        logger.info("=" * 60)
        logger.info("")

        # 创建必要的目录
        Path("tasks").mkdir(exist_ok=True)
        Path("storage").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

        # 启动API服务器
        if not self.start_api():
            logger.error("API服务器启动失败，退出")
            return False

        time.sleep(1)

        # 启动任务执行器
        if not self.start_worker():
            logger.error("任务执行器启动失败，停止API服务器")
            self.stop_all()
            return False

        self.is_running = True

        logger.info("")
        logger.info("=" * 60)
        logger.success("✅ 所有服务已启动")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📊 服务信息:")
        logger.info("   API服务器:    http://localhost:8000")
        logger.info("   API文档:      http://localhost:8000/docs")
        logger.info("   健康检查:     http://localhost:8000/health")
        logger.info("")
        logger.info("🛑 停止服务:")
        logger.info("   按 Ctrl+C 停止所有服务")
        logger.info("")
        logger.info("💡 提示:")
        logger.info("   - 查看API日志: 在另一个终端运行此脚本")
        logger.info("   - 测试API: python scripts/test_api.py")
        logger.info("   - 使用示例: python examples/async_api_client.py")
        logger.info("")
        logger.info("⏳ 服务运行中，按 Ctrl+C 停止...")
        logger.info("")

        return True

    def stop_all(self):
        """停止所有服务"""
        logger.info("")
        logger.info("正在停止服务...")

        # 停止任务执行器
        if self.worker_process and self.worker_process.poll() is None:
            logger.info("正在停止任务执行器...")
            self.worker_process.terminate()
            try:
                self.worker_process.wait(timeout=5)
                logger.success("✓ 任务执行器已停止")
            except subprocess.TimeoutExpired:
                logger.warning("任务执行器未响应，强制终止...")
                self.worker_process.kill()
                self.worker_process.wait()

        # 停止API服务器
        if self.api_process and self.api_process.poll() is None:
            logger.info("正在停止API服务器...")
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=5)
                logger.success("✓ API服务器已停止")
            except subprocess.TimeoutExpired:
                logger.warning("API服务器未响应，强制终止...")
                self.api_process.kill()
                self.api_process.wait()

        self.is_running = False
        logger.success("✅ 所有服务已停止")

    def monitor_processes(self):
        """监控进程状态"""
        while self.is_running:
            try:
                # 检查API进程
                if self.api_process and self.api_process.poll() is not None:
                    logger.error("API服务器意外退出，退出码: {}", self.api_process.returncode)
                    self.is_running = False
                    break

                # 检查Worker进程
                if self.worker_process and self.worker_process.poll() is not None:
                    logger.error("任务执行器意外退出，退出码: {}", self.worker_process.returncode)
                    self.is_running = False
                    break

                time.sleep(1)

            except KeyboardInterrupt:
                logger.info("收到中断信号")
                break

    def run(self):
        """运行服务"""
        # 注册信号处理
        def signal_handler(signum, frame):
            logger.info("收到信号 {}, 正在停止服务...", signum)
            self.stop_all()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 启动所有服务
        if not self.start_all():
            sys.exit(1)

        try:
            # 监控进程
            self.monitor_processes()
        finally:
            # 确保清理
            self.stop_all()


def main():
    """主函数"""
    server = XunLongServer()
    server.run()


if __name__ == "__main__":
    main()
