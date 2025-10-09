#!/bin/bash

# XunLong 
# API

set -e

echo "=================================="
echo "  XunLong "
echo "=================================="
echo ""

# 
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# Python
if ! command -v python &> /dev/null; then
    echo " : Python"
    exit 1
fi

echo " Python: $(python --version)"
echo " : $PROJECT_DIR"
echo ""

# 
mkdir -p tasks
mkdir -p storage
mkdir -p logs

echo "..."
echo ""

# API
echo "1. API ( 8000)..."
python run_api.py > logs/api.log 2>&1 &
API_PID=$!
echo "    API (PID: $API_PID)"
sleep 2

# 
echo "2. ..."
python start_worker.py > logs/worker.log 2>&1 &
WORKER_PID=$!
echo "     (PID: $WORKER_PID)"
sleep 2

# PID
echo $API_PID > logs/api.pid
echo $WORKER_PID > logs/worker.pid

echo ""
echo "=================================="
echo "   "
echo "=================================="
echo ""
echo " :"
echo "   API:    http://localhost:8000"
echo "   API:      http://localhost:8000/docs"
echo "   :     http://localhost:8000/health"
echo ""
echo " :"
echo "   API:      logs/api.log"
echo "   Worker:   logs/worker.log"
echo ""
echo " :"
echo "   : ./scripts/stop_all.sh"
echo "   : kill $API_PID $WORKER_PID"
echo ""
echo " :"
echo "   API: tail -f logs/api.log"
echo "   Worker: tail -f logs/worker.log"
echo ""
