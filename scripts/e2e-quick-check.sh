#!/bin/bash

# TOM-499 E2E Quick Check Script
# 快速验证V3.0 MVP关键功能

set -e

echo "🧪 TOM-499 E2E Quick Check"
echo "==================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: 服务运行状态
echo "📋 检查 1: 服务运行状态"
echo "-----------------------------------"

WEB_RUNNING=$(ps aux | grep -E "next dev" | grep -v grep | wc -l)
API_RUNNING=$(ps aux | grep -E "uvicorn.*8000" | grep -v grep | wc -l)

if [ "$WEB_RUNNING" -gt 0 ]; then
  echo -e "${GREEN}✅ Web App (Next.js) 运行中${NC}"
else
  echo -e "${RED}❌ Web App 未运行${NC}"
  echo "   启动命令: cd apps/web && pnpm dev"
fi

if [ "$API_RUNNING" -gt 0 ]; then
  echo -e "${GREEN}✅ AI Coprocessor (FastAPI) 运行中${NC}"
else
  echo -e "${RED}❌ AI Coprocessor 未运行${NC}"
  echo "   启动命令: cd apps/coprocessor && python -m uvicorn app.main:app --reload --port 8000"
fi

echo ""

# Check 2: 环境变量配置
echo "📋 检查 2: 热词配置"
echo "-----------------------------------"

cd "$(dirname "$0")/.." # 回到项目根目录

if [ -f "apps/coprocessor/.env" ]; then
  HOTWORD_ID=$(grep "ALIYUN_TECH_HOTWORD_ID" apps/coprocessor/.env | cut -d'=' -f2)
  if [ -n "$HOTWORD_ID" ]; then
    echo -e "${GREEN}✅ 热词ID已配置: ${HOTWORD_ID:0:12}...${NC}"
  else
    echo -e "${RED}❌ 热词ID未配置${NC}"
  fi
else
  echo -e "${RED}❌ .env 文件不存在${NC}"
fi

echo ""

# Check 3: 关键代码文件检查
echo "📋 检查 3: 关键代码验证"
echo "-----------------------------------"

# Check 3.1: resetPartial() 使用
if grep -q "resetPartial()" apps/web/src/app/result/page.tsx; then
  echo -e "${GREEN}✅ result/page.tsx 使用 resetPartial()${NC}"
else
  echo -e "${RED}❌ result/page.tsx 未使用 resetPartial()${NC}"
fi

# Check 3.2: 分析模式选择器
if grep -q "analysis_mode" apps/web/src/stores/app-store.ts; then
  echo -e "${GREEN}✅ app-store.ts 包含 analysisMode 状态${NC}"
else
  echo -e "${RED}❌ app-store.ts 缺少 analysisMode${NC}"
fi

# Check 3.3: 热词路由逻辑
if grep -q "vocabulary_id" apps/coprocessor/app/services/asr_service.py; then
  echo -e "${GREEN}✅ asr_service.py 包含热词注入逻辑${NC}"
else
  echo -e "${RED}❌ asr_service.py 缺少热词逻辑${NC}"
fi

# Check 3.4: LLM Track Router
if [ -f "apps/coprocessor/app/services/llm_track_router.py" ]; then
  echo -e "${GREEN}✅ llm_track_router.py 文件存在${NC}"
else
  echo -e "${RED}❌ llm_track_router.py 文件缺失${NC}"
fi

echo ""

# Check 4: API健康检查
echo "📋 检查 4: API健康检查"
echo "-----------------------------------"

if command -v curl &> /dev/null; then
  API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null || echo "000")
  
  if [ "$API_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ AI Coprocessor API 健康 (HTTP 200)${NC}"
  else
    echo -e "${YELLOW}⚠️  AI Coprocessor API 响应异常 (HTTP $API_HEALTH)${NC}"
  fi
else
  echo -e "${YELLOW}⚠️  curl 未安装，跳过API检查${NC}"
fi

echo ""

# Summary
echo "==================================="
echo "🏁 快速检查完成"
echo ""
echo "📝 下一步操作："
echo "   1. 打开浏览器访问: http://localhost:3000"
echo "   2. 参考测试报告: docs/testing/TOM-499-E2E-Test-Execution-Report.md"
echo "   3. 执行5个E2E测试路径"
echo ""
echo "🔗 Linear Issue: https://linear.app/tomorrow-persistence/issue/TOM-499"
echo "==================================="
