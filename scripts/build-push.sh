#!/bin/bash

# ScriptParser 多平台构建和推送脚本
# 
# 使用方法：
# 1. 仅本地构建（多平台）：./scripts/build-push.sh
# 2. 构建并推送到仓库：REGISTRY=your-registry.com ./scripts/build-push.sh
# 3. 指定平台：PLATFORM=linux/amd64 ./scripts/build-push.sh
# 4. 指定标签：TAG=v1.0.0 ./scripts/build-push.sh
# 5. 组合使用：REGISTRY=ccr.ccs.tencentyun.com/baokuan-jieqouqi PLATFORM=linux/amd64 TAG=latest ./scripts/build-push.sh
#
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
PLATFORM=${PLATFORM:-"linux/amd64,linux/arm64"}
PUSH=${PUSH:-"false"}

echo -e "${GREEN}🚀 开始构建 ScriptParser 项目${NC}"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 检查是否需要推送
if [ ! -z "$REGISTRY" ]; then
    PUSH="true"
    WEB_IMAGE="${REGISTRY}/${PROJECT_NAME}-web:${TAG}"
    COPROCESSOR_IMAGE="${REGISTRY}/${PROJECT_NAME}-coprocessor:${TAG}"
    BUILD_ARGS="--push"
else
    WEB_IMAGE="${PROJECT_NAME}-web:${TAG}"
    COPROCESSOR_IMAGE="${PROJECT_NAME}-coprocessor:${TAG}"
    BUILD_ARGS="--load"
fi

echo -e "${YELLOW}🏗️  构建平台: ${PLATFORM}${NC}"
echo -e "${YELLOW}📦 构建目标: $([ "$PUSH" = "true" ] && echo "推送到仓库" || echo "本地构建")${NC}"

# 构建 Web 应用
echo -e "${YELLOW}📦 构建 Web 应用...${NC}"
docker buildx build \
    --platform ${PLATFORM} \
    -f apps/web/Dockerfile \
    -t ${WEB_IMAGE} \
    ${BUILD_ARGS} \
    .

# 构建 AI 协处理器
echo -e "${YELLOW}🤖 构建 AI 协处理器...${NC}"
docker buildx build \
    --platform ${PLATFORM} \
    -f apps/coprocessor/Dockerfile \
    -t ${COPROCESSOR_IMAGE} \
    ${BUILD_ARGS} \
    apps/coprocessor

# 构建结果提示
if [ "$PUSH" = "true" ]; then
    echo -e "${GREEN}✅ 镜像已推送到 ${REGISTRY}${NC}"
else
    echo -e "${GREEN}✅ 镜像已构建到本地${NC}"
fi

echo -e "${GREEN}🎉 构建完成！${NC}"
echo -e "${YELLOW}使用以下命令启动服务:${NC}"
echo -e "  docker-compose up -d"