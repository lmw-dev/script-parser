# 代码规范配置备忘录

> 创建时间: 2025-09-16  
> 项目: ScriptParser  
> 配置原则: 简洁实用，不过度严格

## 📋 配置概览

本项目采用简化的代码规范配置，专注于保持代码一致性而不影响开发效率。

### 🎯 设计原则

1. **简洁优先** - 避免过度复杂的配置
2. **语言分离** - 每种技术栈使用专门的工具
3. **就近原则** - 配置文件放在对应的应用目录中
4. **独立开发友好** - 不强制严格的提交规范

## 📁 配置文件分布

### 根目录配置

```
script-parser/
├── .editorconfig          # 统一编辑器设置
├── .gitignore            # Git 忽略文件
├── .gitmessage           # Git 提交消息模板
├── commitlint.config.js  # Commitlint 配置
├── .husky/               # Git 钩子
│   └── commit-msg        # 提交信息检查钩子
└── scripts/format.sh     # 代码格式化脚本
```

### Web 应用配置 (`apps/web/`)

```
apps/web/
├── .eslintrc.json        # ESLint 代码检查
├── .prettierrc.json      # Prettier 代码格式化
└── package.json          # 脚本和依赖
```

### AI 协处理器配置 (`apps/coprocessor/`)

```
apps/coprocessor/
├── pyproject.toml        # Ruff 配置
├── requirements.txt      # Python 依赖
└── .env.example         # 环境变量模板
```

## ⚙️ 详细配置

### 1. EditorConfig (`.editorconfig`)

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{js,jsx,ts,tsx,json,yml,yaml}]
indent_style = space
indent_size = 2

[*.py]
indent_style = space
indent_size = 4

[*.md]
trim_trailing_whitespace = false
```

**作用**: 统一不同编辑器的基础设置

### 2. Web 应用 - Prettier (`.prettierrc.json`)

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

**作用**: 自动格式化 JavaScript/TypeScript 代码

### 3. Web 应用 - ESLint (`.eslintrc.json`)

```json
{
  "extends": ["next/core-web-vitals"],
  "rules": {
    "prefer-const": "warn",
    "no-unused-vars": "warn",
    "no-console": "warn"
  },
  "ignorePatterns": [
    ".next/**",
    "out/**",
    "build/**",
    "dist/**",
    "node_modules/**"
  ]
}
```

**作用**: 检查代码质量，基于 Next.js 推荐配置

### 4. AI 协处理器 - Ruff (`pyproject.toml`)

```toml
[tool.ruff]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

ignore = [
    "E501",  # 行长度限制
    "B008",  # 函数调用中的默认参数
    "C901",  # 复杂度检查
]

line-length = 88
target-version = "py312"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"
```

**作用**: Python 代码检查和格式化

### 5. Commit Message 规范 (Conventional Commits)

#### 5.1 格式

```
<type>(<scope>): <subject>
```

#### 5.2 Type 类型

- **feat**: 新功能
- **fix**: 修复 bug
- **docs**: 文档更新
- **style**: 代码格式调整（不影响代码运行的变动）
- **refactor**: 重构（既不是新增功能，也不是修复 bug 的代码变动）
- **perf**: 性能优化
- **test**: 增加测试
- **chore**: 构建过程或辅助工具的变动
- **ci**: CI/CD 相关变更

#### 5.3 Scope 范围（可选）

- **web**: Web 应用相关
- **api**: AI 协处理器 API 相关
- **docker**: Docker 配置相关
- **docs**: 文档相关
- **config**: 配置文件相关

#### 5.4 Subject 主题

- **必须**使用动词原形的小写字母开头
- **禁止**首字母大写，**禁止**结尾加句号
- 简洁描述变更内容（≤50 字符）

#### 5.5 示例

**正确示例**:
```bash
feat(api): add user authentication endpoint
fix(web): resolve routing issue in navigation
docs: update deployment guide
style(web): format code with prettier
refactor(api): optimize database queries
chore(docker): update nginx configuration
```

**错误示例**:
```bash
feat(api): Added user authentication endpoint.  # 首字母大写 + 句号
Fix: routing issue                             # 首字母大写
add new feature                                # 缺少 type
```

#### 5.6 自动检查 (Commitlint)

项目集成了 Commitlint 自动检查提交信息格式：

**配置文件**: `commitlint.config.js`
**Git 钩子**: `.husky/commit-msg`

**自动检查规则**:
- 提交类型必须是预定义的类型之一
- 范围（如果提供）必须是预定义的范围之一
- 主题必须小写字母开头，不能为空，不能以句号结尾
- 主题长度限制在 3-50 字符之间

**测试命令**:
```bash
# 测试提交信息格式
echo "feat(api): add user authentication" | npx commitlint  # ✅ 通过
echo "invalid commit message" | npx commitlint             # ❌ 失败
```

#### 5.7 Git 提交模板

项目提供了 `.gitmessage` 模板文件，可以通过以下命令设置：

```bash
# 设置提交模板（可选）
git config commit.template .gitmessage
```

设置后，每次 `git commit` 时会自动显示模板和规范说明。

## 🚀 使用命令

### 根目录命令

```bash
# 开发
pnpm dev:web                # 启动 Web 应用
pnpm build:web             # 构建 Web 应用

# Docker
pnpm docker:up             # 启动 Docker 服务
pnpm docker:down           # 停止 Docker 服务
pnpm docker:build          # 构建 Docker 镜像

# 格式化
./scripts/format.sh        # 格式化所有代码

# 提交检查
npx commitlint --from HEAD~1 --to HEAD  # 检查最近一次提交
echo "feat: add new feature" | npx commitlint  # 测试提交信息格式
```

### Web 应用命令

```bash
cd apps/web

# 开发
pnpm dev                   # 启动开发服务器
pnpm build                 # 构建生产版本

# 代码质量
pnpm lint                  # ESLint 检查
pnpm format                # Prettier 格式化
pnpm format:check          # 检查格式化状态
```

### AI 协处理器命令

```bash
cd apps/coprocessor

# Python 环境
python3 -m venv .venv      # 创建虚拟环境
source .venv/bin/activate  # 激活虚拟环境
pip install -r requirements.txt  # 安装依赖

# 代码质量
ruff check .               # 检查代码
ruff check --fix .         # 自动修复
ruff format .              # 格式化代码

# 运行服务
python -m uvicorn app.main:app --reload --port 8000
```

## ✅ 验证测试

### 测试结果

1. **EditorConfig**: ✅ 正常工作
2. **Prettier**: ✅ 格式化成功
3. **ESLint**: ✅ 检查通过（仅源代码）
4. **Ruff**: ✅ 检查和格式化正常
5. **格式化脚本**: ✅ 统一格式化成功
6. **Commit 规范**: ✅ 已定义标准格式
7. **Commitlint**: ✅ 自动检查正常工作

### 测试命令

```bash
# Web 应用测试
cd apps/web
pnpm lint                  # 无错误
pnpm format:check          # 格式正确
pnpm format                # 格式化成功

# AI 协处理器测试
cd apps/coprocessor
ruff check .               # 少量警告（可接受）
ruff format .              # 格式化成功

# 统一格式化测试
./scripts/format.sh        # 全部成功
```

## 🎯 配置特点

### 优势

1. **简洁实用** - 配置文件少而精
2. **技术分离** - 不同语言使用专门工具
3. **开发友好** - 规则宽松，专注核心问题
4. **维护简单** - 无复杂的 Git 钩子和全局配置
5. **提交规范** - 统一的 Commit Message 格式

### 适用场景

- ✅ 独立开发项目
- ✅ 小团队协作
- ✅ 快速原型开发
- ✅ MVP 项目

### 不适用场景

- ❌ 大型团队项目（需要更严格的规范）
- ❌ 企业级项目（需要完整的 CI/CD 集成）
- ❌ 开源项目（需要贡献者规范）

## 📝 维护说明

### 定期检查

1. **依赖更新** - 定期更新 Prettier、ESLint、Ruff 版本
2. **规则调整** - 根据项目发展调整规则严格程度
3. **工具升级** - 关注新工具和最佳实践

### 扩展建议

如果项目规模扩大，可以考虑添加：

- **Husky** - Git 钩子自动化
- **lint-staged** - 暂存区代码检查
- **Commitlint** - 提交信息规范
- **CI/CD 集成** - 自动化检查和部署

## 🔗 相关文档

- [Prettier 配置文档](https://prettier.io/docs/en/configuration.html)
- [ESLint 配置文档](https://eslint.org/docs/user-guide/configuring/)
- [Ruff 配置文档](https://docs.astral.sh/ruff/configuration/)
- [EditorConfig 文档](https://editorconfig.org/)

---

**备注**: 本配置适用于 ScriptParser 项目的当前阶段，随着项目发展可能需要调整。