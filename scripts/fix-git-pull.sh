#!/bin/bash

# ==================================================
# 腾讯云服务器 Git 拉取问题诊断和修复脚本
# ==================================================
# 使用：在腾讯云服务器上运行此脚本
# 位置：/opt/script-parser/

set -e

echo "🔍 Git 拉取问题诊断和修复脚本"
echo "=================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ 错误：未找到 docker-compose.prod.yml"
    echo "请确保在项目根目录 (/opt/script-parser/) 下运行此脚本"
    exit 1
fi

echo "📂 当前目录: $(pwd)"
echo ""

# 1. 检查 Git 是否安装
echo "1️⃣ 检查 Git 安装..."
if command -v git &> /dev/null; then
    echo "✅ Git 已安装: $(git --version)"
else
    echo "❌ Git 未安装，正在安装..."
    if command -v yum &> /dev/null; then
        sudo yum install -y git
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y git
    else
        echo "❌ 无法自动安装 Git，请手动安装"
        exit 1
    fi
fi
echo ""

# 2. 检查是否为 Git 仓库
echo "2️⃣ 检查 Git 仓库状态..."
if [ -d ".git" ]; then
    echo "✅ 这是一个 Git 仓库"
    
    # 检查远程仓库配置
    echo ""
    echo "📡 远程仓库配置:"
    git remote -v || echo "⚠️  未配置远程仓库"
    
    # 检查当前分支
    echo ""
    echo "🌿 当前分支:"
    git branch --show-current || echo "⚠️  无法获取当前分支"
    
    # 检查工作区状态
    echo ""
    echo "📋 工作区状态:"
    if git diff-index --quiet HEAD --; then
        echo "✅ 工作区干净"
    else
        echo "⚠️  工作区有未提交的更改:"
        git status --short
        echo ""
        echo "💡 建议：先提交或暂存这些更改"
    fi
else
    echo "❌ 这不是一个 Git 仓库"
    echo ""
    echo "🔧 正在初始化 Git 仓库..."
    
    # 询问用户是否要初始化
    read -p "是否要初始化 Git 仓库并设置远程仓库? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git init
        echo "✅ Git 仓库已初始化"
        echo ""
        echo "📝 请提供远程仓库 URL:"
        read -p "Git 仓库 URL (例如: https://github.com/user/repo.git 或 git@github.com:user/repo.git): " REPO_URL
        if [ -n "$REPO_URL" ]; then
            git remote add origin "$REPO_URL"
            echo "✅ 远程仓库已添加: $REPO_URL"
        fi
    else
        echo "❌ 取消操作"
        exit 1
    fi
fi
echo ""

# 3. 尝试拉取代码
echo "3️⃣ 尝试拉取最新代码..."
echo ""

# 检查远程仓库是否存在
if git remote | grep -q "origin"; then
    echo "📥 正在从 origin 拉取 main 分支..."
    
    # 先 fetch
    if git fetch origin; then
        echo "✅ Fetch 成功"
    else
        echo "❌ Fetch 失败"
        echo ""
        echo "可能的原因："
        echo "  - 网络连接问题"
        echo "  - 远程仓库 URL 错误"
        echo "  - 认证失败（需要配置 SSH 密钥或访问令牌）"
        echo ""
        echo "💡 解决方案："
        echo "  1. 检查网络连接: ping github.com (或您的 Git 服务器)"
        echo "  2. 检查远程仓库 URL: git remote -v"
        echo "  3. 如果是私有仓库，需要配置 SSH 密钥或访问令牌"
        exit 1
    fi
    
    # 检查本地是否有 main 分支
    if git show-ref --verify --quiet refs/heads/main; then
        echo "✅ 本地 main 分支存在"
        CURRENT_BRANCH=$(git branch --show-current)
        if [ "$CURRENT_BRANCH" != "main" ]; then
            echo "⚠️  当前不在 main 分支，正在切换到 main..."
            git checkout main
        fi
        
        # 尝试合并
        echo ""
        echo "🔄 正在合并远程更改..."
        if git pull origin main; then
            echo "✅ 代码拉取成功！"
        else
            echo "❌ 代码拉取失败（可能有冲突）"
            echo ""
            echo "💡 如果遇到冲突，可以尝试："
            echo "  - 查看冲突: git status"
            echo "  - 手动解决冲突后: git add . && git commit"
            echo "  - 或者放弃本地更改: git reset --hard origin/main"
            exit 1
        fi
    else
        echo "⚠️  本地没有 main 分支，正在创建并跟踪远程 main..."
        if git checkout -b main origin/main; then
            echo "✅ 已创建并切换到 main 分支"
        else
            echo "❌ 无法创建 main 分支"
            exit 1
        fi
    fi
else
    echo "❌ 未配置 origin 远程仓库"
    echo ""
    echo "💡 请先配置远程仓库："
    echo "  git remote add origin <repository-url>"
    exit 1
fi

echo ""
echo "=================================="
echo "🎉 Git 拉取完成！"
echo "=================================="
echo ""
echo "📊 当前状态:"
git log --oneline -5
echo ""
echo "💡 下一步："
echo "  - 如果后端代码有更新，运行: docker-compose -f docker-compose.prod.yml restart coprocessor"
echo "  - 如果前端代码有更新，需要重新构建镜像"
echo ""






