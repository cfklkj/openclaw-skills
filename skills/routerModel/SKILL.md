---
name: routerModel
description: 自定义模型管理技能，提供模型的增删查改和应用功能。直接管理 ~/.openclaw/openclaw.json 的 models 配置，支持添加提供商、模型管理以及切换默认模型。触发场景：添加新提供商/模型、列出模型、删除模型、更新提供商配置、切换默认模型。
version: 1.0.1
---

# Router Model - OpenClaw 模型管理

## 快速开始

直接管理 OpenClaw 的模型配置（~/.openclaw/openclaw.json），支持提供商和模型的增删查改。

## 核心说明

本技能直接操作 OpenClaw 的主配置文件，无需额外的配置文件。所有修改会立即生效，无需重启 OpenClaw（除了正在运行的会话可能需要重启才能使用新模型）。

## 核心文件

- `scripts/model_manager.py` - 模型管理脚本（提供商 + 模型增删查改）
- `scripts/model_apply.py` - 模型应用脚本（切换默认模型）

## 工作流程

### 1. 快速添加（推荐）

使用 `model_manager.py add` 命令一键添加提供商和模型：

```bash
python scripts/model_manager.py add --provider <provider> --api-key <key> --model-name <model_id> [--base-url <url>]
```

示例：
```bash
python scripts/model_manager.py add --provider nvidia --api-key "nvapi-xxx" --model-name "nvidia/nemotron-3-nano-30b-a3b" --base-url "https://integrate.api.nvidia.com/v1"
```

参数：
- `--provider`: 提供商名称（如 nvidia, openai, anthropic）
- `--api-key`: API密钥
- `--model-name`: 模型ID（如 `nvidia/nemotron-3-nano-30b-a3b`）
- `--base-url`: 自定义API端点（可选）

### 2. 分步添加（高级）

#### 2.1 添加提供商

```bash
python scripts/model_manager.py add-provider --name <provider> --api-key <key> [--base-url <url>]
```

示例：
```bash
python scripts/model_manager.py add-provider --name openai --api-key "sk-xxx" --base-url "https://api.openai.com/v1"
```

#### 2.2 添加模型

```bash
python scripts/model_manager.py add-model --provider <provider> --id <model_id> [--name <name>] [--context-window <size>] [--max-tokens <tokens>]
```

示例：
```bash
python scripts/model_manager.py add-model --provider nvidia --id "nvidia/nemotron-3-nano-30b-a3b" --name "Nemotron 3 Nano"
```

### 3. 列出提供商

```bash
python scripts/model_manager.py list-providers
```

输出：
```
提供商          Base URL                                          API密钥前缀
---------------------------------------------------------------------------------------
nvidia          https://integrate.api.nvidia.com/v1             nvapi-xxx...
openai          https://api.openai.com/v1                       sk-xxx...

总计: 2 个提供商
```

### 4. 列出模型

列出所有模型：
```bash
python scripts/model_manager.py list-models
```

按提供商过滤：
```bash
python scripts/model_manager.py list-models --provider nvidia
```

### 5. 更新提供商配置

```bash
python scripts/model_manager.py update-provider --name <provider> [--api-key <new-key>] [--base-url <new-url>]
```

示例：
```bash
python scripts/model_manager.py update-provider --name nvidia --api-key "nvapi-new-key"
```

### 6. 删除模型

```bash
python scripts/model_manager.py delete-model --provider <provider> --id <model_id>
```

示例：
```bash
python scripts/model_manager.py delete-model --provider nvidia --id "nvidia/nemotron-3-nano-30b-a3b"
```

### 7. 删除提供商及其所有模型

```bash
python scripts/model_manager.py delete-provider --name <provider>
```

示例：
```bash
python scripts/model_manager.py delete-provider --name nvidia
```

### 8. 应用模型为默认

使用 `model_apply.py` 切换默认模型：

```bash
python scripts/model_apply.py apply <model_spec>
```

支持的模型格式：
- 完整路径：`nvidia/nemotron-3-nano-30b-a3b`
- 模型ID模糊匹配：`nemotron`

示例：
```bash
python scripts/model_apply.py apply "nvidia/nemotron-3-nano-30b-a3b"
# 或
python scripts/model_apply.py apply "nemotron"
```

### 9. 查看当前配置

查看当前默认模型：
```bash
python scripts/model_apply.py current
```

查看会话配置：
```bash
python scripts/model_apply.py session
```

列出可用模型：
```bash
python scripts/model_apply.py list
```

预览应用（不实际执行）：
```bash
python scripts/model_apply.py apply "nemotron" --dry-run
```

## 配置文件结构

技能直接修改 `~/.openclaw/openclaw.json`，修改后的结构示例：

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

## 注意事项

- ⚠️ **直接修改配置文件**：本技能直接修改 ~/.openclaw/openclaw.json，请确保 OpenClaw 未在写入该文件
- 🔄 **会话需要重启**：修改默认模型后，正在运行的会话可能需要重启才能生效
- 📦 **备份建议**：修改前建议备份 openclaw.json 文件
- 🔐 **API密钥安全**：API密钥以明文存储，确保文件权限正确

## 故障排除

### 无法找到模型

检查模型是否已添加：
```bash
python scripts/model_manager.py list-models
```

### 应用模型失败

- 检查模型ID是否正确
- 确保提供商和模型已存在
- 检查 openclaw.json 格式是否正确

### 配置文件损坏

如果 openclaw.json 损坏，从备份恢复或重新运行 OpenClaw 初始化。

## 高级用法

### 自定义模型参数

添加模型时可以指定参数：

```bash
python scripts/model_manager.py add-model \
  --provider nvidia \
  --id "custom/model" \
  --context-window 256000 \
  --max-tokens 32768
```

### 切换默认模型后重启网关

```bash
python scripts/model_apply.py apply "nvidia/model"
openclaw gateway restart
```
