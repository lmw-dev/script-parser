module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // 类型枚举
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 新功能
        'fix',      // 修复
        'docs',     // 文档
        'style',    // 格式
        'refactor', // 重构
        'perf',     // 性能优化
        'test',     // 测试
        'chore',    // 构建/工具
        'ci',       // CI/CD
      ],
    ],
    // 范围枚举（可选，但如果有则必须是以下之一）
    'scope-enum': [
      1,
      'always',
      [
        'web',      // Web 应用
        'api',      // AI 协处理器 API
        'docker',   // Docker 配置
        'docs',     // 文档
        'config',   // 配置文件
      ],
    ],
    // 主题长度限制
    'subject-max-length': [2, 'always', 50],
    'subject-min-length': [2, 'always', 3],
    // 主题格式
    'subject-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    // 类型格式
    'type-case': [2, 'always', 'lower-case'],
    'type-empty': [2, 'never'],
    // 范围格式
    'scope-case': [2, 'always', 'lower-case'],
  },
};