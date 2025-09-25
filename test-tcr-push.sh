#!/bin/bash

# TCR推送测试脚本
set -e

echo "🧪 测试TCR镜像推送功能"
echo "================================"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

echo "🔍 当前可推送的镜像："
docker images | grep ccr.ccs.tencentyun.com

echo ""
echo "📤 推送 Web 镜像到 TCR..."
docker push ccr.ccs.tencentyun.com/baokuan-jieqouqi/scriptparser-web:latest

echo ""
echo "📤 推送 Coprocessor 镜像到 TCR..."
docker push ccr.ccs.tencentyun.com/baokuan-jieqouqi/scriptparser-coprocessor:latest

echo ""
echo "✅ TCR 推送完成！"
echo ""
echo "🧪 测试镜像拉取："
echo "docker pull ccr.ccs.tencentyun.com/baokuan-jieqouqi/scriptparser-web:latest"
echo "docker pull ccr.ccs.tencentyun.com/baokuan-jieqouqi/scriptparser-coprocessor:latest"