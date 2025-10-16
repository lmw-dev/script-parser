#!/bin/bash

# ScriptParser 构建和推送脚本
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
REGISTRY=${REGISTRY:-""}
TAG=${TAG:-"latest"}
PROJECT_NAME="scriptparser"

echo -e "${GREEN}🚀 开始构建 ScriptParser 项目${NC}"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 构建 Web 应用
echo -e "${YELLOW}📦 构建 Web 应用...${NC}"
docker build -f apps/web/Dockerfile -t ${PROJECT_NAME}-web:${TAG} .

# 构建 AI 协处理器
echo -e "${YELLOW}🤖 构建 AI 协处理器...${NC}"
docker build -f apps/coprocessor/Dockerfile -t ${PROJECT_NAME}-coprocessor:${TAG} apps/coprocessor

# 如果指定了 registry，则推送镜像
if [ ! -z "$REGISTRY" ]; then
    echo -e "${YELLOW}📤 推送镜像到 ${REGISTRY}...${NC}"
    
    # 标记镜像
    docker tag ${PROJECT_NAME}-web:${TAG} ${REGISTRY}/${PROJECT_NAME}-web:${TAG}
    docker tag ${PROJECT_NAME}-coprocessor:${TAG} ${REGISTRY}/${PROJECT_NAME}-coprocessor:${TAG}
    
    # 推送镜像
    docker push ${REGISTRY}/${PROJECT_NAME}-web:${TAG}
    docker push ${REGISTRY}/${PROJECT_NAME}-coprocessor:${TAG}
    
    echo -e "${GREEN}✅ 镜像推送完成${NC}"
else
    echo -e "${YELLOW}ℹ️  跳过推送 (未指定 REGISTRY)${NC}"
fi

echo -e "${GREEN}🎉 构建完成！${NC}"
echo -e "${YELLOW}使用以下命令启动服务:${NC}"
echo -e "  docker-compose up -d"