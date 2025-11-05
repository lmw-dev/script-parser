#!/bin/bash

# ==================================================
# ScriptParser Mac mini 快速部署脚本
# 适用于代码更新后的快速部署（使用 volumes 挂载）
# ==================================================

set -e

echo "⚡ ScriptParser Mac mini 快速部署"
echo "=================================="
echo ""

# 检查是否在项目根目录
if [ ! -f "docker-compose.macmini.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查是否在 Mac mini 上
if [ ! -d "/Volumes/ExternalLiumw" ]; then
    echo "❌ 错误: 此脚本仅能在 Mac mini 上运行"
    echo "   检测不到外部磁盘 /Volumes/ExternalLiumw"
    exit 1
fi

echo "📥 拉取最新代码..."
git fetch origin
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ 代码已是最新"
else
    echo "🔄 发现新代码，开始更新..."
    
    # 保存本地修改（如有）
    if ! git diff-index --quiet HEAD --; then
        echo "💾 保存本地修改..."
        git stash save "auto-stash before quick deploy"
        STASHED=true
    else
        STASHED=false
    fi
    
    # 拉取代码
    git pull origin main
    
    # 恢复本地修改（如有冲突则保留远程版本）
    if [ "$STASHED" = true ]; then
        echo "🔄 恢复本地修改..."
        if ! git stash pop; then
            echo "⚠️  检测到冲突，保留远程版本..."
            git checkout --theirs .
            git add .
            git stash drop
        fi
    fi
fi

echo ""
echo "🔄 重启服务（使用挂载的代码）..."

# 仅重启后端服务（前端需要重新构建镜像）
/usr/local/bin/docker-compose -f docker-compose.macmini.yml restart coprocessor

echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 健康检查
echo ""
echo "🔍 健康检查:"
MAX_RETRIES=5
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -f -s "http://localhost:8081/api/health" > /dev/null 2>&1; then
        echo "✅ API 服务正常"
        break
    else
        RETRY=$((RETRY+1))
        if [ $RETRY -lt $MAX_RETRIES ]; then
            echo "⏳ 等待服务启动... ($RETRY/$MAX_RETRIES)"
            sleep 3
        else
            echo "⚠️  API 服务启动超时，请检查日志"
            echo "   docker-compose -f docker-compose.macmini.yml logs -f coprocessor"
        fi
    fi
done

echo ""
echo "📊 服务状态:"
/usr/local/bin/docker-compose -f docker-compose.macmini.yml ps

echo ""
echo "✅ 快速部署完成！"
echo ""
echo "📝 提示:"
echo "  - 后端代码已更新并重启（使用挂载方式）"
echo "  - 如果前端代码有更新，需要重新构建镜像"
echo "  - 查看日志: docker-compose -f docker-compose.macmini.yml logs -f"
echo ""
echo "=================================="
