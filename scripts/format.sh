#!/bin/bash

# 代码格式化脚本
set -e

echo "🎨 格式化代码..."

# 格式化 Web 应用
if [ -d "apps/web" ]; then
    echo "📦 格式化 Web 应用..."
    cd apps/web
    if [ -f "package.json" ]; then
        pnpm format 2>/dev/null || echo "⚠️  跳过 Web 格式化"
        pnpm lint --fix 2>/dev/null || echo "⚠️  跳过 Web 检查"
    fi
    cd ../..
fi

# 格式化 AI 协处理器
if [ -d "apps/coprocessor" ]; then
    echo "🤖 格式化 AI 协处理器..."
    cd apps/coprocessor
    if command -v ruff &> /dev/null; then
        ruff check --fix . 2>/dev/null || echo "⚠️  Ruff 检查失败"
        ruff format . 2>/dev/null || echo "⚠️  Ruff 格式化失败"
    else
        echo "💡 提示: 安装 ruff 来格式化 Python 代码"
    fi
    cd ../..
fi

echo "✅ 代码格式化完成！"