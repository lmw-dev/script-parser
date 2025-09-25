#!/bin/bash

# ==================================================
# SOP合规性检查脚本
# ==================================================
# 根据 [[SOP - 腾讯云项目部署流程]] 多项目部署防冲突规范进行检查

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}🔍 SOP合规性检查 - 多项目部署防冲突规范${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# 加载环境变量
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
else
    echo -e "${RED}❌ 未找到 .env 文件${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 当前项目配置:${NC}"
echo -e "  项目名称: ScriptParser (脚本快拆)"
echo -e "  项目前缀: ${PROJECT_PREFIX:-sp}"
echo -e "  Nginx端口: ${NGINX_PORT:-8081}"
echo ""

# 检查项目前缀
echo -e "${BLUE}1️⃣ 检查项目前缀规范...${NC}"
if [ "${PROJECT_PREFIX}" = "sp" ]; then
    echo -e "${GREEN}✅ 项目前缀正确: ${PROJECT_PREFIX}${NC}"
else
    echo -e "${RED}❌ 项目前缀应为 'sp'，当前为: ${PROJECT_PREFIX}${NC}"
fi

# 检查端口配置
echo -e "${BLUE}2️⃣ 检查端口配置...${NC}"
if [ "${NGINX_PORT}" = "8081" ]; then
    echo -e "${GREEN}✅ Nginx端口配置正确: ${NGINX_PORT} (脚本快拆专用)${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx端口: ${NGINX_PORT} (确保与其他项目不冲突)${NC}"
fi

# 检查Docker Compose配置
echo -e "${BLUE}3️⃣ 检查Docker Compose配置...${NC}"
if [ -f "$PROJECT_ROOT/docker-compose.prod.yml" ]; then
    
    # 检查容器名称规范
    echo -e "${YELLOW}  检查容器名称规范...${NC}"
    if grep -q "\${PROJECT_PREFIX}_frontend" "$PROJECT_ROOT/docker-compose.prod.yml" && \
       grep -q "\${PROJECT_PREFIX}_backend" "$PROJECT_ROOT/docker-compose.prod.yml" && \
       grep -q "\${PROJECT_PREFIX}_nginx" "$PROJECT_ROOT/docker-compose.prod.yml"; then
        echo -e "${GREEN}  ✅ 容器名称符合规范: ${PROJECT_PREFIX}_frontend, ${PROJECT_PREFIX}_backend, ${PROJECT_PREFIX}_nginx${NC}"
    else
        echo -e "${RED}  ❌ 容器名称不符合规范${NC}"
    fi
    
    # 检查网络配置
    echo -e "${YELLOW}  检查网络配置...${NC}"
    if grep -q "\${PROJECT_PREFIX}_default" "$PROJECT_ROOT/docker-compose.prod.yml"; then
        echo -e "${GREEN}  ✅ 网络配置符合规范: ${PROJECT_PREFIX}_default${NC}"
    else
        echo -e "${RED}  ❌ 网络配置不符合规范，应为: ${PROJECT_PREFIX}_default${NC}"
    fi
    
    # 检查数据卷配置
    echo -e "${YELLOW}  检查数据卷配置...${NC}"
    if grep -q "\${PROJECT_PREFIX}_nginx_data" "$PROJECT_ROOT/docker-compose.prod.yml"; then
        echo -e "${GREEN}  ✅ 数据卷配置符合规范: ${PROJECT_PREFIX}_nginx_data${NC}"
    else
        echo -e "${YELLOW}  ⚠️  未发现标准数据卷配置${NC}"
    fi
    
else
    echo -e "${RED}❌ 未找到 docker-compose.prod.yml 文件${NC}"
fi

# 检查环境变量配置
echo -e "${BLUE}4️⃣ 检查环境变量配置...${NC}"
required_vars=("PROJECT_PREFIX" "TCR_REGISTRY" "TCR_NAMESPACE" "NGINX_PORT")
all_vars_ok=true

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}  ❌ 缺少必需环境变量: $var${NC}"
        all_vars_ok=false
    else
        echo -e "${GREEN}  ✅ $var: ${!var}${NC}"
    fi
done

# SOP规范对比表
echo ""
echo -e "${BLUE}📊 SOP规范对比表:${NC}"
echo -e "${YELLOW}┌─────────────────┬─────────────────────┬─────────────────────┐${NC}"
echo -e "${YELLOW}│ 资源类型        │ 命名规范            │ 脚本快拆当前配置    │${NC}"
echo -e "${YELLOW}├─────────────────┼─────────────────────┼─────────────────────┤${NC}"
echo -e "${YELLOW}│ 项目前缀        │ [项目缩写]          │ ${PROJECT_PREFIX}                   │${NC}"
echo -e "${YELLOW}│ 容器名称        │ [前缀]_[服务名]     │ ${PROJECT_PREFIX}_frontend, ${PROJECT_PREFIX}_backend│${NC}"
echo -e "${YELLOW}│ 主机端口映射    │ 独一无二的主机端口  │ ${NGINX_PORT}:80 (Nginx)       │${NC}"
echo -e "${YELLOW}│ Docker网络      │ [前缀]_default      │ ${PROJECT_PREFIX}_default           │${NC}"
echo -e "${YELLOW}│ Docker卷        │ [前缀]_[数据名]     │ ${PROJECT_PREFIX}_nginx_data        │${NC}"
echo -e "${YELLOW}└─────────────────┴─────────────────────┴─────────────────────┘${NC}"

echo ""
if [ "$all_vars_ok" = true ]; then
    echo -e "${GREEN}🎊 SOP合规性检查通过！项目配置符合多项目部署防冲突规范${NC}"
    echo -e "${BLUE}📝 建议: 在服务器部署时确保端口 ${NGINX_PORT} 未被其他项目占用${NC}"
else
    echo -e "${RED}⚠️  发现配置问题，请根据检查结果进行调整${NC}"
fi

echo ""
echo -e "${BLUE}🔗 参考文档: [[SOP - 腾讯云项目部署流程]] 第2章 多项目部署防冲突规范${NC}"
echo -e "${BLUE}=================================================${NC}"