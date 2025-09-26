#!/bin/bash

# 智能Docker构建脚本 - 支持缓存优先构建
# 专门为OpenVPN环境和腾讯云TCR优化

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}🚀 智能Docker构建系统${NC}"
echo -e "${YELLOW}📍 项目目录: $PROJECT_ROOT${NC}"

# 检查环境
check_environment() {
    echo -e "${BLUE}🔍 环境检查...${NC}"
    
    # 检查Docker
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker未运行${NC}"
        exit 1
    fi
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ 未找到.env文件${NC}"
        exit 1
    fi
    
    # 加载环境变量
    source .env
    
    # 检查TCR环境变量
    if [ -z "$TCR_REGISTRY" ] || [ -z "$TCR_NAMESPACE" ]; then
        echo -e "${RED}❌ 缺少TCR配置环境变量${NC}"
        echo -e "${YELLOW}💡 请确保.env文件包含: TCR_REGISTRY, TCR_NAMESPACE${NC}"
        exit 1
    fi
    
    # 设置兼容变量
    REGISTRY_HOST="$TCR_REGISTRY"
    REGISTRY_NAMESPACE="$TCR_NAMESPACE"
    
    # 检测VPN状态
    VPN_CONNECTED=false
    if ifconfig | grep -q "utun.*inet.*10\."; then
        VPN_CONNECTED=true
        echo -e "${GREEN}✅ 检测到OpenVPN连接${NC}"
    else
        echo -e "${YELLOW}⚠️  未检测到VPN连接${NC}"
    fi
    
    echo -e "${GREEN}✅ 环境检查完成${NC}"
    echo ""
}

# 检查基础镜像缓存
check_base_images() {
    local mode=$1
    echo -e "${BLUE}🏦️  检查基础镜像缓存...${NC}"
    
    local missing_images=()
    local base_images=()
    
    # 根据构建目标选择需要的基础镜像
    case "$mode" in
        "web")
            base_images=("node:18-alpine")
            ;;
        "coprocessor"|"ai")
            base_images=("python:3.12-slim")
            ;;
        "all"|*)
            base_images=("python:3.12-slim" "node:18-alpine")
            ;;
    esac
    
    for img in "${base_images[@]}"; do
        if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${img}$"; then
            missing_images+=("$img")
        else
            echo -e "${GREEN}✓${NC} $img"
        fi
    done
    
    if [ ${#missing_images[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  缺少基础镜像:${NC}"
        for img in "${missing_images[@]}"; do
            echo -e "${RED}  ✗${NC} $img"
        done
        
        if [ "$VPN_CONNECTED" = true ]; then
            echo ""
            read -p "是否现在拉取缺失的基础镜像？(Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                pull_missing_images "${missing_images[@]}"
            fi
        else
            echo -e "${RED}❌ 没有VPN连接，无法拉取镜像。请先连接VPN或运行预缓存脚本${NC}"
            echo -e "${YELLOW}💡 运行: ./scripts/precache_images.sh${NC}"
            exit 1
        fi
    fi
    echo ""
}

# 拉取缺失镜像
pull_missing_images() {
    local images=("$@")
    echo -e "${BLUE}📥 拉取缺失的基础镜像...${NC}"
    
    for img in "${images[@]}"; do
        echo -e "${YELLOW}拉取: $img${NC}"
        if docker pull "$img"; then
            echo -e "${GREEN}✅ 成功: $img${NC}"
        else
            echo -e "${RED}❌ 失败: $img${NC}"
            echo -e "${YELLOW}💡 建议: 检查网络连接或稍后重试${NC}"
            exit 1
        fi
    done
}

# 构建函数
build_image() {
    local service=$1
    local dockerfile=$2
    local context=$3
    local tag_name="$REGISTRY_HOST/$REGISTRY_NAMESPACE/scriptparser-${service}:latest"
    
    echo -e "${PURPLE}🔨 构建 $service 镜像...${NC}"
    echo -e "${YELLOW}📂 构建上下文: $context${NC}"
    echo -e "${YELLOW}🏷️  镜像标签: $tag_name${NC}"
    
    # 使用buildx进行多平台构建
    if docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --push \
        -f "$dockerfile" \
        -t "$tag_name" \
        "$context"; then
        echo -e "${GREEN}✅ $service 构建并推送成功${NC}"
        return 0
    else
        echo -e "${RED}❌ $service 构建失败${NC}"
        return 1
    fi
}

# 主构建流程
main() {
    local mode=${1:-"all"}
    
    check_environment
    check_base_images "$mode"
    
    echo -e "${GREEN}🏦️  开始构建流程...${NC}"
    
    local success_count=0
    local total_count=0
    
    case "$mode" in
        "web")
            echo -e "${BLUE}🌐 构建Web应用...${NC}"
            total_count=1
            if build_image "web" "apps/web/Dockerfile" "."; then
                success_count=$((success_count + 1))
            fi
            ;;
        "coprocessor"|"ai")
            echo -e "${BLUE}🤖 构建AI协处理器...${NC}"
            total_count=1
            if build_image "coprocessor" "apps/coprocessor/Dockerfile" "."; then
                success_count=$((success_count + 1))
            fi
            ;;
        "all"|*)
            echo -e "${BLUE}🔄 构建所有服务...${NC}"
            total_count=2
            
            if build_image "web" "apps/web/Dockerfile" "."; then
                success_count=$((success_count + 1))
            fi
            
            if build_image "coprocessor" "apps/coprocessor/Dockerfile" "."; then
                success_count=$((success_count + 1))
            fi
            ;;
    esac
    
    # 构建报告
    echo ""
    echo -e "${GREEN}📊 构建报告${NC}"
    echo -e "成功: ${success_count}/${total_count}"
    
    if [ $success_count -eq $total_count ]; then
        echo -e "${GREEN}🎉 所有镜像构建成功！${NC}"
        
        # 验证推送结果
        echo -e "${BLUE}🔍 验证推送结果...${NC}"
        echo "Web镜像: $REGISTRY_HOST/$REGISTRY_NAMESPACE/scriptparser-web:latest"
        echo "AI协处理器: $REGISTRY_HOST/$REGISTRY_NAMESPACE/scriptparser-coprocessor:latest"
        
        return 0
    else
        echo -e "${RED}❌ 部分镜像构建失败${NC}"
        return 1
    fi
}

# 显示帮助
show_help() {
    echo "智能Docker构建脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  all          构建所有镜像（默认）"
    echo "  web          只构建Web应用"
    echo "  coprocessor  只构建AI协处理器"
    echo "  ai           同 coprocessor"
    echo "  -h, --help   显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0           # 构建所有镜像"
    echo "  $0 web       # 只构建Web应用"
    echo "  $0 ai        # 只构建AI协处理器"
}

# 参数处理
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$1"
        ;;
esac