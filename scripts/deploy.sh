#!/bin/bash

# ==================================================
# ScriptParser 统一部署脚本 v2.0
# ==================================================
# 用法:
#   ./deploy.sh build      - 构建并推送镜像到TCR
#   ./deploy.sh deploy     - 在服务器上部署或更新服务
#   ./deploy.sh status     - 检查服务状态
#   ./deploy.sh logs [service] - 查看服务日志
#   ./deploy.sh help       - 显示帮助信息

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="scriptparser"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="docker-compose.prod.yml"

# 环境变量检查和加载
load_env() {
    if [ -f "$PROJECT_ROOT/.env" ]; then
        echo -e "${BLUE}📋 加载环境变量...${NC}"
        set -a  # 自动导出所有变量
        source "$PROJECT_ROOT/.env"
        set +a
        echo -e "${GREEN}✅ 环境变量加载完成${NC}"
    else
        echo -e "${RED}❌ 未找到 .env 文件${NC}"
        echo -e "${YELLOW}💡 请先复制 .env.example 为 .env 并填入配置${NC}"
        exit 1
    fi
}

# 检查必需的环境变量
check_required_env() {
    local required_vars=("TCR_REGISTRY" "TCR_NAMESPACE")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo -e "${RED}❌ 缺少必需的环境变量:${NC}"
        printf '%s\n' "${missing_vars[@]}"
        exit 1
    fi
}

# 检查Docker是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker 未运行，请先启动 Docker${NC}"
        exit 1
    fi
}

# TCR登录
tcr_login() {
    echo -e "${BLUE}🔐 登录腾讯云TCR...${NC}"
    
    # 腾讯云个人版TCR固定地址
    local tcr_endpoint="$TCR_REGISTRY"
    
    # 检查是否已配置TCR凭证
    if [ -z "$TCR_USERNAME" ] || [ -z "$TCR_PASSWORD" ]; then
        echo -e "${YELLOW}⚠️  TCR凭证未配置，请确保Docker已通过其他方式登录TCR${NC}"
        echo -e "${YELLOW}💡 或在.env文件中设置 TCR_USERNAME 和 TCR_PASSWORD${NC}"
        echo -e "${YELLOW}💡 手动登录：docker login $tcr_endpoint${NC}"
    else
        echo "$TCR_PASSWORD" | docker login "$tcr_endpoint" -u "$TCR_USERNAME" --password-stdin
        echo -e "${GREEN}✅ TCR登录成功${NC}"
    fi
}

# 构建并推送镜像
build_and_push() {
    echo -e "${GREEN}🚀 开始构建 ScriptParser 项目${NC}"
    echo -e "${BLUE}=================================================${NC}"
    
    load_env
    check_required_env
    check_docker
    tcr_login
    
    # 构建镜像标记（腾讯云个人版TCR格式）
    local web_image="${TCR_REGISTRY}/${TCR_NAMESPACE}/${PROJECT_NAME}-web:latest"
    local coprocessor_image="${TCR_REGISTRY}/${TCR_NAMESPACE}/${PROJECT_NAME}-coprocessor:latest"
    
    echo -e "${YELLOW}📦 构建 Web 应用...${NC}"
    cd "$PROJECT_ROOT"
    docker build -t "${PROJECT_NAME}-web:latest" \
        --build-arg NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL}" \
        -f "./apps/web/Dockerfile" .
    
    echo -e "${YELLOW}🤖 构建 AI 协处理器...${NC}"
    docker build -t "${PROJECT_NAME}-coprocessor:latest" "./apps/coprocessor"
    
    echo -e "${YELLOW}🏷️  标记镜像...${NC}"
    docker tag "${PROJECT_NAME}-web:latest" "$web_image"
    docker tag "${PROJECT_NAME}-coprocessor:latest" "$coprocessor_image"
    
    echo -e "${YELLOW}📤 推送镜像到 TCR...${NC}"
    docker push "$web_image"
    docker push "$coprocessor_image"
    
    echo -e "${GREEN}✅ 镜像构建和推送完成${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${GREEN}🎉 构建完成！${NC}"
    echo -e "${YELLOW}镜像已推送到:${NC}"
    echo -e "  Web: $web_image"
    echo -e "  Coprocessor: $coprocessor_image"
}

# 服务器部署
deploy_to_server() {
    echo -e "${GREEN}🚀 开始服务器部署${NC}"
    echo -e "${BLUE}=================================================${NC}"
    
    load_env
    check_required_env
    check_docker
    
    cd "$PROJECT_ROOT"
    
    echo -e "${YELLOW}📥 拉取最新代码...${NC}"
    if [ -d ".git" ]; then
        git pull
        echo -e "${GREEN}✅ 代码更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  非Git仓库，跳过代码拉取${NC}"
    fi
    
    echo -e "${YELLOW}📦 拉取最新镜像...${NC}"
    docker-compose -f "$COMPOSE_FILE" pull
    echo -e "${GREEN}✅ 镜像拉取完成${NC}"
    
    echo -e "${YELLOW}🔄 重启服务...${NC}"
    docker-compose -f "$COMPOSE_FILE" up -d
    echo -e "${GREEN}✅ 服务启动完成${NC}"
    
    echo -e "${BLUE}⏳ 等待服务就绪...${NC}"
    sleep 10
    
    echo -e "${YELLOW}🏥 执行健康检查...${NC}"
    health_check
    
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${GREEN}🎉 部署完成！${NC}"
}

# 健康检查
health_check() {
    local all_healthy=true
    
    echo -e "${BLUE}🔍 检查服务健康状态...${NC}"
    
    # 检查容器状态
    local containers=$(docker-compose -f "$COMPOSE_FILE" ps -q)
    if [ -z "$containers" ]; then
        echo -e "${RED}❌ 未找到运行中的容器${NC}"
        return 1
    fi
    
    # 检查Nginx端口
    local nginx_port="${NGINX_PORT:-8081}"
    if curl -f -s "http://localhost:${nginx_port}/nginx-health" > /dev/null; then
        echo -e "${GREEN}✅ Nginx 健康检查通过 (端口 ${nginx_port})${NC}"
    else
        echo -e "${RED}❌ Nginx 健康检查失败 (端口 ${nginx_port})${NC}"
        all_healthy=false
    fi
    
    # 检查Web应用（通过Nginx代理）
    if curl -f -s "http://localhost:${nginx_port}/" > /dev/null; then
        echo -e "${GREEN}✅ Web应用 健康检查通过${NC}"
    else
        echo -e "${RED}❌ Web应用 健康检查失败${NC}"
        all_healthy=false
    fi
    
    # 检查AI协处理器（通过Nginx代理）
    if curl -f -s "http://localhost:${nginx_port}/api/health" > /dev/null; then
        echo -e "${GREEN}✅ AI协处理器 健康检查通过${NC}"
    else
        echo -e "${YELLOW}⚠️  AI协处理器 健康检查失败（可能尚未实现/health端点）${NC}"
    fi
    
    if [ "$all_healthy" = true ]; then
        echo -e "${GREEN}🎊 所有服务健康检查通过！${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  部分服务健康检查未通过${NC}"
        return 1
    fi
}

# 检查服务状态
check_status() {
    echo -e "${GREEN}📊 检查服务状态${NC}"
    echo -e "${BLUE}=================================================${NC}"
    
    load_env
    cd "$PROJECT_ROOT"
    
    echo -e "${YELLOW}🐳 Docker容器状态:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo -e "\n${YELLOW}📊 容器资源使用:${NC}"
    local containers=$(docker-compose -f "$COMPOSE_FILE" ps -q)
    if [ ! -z "$containers" ]; then
        docker stats --no-stream $containers
    else
        echo -e "${RED}❌ 未找到运行中的容器${NC}"
    fi
    
    echo -e "\n${YELLOW}🌐 端口监听状态:${NC}"
    local nginx_port="${NGINX_PORT:-8081}"
    if netstat -tuln | grep -q ":${nginx_port} "; then
        echo -e "${GREEN}✅ Nginx端口 ${nginx_port} 正在监听${NC}"
    else
        echo -e "${RED}❌ Nginx端口 ${nginx_port} 未监听${NC}"
    fi
    
    echo -e "\n${BLUE}=================================================${NC}"
    
    # 执行健康检查
    if health_check; then
        echo -e "${GREEN}🎊 服务状态良好！${NC}"
    else
        echo -e "${YELLOW}⚠️  服务可能存在问题${NC}"
    fi
}

# 查看日志
view_logs() {
    local service="$1"
    
    load_env
    cd "$PROJECT_ROOT"
    
    if [ -z "$service" ]; then
        echo -e "${YELLOW}📜 显示所有服务日志:${NC}"
        docker-compose -f "$COMPOSE_FILE" logs -f
    else
        echo -e "${YELLOW}📜 显示 ${service} 服务日志:${NC}"
        docker-compose -f "$COMPOSE_FILE" logs -f "$service"
    fi
}

# 显示帮助信息
show_help() {
    echo -e "${GREEN}ScriptParser 部署脚本 v2.0${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${YELLOW}用法:${NC}"
    echo -e "  ${GREEN}./deploy.sh build${NC}              - 构建并推送镜像到TCR"
    echo -e "  ${GREEN}./deploy.sh deploy${NC}             - 在服务器上部署或更新服务"
    echo -e "  ${GREEN}./deploy.sh status${NC}             - 检查服务状态和健康检查"
    echo -e "  ${GREEN}./deploy.sh logs [service]${NC}     - 查看服务日志"
    echo -e "  ${GREEN}./deploy.sh help${NC}               - 显示此帮助信息"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo -e "  ${BLUE}./deploy.sh build${NC}              # 本地构建并推送镜像"
    echo -e "  ${BLUE}./deploy.sh deploy${NC}             # 服务器端部署更新"
    echo -e "  ${BLUE}./deploy.sh logs web${NC}           # 查看web服务日志"
    echo -e "  ${BLUE}./deploy.sh logs${NC}               # 查看所有服务日志"
    echo ""
    echo -e "${YELLOW}注意事项:${NC}"
    echo -e "  • 确保项目根目录存在 .env 文件"
    echo -e "  • build 命令在本地开发机器上运行"
    echo -e "  • deploy 命令在生产服务器上运行"
    echo -e "  • 生产部署使用 docker-compose.prod.yml"
    echo -e "${BLUE}=================================================${NC}"
}

# 主函数
main() {
    case "${1:-help}" in
        build)
            build_and_push
            ;;
        deploy)
            deploy_to_server
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"