#!/usr/bin/env python3
"""
TOM-490 热词配置验证脚本
用于验证 ALIYUN_TECH_HOTWORD_ID 环境变量是否正确配置

使用方法:
    python verify_hotword_config.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# 检查热词ID配置
hotword_id = os.getenv("ALIYUN_TECH_HOTWORD_ID")

print("=" * 70)
print("🔍 TOM-490: 阿里云热词配置验证")
print("=" * 70)
print()

# 检查配置状态
if not hotword_id:
    print("❌ 配置失败: ALIYUN_TECH_HOTWORD_ID 未设置或为空")
    print()
    print("请在 .env 文件中添加以下配置:")
    print("   ALIYUN_TECH_HOTWORD_ID=your_vocabulary_id_here")
    print()
    sys.exit(1)

if hotword_id == "your_vocabulary_id_here":
    print("⚠️  配置已添加，但仍为占位符值")
    print(f"   当前值: {hotword_id}")
    print()
    print("📋 下一步操作:")
    print()
    print("   步骤 1️⃣: 访问阿里云控制台")
    print("      https://nls-portal.console.aliyun.com/")
    print()
    print("   步骤 2️⃣: 创建业务专属热词表")
    print("      - 导航: 自学习平台 → 热词")
    print("      - 点击「创建热词表」")
    print("      - 命名: tech_vocab_v1_2025")
    print("      - 类型: 业务专属热词表")
    print()
    print("   步骤 3️⃣: 导入科技术语")
    print("      - 打开: app/assets/tech_vocab_v1.json")
    print("      - 导入 248 个科技术语到热词表")
    print()
    print("   步骤 4️⃣: 获取热词表ID")
    print("      - 在热词表列表中找到刚创建的表")
    print("      - 复制「热词表ID」(vocabulary_id)")
    print()
    print("   步骤 5️⃣: 更新配置")
    print("      - 编辑 .env 文件")
    print("      - 替换 ALIYUN_TECH_HOTWORD_ID 的值")
    print("      - 重新运行此脚本验证")
    print()
    print("=" * 70)
    sys.exit(0)

# 配置成功
print("✅ 配置成功！")
print()
print(f"   热词表ID: {hotword_id}")
print()
print("🎉 配置验证通过！")
print()
print("📝 下一步:")
print("   - 可以开始编码实现 TOM-490")
print("   - 或者运行集成测试验证热词效果")
print()
print("=" * 70)
sys.exit(0)

