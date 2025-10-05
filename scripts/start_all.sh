#!/bin/bash

# XunLong 完整启动脚本
# 同时启动API服务器和任务执行器

set -e

echo "=================================="
echo "  XunLong 服务启动脚本"
echo "=================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到Python"
    exit 1
fi

echo "✓ Python环境: $(python --version)"
echo "✓ 工作目录: $PROJECT_DIR"
echo ""

# 创建必要的目录
mkdir -p tasks
mkdir -p storage
mkdir -p logs

echo "正在启动服务..."
echo ""

# 启动API服务器（后台运行）
echo "1. 启动API服务器 (端口 8000)..."
python run_api.py > logs/api.log 2>&1 &
API_PID=$!
echo "   ✓ API服务器已启动 (PID: $API_PID)"
sleep 2

# 启动任务执行器（后台运行）
echo "2. 启动任务执行器..."
python start_worker.py > logs/worker.log 2>&1 &
WORKER_PID=$!
echo "   ✓ 任务执行器已启动 (PID: $WORKER_PID)"
sleep 2

# 保存PID
echo $API_PID > logs/api.pid
echo $WORKER_PID > logs/worker.pid

echo ""
echo "=================================="
echo "  ✅ 所有服务已启动"
echo "=================================="
echo ""
echo "📊 服务信息:"
echo "   API服务器:    http://localhost:8000"
echo "   API文档:      http://localhost:8000/docs"
echo "   健康检查:     http://localhost:8000/health"
echo ""
echo "📁 日志文件:"
echo "   API日志:      logs/api.log"
echo "   Worker日志:   logs/worker.log"
echo ""
echo "🛑 停止服务:"
echo "   运行: ./scripts/stop_all.sh"
echo "   或者: kill $API_PID $WORKER_PID"
echo ""
echo "💡 提示:"
echo "   查看API日志: tail -f logs/api.log"
echo "   查看Worker日志: tail -f logs/worker.log"
echo ""
