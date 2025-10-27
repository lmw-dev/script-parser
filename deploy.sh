#!/bin/bash

# ==================================================
# ScriptParser 生产环境快速部署脚本
# ==================================================
# 说明：用于腾讯云VPS上的快速更新部署
# 使用：./deploy.sh

set -e  # 遇到错误立即退出

echo "🚀 ScriptParser 生产环境部署脚本"
echo "=================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ 错误：未找到 docker-compose.prod.yml"
    echo "请确保在项目根目录下运行此脚本"
    exit 1
fi

# 1. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main
echo "✅ 代码更新完成"
echo ""

# 2. 重启后端服务（应用代码变更）
echo "🔄 重启后端服务（应用本地代码变更）..."
docker-compose -f docker-compose.prod.yml restart coprocessor
echo "✅ 后端服务重启完成"
echo ""

# 3. 等待服务启动
echo "⏳ 等待服务启动（15秒）..."
sleep 15
echo ""

# 4. 健康检查
echo "🔍 执行健康检查..."
if curl -f http://localhost:8081/api/health 2>/dev/null; then
    echo ""
    echo "✅ 健康检查通过"
else
    echo ""
    echo "⚠️  健康检查失败，请查看日志"
    docker-compose -f docker-compose.prod.yml logs --tail=20 coprocessor
    exit 1
fi
echo ""

# 5. 显示服务状态
echo "📊 服务状态："
docker-compose -f docker-compose.prod.yml ps
echo ""

# 6. 显示最新日志
echo "📋 最新日志："
docker-compose -f docker-compose.prod.yml logs --tail=10 coprocessor
echo ""

echo "=================================="
echo "🎉 部署完成！"
echo "访问地址：http://localhost:8081"
echo "=================================="
