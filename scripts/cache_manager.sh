#!/bin/bash

# Docker缓存管理脚本
# 为OpenVPN环境提供完整的缓存策略解决方案

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${CYAN}🎛️  Docker缓存管理系统${NC}"
echo -e "${YELLOW}📁 项目目录: $PROJECT_ROOT${NC}"
echo ""

# 检查VPN状态
check_vpn_status() {
    if ifconfig | grep -q "utun.*inet.*10\."; then
        echo -e "${GREEN}✅ OpenVPN已连接${NC}"
        return 0
    else
        echo -e "${RED}❌ OpenVPN未连接${NC}"
        return 1
    fi
}

# 显示缓存状态
show_cache_status() {
    echo -e "${BLUE}📊 Docker缓存状态${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 项目关键镜像
    local key_images=("python:3.12-slim" "node:20-alpine" "nginx:alpine")
    echo -e "${PURPLE}🔑 关键基础镜像:${NC}"
    
    for img in "${key_images[@]}"; do
        if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${img}$"; then
            local size=$(docker images --format "{{.Size}}" "$img")
            echo -e "  ${GREEN}✓${NC} $img ($size)"
        else
            echo -e "  ${RED}✗${NC} $img (缺失)"
        fi
    done
    
    echo ""
    
    # 项目构建的镜像
    echo -e "${PURPLE}🚀 项目镜像:${NC}"
    docker images --filter "reference=*scriptparser*" --format "  ✓ {{.Repository}}:{{.Tag}} ({{.Size}})" 2>/dev/null || echo "  暂无项目镜像"
    
    echo ""
    
    # 存储使用情况
    echo -e "${PURPLE}💾 存储使用情况:${NC}"
    docker system df --format "table {{.Type}}\t{{.Total}}\t{{.Active}}\t{{.Size}}\t{{.Reclaimable}}" | sed 's/^/  /'
    
    echo ""
}

# 清理不必要的镜像
cleanup_images() {
    echo -e "${YELLOW}🧹 清理Docker镜像...${NC}"
    
    # 清理悬挂镜像
    echo "清理悬挂镜像..."
    docker image prune -f
    
    # 清理未使用的镜像（谨慎）
    read -p "是否清理未使用的镜像？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker image prune -a -f
    fi
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 预缓存策略
precache_strategy() {
    echo -e "${BLUE}🎯 预缓存策略选择${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. 快速缓存（仅项目必需镜像）"
    echo "2. 完整缓存（常用开发镜像）"  
    echo "3. 自定义缓存"
    echo "4. 返回主菜单"
    echo ""
    
    read -p "请选择 (1-4): " -n 1 -r choice
    echo ""
    
    case $choice in
        1)
            echo -e "${GREEN}🚀 执行快速缓存...${NC}"
            cache_critical_images
            ;;
        2)
            echo -e "${GREEN}🚀 执行完整缓存...${NC}"
            "$SCRIPT_DIR/precache_images.sh"
            ;;
        3)
            echo -e "${GREEN}🚀 自定义缓存...${NC}"
            custom_cache
            ;;
        4)
            return
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
}

# 缓存关键镜像
cache_critical_images() {
    local images=("python:3.12-slim" "nginx:alpine")
    
    echo -e "${BLUE}📥 缓存关键镜像...${NC}"
    
    if ! check_vpn_status; then
        echo -e "${RED}⚠️  建议连接VPN以获得更好的下载速度${NC}"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    for img in "${images[@]}"; do
        if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${img}$"; then
            echo -e "${GREEN}✓${NC} $img (已存在)"
        else
            echo -e "${YELLOW}📥 拉取: $img${NC}"
            if docker pull "$img"; then
                echo -e "${GREEN}✅ 成功: $img${NC}"
            else
                echo -e "${RED}❌ 失败: $img${NC}"
            fi
        fi
    done
}

# 自定义缓存
custom_cache() {
    echo -e "${BLUE}🎨 自定义镜像缓存${NC}"
    echo "请输入要缓存的镜像名称（一行一个），输入空行结束："
    
    local custom_images=()
    while IFS= read -r line; do
        if [ -z "$line" ]; then
            break
        fi
        custom_images+=("$line")
    done
    
    if [ ${#custom_images[@]} -eq 0 ]; then
        echo "没有输入镜像，返回主菜单"
        return
    fi
    
    echo -e "${BLUE}将要缓存的镜像:${NC}"
    for img in "${custom_images[@]}"; do
        echo "  - $img"
    done
    
    read -p "确认缓存？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        return
    fi
    
    for img in "${custom_images[@]}"; do
        echo -e "${YELLOW}📥 拉取: $img${NC}"
        if docker pull "$img"; then
            echo -e "${GREEN}✅ 成功: $img${NC}"
        else
            echo -e "${RED}❌ 失败: $img${NC}"
        fi
    done
}

# 构建管理
build_management() {
    echo -e "${BLUE}🏗️  构建管理${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. 智能构建（检查缓存后构建）"
    echo "2. 强制重新构建"
    echo "3. 仅构建Web应用"
    echo "4. 仅构建AI协处理器" 
    echo "5. 返回主菜单"
    echo ""
    
    read -p "请选择 (1-5): " -n 1 -r choice
    echo ""
    
    case $choice in
        1)
            echo -e "${GREEN}🚀 执行智能构建...${NC}"
            "$SCRIPT_DIR/smart_build.sh"
            ;;
        2)
            echo -e "${GREEN}🚀 执行强制重建...${NC}"
            "$SCRIPT_DIR/deploy.sh" build
            ;;
        3)
            echo -e "${GREEN}🚀 构建Web应用...${NC}"
            "$SCRIPT_DIR/smart_build.sh" web
            ;;
        4)
            echo -e "${GREEN}🚀 构建AI协处理器...${NC}"
            "$SCRIPT_DIR/smart_build.sh" ai
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
}

# 网络诊断
network_diagnosis() {
    echo -e "${BLUE}🔍 网络诊断${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # VPN状态
    echo -e "${PURPLE}VPN状态:${NC}"
    check_vpn_status
    
    # Docker Registry连通性
    echo -e "${PURPLE}Docker Registry连通性:${NC}"
    echo -n "Docker Hub: "
    if timeout 5 docker search --limit 1 hello-world >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 可访问${NC}"
    else
        echo -e "${RED}❌ 访问困难${NC}"
    fi
    
    echo -n "腾讯云TCR: "
    if timeout 5 curl -s https://ccr.ccs.tencentyun.com >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 可访问${NC}"
    else
        echo -e "${RED}❌ 访问困难${NC}"
    fi
    
    # 镜像加速器测试
    echo -e "${PURPLE}镜像加速器状态:${NC}"
    if [ -f "/etc/docker/daemon.json" ]; then
        echo "已配置镜像加速器"
        cat /etc/docker/daemon.json | jq -r '.["registry-mirrors"][]' 2>/dev/null | sed 's/^/  - /' || echo "  - 配置文件格式错误"
    else
        echo -e "${YELLOW}⚠️  未配置镜像加速器${NC}"
    fi
    
    echo ""
}

# 显示帮助
show_help() {
    echo -e "${CYAN}📖 Docker缓存管理系统帮助${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${PURPLE}🎯 核心功能:${NC}"
    echo "• 缓存状态监控和管理"
    echo "• 智能预缓存策略"
    echo "• VPN环境优化构建"
    echo "• 网络连通性诊断"
    echo ""
    echo -e "${PURPLE}💡 使用建议:${NC}"
    echo "1. 连接VPN后先执行预缓存"
    echo "2. 断开VPN后使用缓存进行构建"
    echo "3. 定期清理无用镜像释放空间"
    echo ""
    echo -e "${PURPLE}🚀 工作流程:${NC}"
    echo "VPN连接 → 预缓存镜像 → VPN断开 → 智能构建 → 推送到TCR"
    echo ""
}

# 主菜单
show_main_menu() {
    while true; do
        echo -e "${CYAN}🎛️  Docker缓存管理主菜单${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "1. 查看缓存状态"
        echo "2. 预缓存策略"
        echo "3. 构建管理"
        echo "4. 清理镜像"
        echo "5. 网络诊断"
        echo "6. 帮助信息"
        echo "7. 退出"
        echo ""
        
        read -p "请选择功能 (1-7): " -n 1 -r choice
        echo ""
        
        case $choice in
            1)
                show_cache_status
                ;;
            2)
                precache_strategy
                ;;
            3)
                build_management
                ;;
            4)
                cleanup_images
                ;;
            5)
                network_diagnosis
                ;;
            6)
                show_help
                ;;
            7)
                echo -e "${GREEN}👋 再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选择，请重新输入${NC}"
                ;;
        esac
        
        echo ""
        echo -e "${YELLOW}按任意键返回主菜单...${NC}"
        read -n 1
        clear
    done
}

# 检查Docker是否运行
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker未运行，请先启动Docker${NC}"
    exit 1
fi

# 启动主菜单
clear
show_main_menu