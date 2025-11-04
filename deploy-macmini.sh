#!/bin/bash

# ==================================================
# ScriptParser Mac mini 部署脚本
# ==================================================

set -e

echo "🍎 ScriptParser Mac mini 部署工具"
echo "=================================="
echo ""

# 检查是否在项目根目录
if [ ! -f "docker-compose.macmini.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 获取 Mac mini 的局域网 IP
echo "🔍 检测 Mac mini IP 地址..."
MAC_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo "127.0.0.1")
echo "📍 检测到 IP: $MAC_IP"
echo ""

# 询问是否使用检测到的 IP
read -p "是否使用此 IP 地址? (y/n, 默认 y): " confirm
confirm=${confirm:-y}

if [ "$confirm" != "y" ]; then
    read -p "请输入 Mac mini 的 IP 地址: " MAC_IP
fi

echo ""
echo "📝 配置信息:"
echo "  - IP 地址: $MAC_IP"
echo "  - 访问端口: 8081"
echo "  - 访问地址: http://$MAC_IP:8081"
echo ""

# 更新 docker-compose.macmini.yml 中的 IP
echo "🔧 更新配置文件..."
sed -i.bak "s|http://192.168.31.100:8081|http://$MAC_IP:8081|g" docker-compose.macmini.yml
rm -f docker-compose.macmini.yml.bak

# 检查环境变量文件
if [ ! -f "apps/coprocessor/.env" ]; then
    echo "⚠️  警告: 未找到 apps/coprocessor/.env 文件"
    echo "   请从 apps/coprocessor/.env.example 复制并配置"
    read -p "是否继续? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
fi

echo ""
echo "🚀 开始部署..."
echo ""

# 停止现有服务
echo "⏹️  停止现有服务..."
docker-compose -f docker-compose.macmini.yml down 2>/dev/null || true

# 构建并启动服务
echo "🔨 构建镜像并启动服务（首次构建可能需要 10-20 分钟）..."
docker-compose -f docker-compose.macmini.yml up -d --build

# 等待服务启动
echo ""
echo "⏳ 等待服务启动（健康检查中）..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker-compose -f docker-compose.macmini.yml ps

# 健康检查
echo ""
echo "🔍 健康检查:"
if curl -f -s "http://localhost:8081/api/health" > /dev/null; then
    echo "✅ API 服务正常"
else
    echo "⚠️  API 服务可能未完全启动，请等待或查看日志"
fi

echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 访问信息:"
echo "  - 本机访问: http://localhost:8081"
echo "  - 局域网访问: http://$MAC_IP:8081"
echo "  - API 健康检查: http://$MAC_IP:8081/api/health"
echo ""
echo "📝 常用命令:"
echo "  - 查看日志: docker-compose -f docker-compose.macmini.yml logs -f"
echo "  - 重启服务: docker-compose -f docker-compose.macmini.yml restart"
echo "  - 停止服务: docker-compose -f docker-compose.macmini.yml down"
echo "  - 查看状态: docker-compose -f docker-compose.macmini.yml ps"
echo ""
echo "=================================="
