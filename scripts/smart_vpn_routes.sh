#!/bin/bash

# 智能VPN路由配置脚本
# 目的：让腾讯云服务直连，Docker Hub等走VPN

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌐 配置智能VPN路由...${NC}"

# 腾讯云相关域名/IP段 - 直连
TENCENT_DOMAINS=(
    "tencentcloudcr.com"
    "qcloud.com"
    "myqcloud.com"
    "tencent-cloud.net"
)

TENCENT_IP_RANGES=(
    "119.29.0.0/16"
    "129.28.0.0/16"
    "150.109.0.0/16"
    "162.14.0.0/16"
    "203.205.128.0/19"
)

# Docker Hub等需要VPN的域名
DOCKER_DOMAINS=(
    "docker.io"
    "registry-1.docker.io"
    "index.docker.io"
    "dseasb33srnrn.cloudfront.net"
    "production.cloudflare.docker.com"
)

# 获取当前默认网关
DEFAULT_GATEWAY=$(route -n get default | grep gateway | awk '{print $2}')
echo -e "${YELLOW}📍 当前默认网关: $DEFAULT_GATEWAY${NC}"

# 获取VPN网关（假设是utun接口）
VPN_INTERFACE=$(ifconfig | grep -E "utun[0-9]+" | grep "inet " | head -1 | awk '{print $1}' | sed 's/://')
if [ -n "$VPN_INTERFACE" ]; then
    echo -e "${YELLOW}🔗 发现VPN接口: $VPN_INTERFACE${NC}"
else
    echo -e "${RED}❌ 未发现活动的VPN接口${NC}"
    exit 1
fi

# 为腾讯云IP段添加直连路由
echo -e "${GREEN}📡 配置腾讯云直连路由...${NC}"
for ip_range in "${TENCENT_IP_RANGES[@]}"; do
    echo "  添加直连路由: $ip_range -> $DEFAULT_GATEWAY"
    sudo route add -net $ip_range $DEFAULT_GATEWAY 2>/dev/null || true
done

# 验证配置
echo -e "${GREEN}✅ 路由配置完成！${NC}"
echo -e "${YELLOW}📊 当前路由状态:${NC}"
netstat -rn | grep -E "(119\.29|129\.28|150\.109)" | head -5

echo ""
echo -e "${GREEN}🎯 配置建议:${NC}"
echo "1. 腾讯云服务现在会直连（速度快）"
echo "2. Docker Hub等仍走VPN（能正常拉取）"
echo "3. 可以正常构建和推送了！"

# 创建清理脚本
cat > /tmp/cleanup_smart_routes.sh << 'EOF'
#!/bin/bash
echo "清理智能路由配置..."
sudo route delete -net 119.29.0.0/16 2>/dev/null || true
sudo route delete -net 129.28.0.0/16 2>/dev/null || true
sudo route delete -net 150.109.0.0/16 2>/dev/null || true
sudo route delete -net 162.14.0.0/16 2>/dev/null || true
sudo route delete -net 203.205.128.0/19 2>/dev/null || true
echo "✅ 路由清理完成"
EOF

chmod +x /tmp/cleanup_smart_routes.sh
echo ""
echo -e "${YELLOW}📝 如需清理路由配置，运行: bash /tmp/cleanup_smart_routes.sh${NC}"