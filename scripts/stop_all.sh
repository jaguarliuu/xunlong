#!/bin/bash

# XunLong 停止脚本

set -e

echo "=================================="
echo "  XunLong 服务停止脚本"
echo "=================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# 读取并停止API服务器
if [ -f logs/api.pid ]; then
    API_PID=$(cat logs/api.pid)
    if ps -p $API_PID > /dev/null; then
        echo "正在停止API服务器 (PID: $API_PID)..."
        kill $API_PID
        echo "   ✓ API服务器已停止"
    else
        echo "   ⚠ API服务器进程不存在 (PID: $API_PID)"
    fi
    rm -f logs/api.pid
else
    echo "   ⚠ 未找到API服务器PID文件"
fi

# 读取并停止任务执行器
if [ -f logs/worker.pid ]; then
    WORKER_PID=$(cat logs/worker.pid)
    if ps -p $WORKER_PID > /dev/null; then
        echo "正在停止任务执行器 (PID: $WORKER_PID)..."
        kill $WORKER_PID
        echo "   ✓ 任务执行器已停止"
    else
        echo "   ⚠ 任务执行器进程不存在 (PID: $WORKER_PID)"
    fi
    rm -f logs/worker.pid
else
    echo "   ⚠ 未找到任务执行器PID文件"
fi

echo ""
echo "✅ 所有服务已停止"
echo ""
