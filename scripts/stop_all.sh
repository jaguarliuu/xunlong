#!/bin/bash

# XunLong 

set -e

echo "=================================="
echo "  XunLong "
echo "=================================="
echo ""

# 
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# API
if [ -f logs/api.pid ]; then
    API_PID=$(cat logs/api.pid)
    if ps -p $API_PID > /dev/null; then
        echo "API (PID: $API_PID)..."
        kill $API_PID
        echo "    API"
    else
        echo "    API (PID: $API_PID)"
    fi
    rm -f logs/api.pid
else
    echo "    APIPID"
fi

# 
if [ -f logs/worker.pid ]; then
    WORKER_PID=$(cat logs/worker.pid)
    if ps -p $WORKER_PID > /dev/null; then
        echo " (PID: $WORKER_PID)..."
        kill $WORKER_PID
        echo "    "
    else
        echo "     (PID: $WORKER_PID)"
    fi
    rm -f logs/worker.pid
else
    echo "    PID"
fi

echo ""
echo " "
echo ""
