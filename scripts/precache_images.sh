#!/bin/bash

# Docker镜像预缓存脚本
# 在VPN连接时批量拉取常用的基础镜像

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🐳 Docker镜像预缓存工具${NC}"
echo -e "${YELLOW}💡 专为OpenVPN环境优化的镜像缓存策略${NC}"

# 检测VPN连接状态
VPN_CONNECTED=false
if ifconfig | grep -q "utun.*inet.*10\."; then
    VPN_CONNECTED=true
    echo -e "${GREEN}✅ 检测到OpenVPN连接${NC}"
else
    echo -e "${RED}⚠️  未检测到VPN连接，可能影响拉取速度${NC}"
fi

echo ""

# 检查Docker是否运行
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker未运行，请先启动Docker${NC}"
    exit 1
fi

# 项目必需的基础镜像（优先级排序）
CRITICAL_IMAGES=(
    "python:3.12-slim"     # AI co-processor 必需
    "node:20-alpine"       # Web 前端可能需要
    "nginx:alpine"         # 生产环境代理
)

# 常用基础镜像列表（可选）
OPTIONAL_IMAGES=(
    "python:3.11-slim" 
    "python:3.10-slim"
    "node:18-alpine"
    "redis:alpine"
    "postgres:15-alpine"
    "ubuntu:22.04"
    "ubuntu:20.04"
    "alpine:latest"
)

# 合并镜像列表
IMAGES=("${CRITICAL_IMAGES[@]}" "${OPTIONAL_IMAGES[@]}")

# 检查已有镜像
echo -e "${BLUE}🔍 检查已有镜像...${NC}"
EXISTING_IMAGES=()
MISSING_IMAGES=()

for img in "${IMAGES[@]}"; do
    if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${img}$"; then
        EXISTING_IMAGES+=("$img")
    else
        MISSING_IMAGES+=("$img")
    fi
done

if [ ${#EXISTING_IMAGES[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ 已有镜像 (${#EXISTING_IMAGES[@]}个):${NC}"
    for img in "${EXISTING_IMAGES[@]}"; do
        echo "  ✓ $img"
    done
    echo ""
fi

if [ ${#MISSING_IMAGES[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 所有需要的镜像已经存在！${NC}"
    exit 0
fi

echo -e "${YELLOW}📦 需要拉取的镜像 (${#MISSING_IMAGES[@]}个):${NC}"
for img in "${MISSING_IMAGES[@]}"; do
    echo "  - $img"
done

# 只拉取缺失的镜像
IMAGES=("${MISSING_IMAGES[@]}")

echo ""
if [ "$VPN_CONNECTED" = true ]; then
    echo -e "${GREEN}✅ VPN已连接，可以开始拉取${NC}"
    read -p "是否继续？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "取消操作"
        exit 0
    fi
else
    echo -e "${YELLOW}⚠️  没有VPN连接，拉取可能很慢${NC}"
    read -p "仍要继续吗？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消操作"
        exit 0
    fi
fi
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消操作"
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 开始拉取镜像...${NC}"

TOTAL=${#IMAGES[@]}
CURRENT=0
FAILED=()

for img in "${IMAGES[@]}"; do
    CURRENT=$((CURRENT + 1))
    echo -e "${YELLOW}[$CURRENT/$TOTAL] 拉取: $img${NC}"
    
    if docker pull $img; then
        echo -e "${GREEN}✅ 成功: $img${NC}"
    else
        echo -e "${RED}❌ 失败: $img${NC}"
        FAILED+=($img)
    fi
    echo ""
done

echo -e "${GREEN}📊 缓存完成报告:${NC}"
echo -e "成功: $((TOTAL - ${#FAILED[@]}))/$TOTAL"
echo -e "失败: ${#FAILED[@]}/$TOTAL"

if [ ${#FAILED[@]} -gt 0 ]; then
    echo -e "${RED}失败的镜像:${NC}"
    for img in "${FAILED[@]}"; do
        echo "  - $img"
    done
fi

# 显示当前镜像占用空间
echo ""
echo -e "${BLUE}💾 当前镜像存储使用情况:${NC}"
docker system df

# 提供清理建议
echo ""
echo -e "${YELLOW}💡 优化建议:${NC}"
echo "1. 定期运行: docker system prune 清理无用镜像"
echo "2. 使用: docker images --filter dangling=true -q | xargs docker rmi 清理悬挂镜像"
echo "3. 镜像缓存后，可以断开VPN进行构建"