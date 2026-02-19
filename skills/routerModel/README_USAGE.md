# Router Model 技能 - 使用指南

## 技能概览

`routerModel` 技能提供了一套完整的 OpenClaw 模型管理解决方案，直接管理 `~/.openclaw/openclaw.json`：

- ✅ 添加、更新、删除提供商和模型
- ✅ 列出所有提供商和模型
- ✅ 切换默认模型
- ✅ 无需额外配置文件

**重要**: 本技能直接操作 OpenClaw 主配置文件，所有修改立即生效。

## 目录结构

```
routerModel-skill/
├── SKILL.md                    # 技能主文件（AI 代理读取）
├── README_USAGE.md            # 本使用指南
└── scripts/
    ├── model_manager.py       # 模型管理脚本
    └── model_apply.py         # 模型应用脚本
```

## 快速示例

### 1. 快速添加 NVIDIA 模型

```bash
cd "H:\tzj\pro2026\插件规划\2月\19\routerModel-skill\scripts"
python model_manager.py add --provider nvidia --api-key "nvapi-your-key" --model-name "nvidia/nemotron-3-nano-30b-a3b" --base-url "https://integrate.api.nvidia.com/v1"
```

输出：
```
✓ 提供商添加成功
  名称: nvidia
  API密钥: nvapi-you...
  Base URL: https://integrate.api.nvidia.com/v1
  API类型: openai-completions
✓ 模型添加成功
  提供商: nvidia
  模型ID: nvidia/nemotron-3-nano-30b-a3b
```

### 2. 查看所有提供商

```bash
python model_manager.py list-providers
```

输出：
```
提供商          Base URL                                          API密钥前缀
---------------------------------------------------------------------------------------
nvidia          https://integrate.api.nvidia.com/v1             nvapi-you...

总计: 1 个提供商
```

### 3. 查看所有模型

```bash
python model_manager.py list-models
```

输出：
```
提供商       模型ID                                        名称
----------------------------------------------------------------------------------------------------
nvidia       nvidia/nemotron-3-nano-30b-a3b               nvidia/nemotron-3-nano-30b-a3b

总计: 1 个模型，1 个提供商
```

### 4. 应用模型为默认

```bash
python model_apply.py apply "nvidia/nemotron-3-nano-30b-a3b"
```

或使用模糊匹配：
```bash
python model_apply.py apply "nemotron"
```

输出：
```
将要应用的模型：
  提供商: nvidia
  模型ID: nvidia/nemotron-3-nano-30b-a3b
  模型名称: nvidia/nemotron-3-nano-30b-a3b

✓ 已设置默认模型: nvidia/nemotron-3-nano-30b-a3b

提示：修改已生效，但正在运行的会话可能需要重启才能使用新模型
重启命令: openclaw gateway restart
```

### 5. 查看当前默认模型

```bash
python model_apply.py current
```

### 6. 搜索特定提供商的模型

```bash
python model_manager.py list-models --provider nvidia
```

## 完整命令参考

### model_manager.py

#### 提供商管理

```bash
# 快速添加（提供商 + 模型）
python model_manager.py add --provider <提供商> --api-key <密钥> --model-name <模型ID> [--base-url <端点>]

# 添加提供商
python model_manager.py add-provider --name <提供商> --api-key <密钥> [--base-url <端点>]

# 列出所有提供商
python model_manager.py list-providers

# 更新提供商
python model_manager.py update-provider --name <提供商> [--api-key <新密钥>] [--base-url <新端点>]

# 删除提供商及其所有模型
python model_manager.py delete-provider --name <提供商>
```

#### 模型管理

```bash
# 添加模型
python model_manager.py add-model --provider <提供商> --id <模型ID> [--name <名称>] [--context-window <大小>] [--max-tokens <数量>]

# 列出所有模型
python model_manager.py list-models

# 列出特定提供商的模型
python model_manager.py list-models --provider <提供商>

# 删除模型
python model_manager.py delete-model --provider <提供商> --id <模型ID>
```

### model_apply.py

```bash
# 应用模型为默认
python model_apply.py apply <模型ID>

# 应用模型（模糊匹配）
python model_apply.py apply "nemotron"

# 预览应用（不实际执行）
python model_apply.py apply <模型ID> --dry-run

# 列出所有可用模型
python model_apply.py list

# 获取当前默认模型
python model_apply.py current

# 列出会话配置
python model_apply.py session
```

## 支持的模型提供商示例

### NVIDIA

```bash
python model_manager.py add --provider nvidia --api-key "nvapi-xxx" --model-name "nvidia/nemotron-3-nano-30b-a3b" --base-url "https://integrate.api.nvidia.com/v1"
```

### OpenAI

```bash
python model_manager.py add --provider openai --api-key "sk-xxx" --model-name "gpt-4" --base-url "https://api.openai.com/v1"
```

### Anthropic

```bash
python model_manager.py add --provider anthropic --api-key "sk-ant-xxx" --model-name "claude-3-opus-20240229"
```

### 自定义端点

```bash
python model_manager.py add --provider custom --api-key "your-key" --model-name "your/model" --base-url "https://your-endpoint.com/v1"
```

## 工作流程示例

### 场景1：从头开始配置新提供商

```bash
# 1. 添加提供商
python model_manager.py add-provider --name myprovider --api-key "your-api-key"

# 2. 添加多个模型
python model_manager.py add-model --provider myprovider --id "myprovider/model-1"
python model_manager.py add-model --provider myprovider --id "myprovider/model-2"

# 3. 设置默认模型
python model_apply.py apply "myprovider/model-1"

# 4. 重启 OpenClaw 使更改生效
openclaw gateway restart
```

### 场景2：快速测试新模型

```bash
# 一键添加并应用
python model_manager.py add --provider test --api-key "test-key" --model-name "test/model"
python model_apply.py apply "test/model"
```

### 场景3：更新API密钥

```bash
# 查看当前提供商列表
python model_manager.py list-providers

# 更新API密钥
python model_manager.py update-provider --name nvidia --api-key "new-api-key"
```

### 场景4：清理不需要的模型

```bash
# 删除单个模型
python model_manager.py delete-model --provider nvidia --id "nvidia/old-model"

# 删除整个提供商
python model_manager.py delete-provider --name old-provider
```

## 与 OpenClaw 的集成

### 配置文件位置

技能直接修改：`~/.openclaw/openclaw.json`

### 修改后的结构

```json
{
  "models": {
    "providers": {
      "nvidia": {
        "baseUrl": "https://integrate.api.nvidia.com/v1",
        "apiKey": "nvapi-xxx",
        "api": "openai-completions",
        "models": [
          {
            "id": "nvidia/nemotron-3-nano-30b-a3b",
            "name": "nvidia/nemotron-3-nano-30b-a3b",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 128000,
            "maxTokens": 16384
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "nvidia/nemotron-3-nano-30b-a3b"
      }
    }
  }
}
```

### 重启网关

修改默认模型后，需要重启网关使更改在所有会话中生效：

```bash
openclaw gateway restart
```

## 注意事项

### ⚠️ 重要安全提示

1. **API密钥以明文存储**：~/.openclaw/openclaw.json 包含 API 密钥
2. **权限保护**：确保 openclaw.json 的文件权限正确
3. **不要提交到版本控制**：该文件可能包含敏感信息

### 🔧 故障排除

#### 问题：执行时出现编码错误

**解决方案**：脚本已经内置了 UTF-8 编码处理。

#### 问题：无法找到模型

**可能原因**：
- 模型未添加
- 提供商名称或模型ID不正确

**解决方案**：
```bash
# 列出所有模型
python model_manager.py list-models
```

#### 问题：应用模型后无法生效

**解决方案**：
```bash
# 重启 OpenClaw Gateway
openclaw gateway restart

# 检查默认模型
python model_apply.py current
```

#### 问题：配置文件损坏

**解决方案**：从备份恢复 openclaw.json 或重新初始化 OpenClaw。

## 开发说明

### 修改脚本

脚本使用 Python 3 编写，可以直接编辑：

- `model_manager.py` - 提供商和模型的增删查改逻辑
- `model_apply.py` - 应用模型为默认的逻辑

### 配置文件结构

理解 ~/.openclaw/openclaw.json 的键值结构可以帮助更好地调试问题。

关键部分：
- `models.providers` - 提供商配置
- `agents.defaults.model.primary` - 默认模型ID

## 未来扩展

可以考虑的增强功能：

- [ ] 模型使用统计和成本追踪
- [ ] API 密钥加密存储选项
- [ ] 模型性能测试和基准
- [ ] 自动模型切换策略
- [ ] Web UI 或 GUI 配置界面
- [ ] 模型导入/导出功能

## 联系支持

如遇到问题，请检查：
1. Python 版本（需要 Python 3.6+）
2. OpenClaw 版本和配置
3. ~/.openclaw/openclaw.json 的格式
4. 错误日志和输出

---

**技能创建日期：** 2026-02-19
**版本：** 2.0.0
**重大变更：** v2.0 直接管理 ~/.openclaw/openclaw.json，移除独立配置文件
**作者：** OpenClaw + 包打听的AI助手
