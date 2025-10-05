#!/bin/bash

# XunLong Documentation - Quick Start Script

echo "🐉 XunLong Documentation Setup"
echo "================================"
echo ""

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✅ npm version: $(npm --version)"
echo ""

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start dev server
echo "🚀 Starting VitePress dev server..."
echo ""
echo "   Documentation will be available at:"
echo "   👉 http://localhost:5173"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

npm run docs:dev
