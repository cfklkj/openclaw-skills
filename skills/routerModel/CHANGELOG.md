# 更新日志

## [1.1.1] - 2026-02-19

### 修复
- 修复 select 命令无法生成按钮的问题
- 修改 select_models 输出格式为标准 JSON，包含 current_model 和 buttons 字段
- 移除不被识别的 [[[BUTTONS]]]...[[[/BUTTONS]]] 格式
- 方便 agent 解析并使用 message 工具发送正确的 inline buttons

---

## [1.1.0] - 2026-02-19

### 新增
- 添加 `select` 命令，支持交互式选择模型
- 列表输出 inline buttons，用户点击即可直接切换模型
- 显示当前使用的模型
- 支持按提供商过滤模型

### 改进
- 优化用户体验，简化模型切换流程

---

## [1.0.1] - 2026-02-19

### 修复
- 修复 `_init_provider` 方法中多余的 `config` 参数，导致添加提供商时 `apiKey`、`baseUrl` 参数位置错位
- 修复使用 `add` 快速添加时重复添加模型的问题（openrouter 下出现重复的 z-ai/glm4.7）

### 新增
- 添加版本号到 SKILL.md
- 创建 CHANGELOG.md 记录更新历史

---

## [1.0.0] - 初始版本

### 功能
- 添加提供商（add-provider）
- 删除提供商（delete-provider）
- 更新提供商配置（update-provider）
- 列出提供商（list-providers）
- 添加模型（add-model）
- 删除模型（delete-model）
- 列出模型（list-models）
- 快速添加提供商和模型（add）
- 应用模型为默认（model_apply.py）
