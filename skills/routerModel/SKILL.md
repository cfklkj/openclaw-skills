---
name: routerModel
description: 自定义模型管理技能，提供模型的增删查改和应用功能。用于管理多个AI模型提供商（如NVIDIA、OpenAI、Anthropic等）的API密钥和模型配置，并支持将模型应用到当前会话。触发场景：添加新模型、列出模型、删除模型、更新模型配置、切换会话使用的模型。
---

# Router Model - 自定义模型管理

## 快速开始

管理自定义模型配置，支持多个提供商的API密钥和模型名称管理。

## 核心文件

- `model_config.json` - 模型配置存储文件
- `scripts/model_manager.py` - 模型管理脚本（增删查改）
- `scripts/model_apply.py` - 模型应用脚本（切换会话模型）

## 工作流程

### 1. 添加模型

使用 `model_manager.py add` 命令添加新模型：

```bash
python scripts/model_manager.py add --provider <provider> --api-key <key> --model-name <name>
```

示例：
```bash
python scripts/model_manager.py add --provider nvidia --api-key "nvapi-xxx" --model-name "nvidia/nemotron-3-nano-30b-a3b"
```

参数：
- `--provider`: 提供商名称（如 nvidia, openai, anthropic）
- `--api-key`: API密钥
- `--model-name`: 模型完整名称（支持路径格式，如 `provider/model-name`）

### 2. 列出模型

使用 `model_manager.py list` 查看所有已配置的模型：

```bash
python scripts/model_manager.py list
```

输出格式：表格显示模型ID、提供商、模型名称和配置时间。

### 3. 搜索模型

使用 `model_manager.py search` 按提供商搜索：

```bash
python scripts/model_manager.py search --provider <provider>
```

示例：
```bash
python scripts/model_manager.py search --provider nvidia
```

### 4. 更新模型配置

使用 `model_manager.py update` 更新已存在的模型：

```bash
python scripts/model_manager.py update --id <model-id> [--api-key <new-key>] [--model-name <new-name>]
```

示例：
```bash
python scripts/model_manager.py update --id nvidia-001 --api-key "nvapi-new-key"
```

### 5. 删除模型

使用 `model_manager.py delete` 删除模型：

```bash
python scripts/model_manager.py delete --id <model-id>
```

示例：
```bash
python scripts/model_manager.py delete --id nvidia-001
```

### 6. 应用模型到会话

使用 `model_apply.py` 将模型应用到当前会话：

```bash
python scripts/model_apply.py --model-id <model-id>
```

这会：
1. 从配置中读取模型的API密钥和模型名称
2. 检测当前会话
3. 通过 `gateway config.patch` 更新会话使用的模型

支持通过模型名称直接应用（模糊匹配）：

```bash
python scripts/model_apply.py --model-name "nvidia/nemotron"
```

## 配置文件格式

`model_config.json` 结构：

```json
{
  "models": [
    {
      "id": "nvidia-001",
      "provider": "nvidia",
      "api_key": "nvapi-xxx",
      "model_name": "nvidia/nemotron-3-nano-30b-a3b",
      "created_at": "2026-02-19T12:00:00Z",
      "last_used": "2026-02-19T12:30:00Z"
    }
  ]
}
```

## 注意事项

- API密钥以明文存储在本地配置文件中，请确保 `model_config.json` 不被提交到版本控制系统
- 模型ID格式：`{provider}-{序号}`（自动生成）
- 应用模型到会话需要 OpenClaw Gateway 运行中
- 更新模型配置会同步更新会话，可能需要几秒钟生效

## 故障排除

### 添加模型失败

检查：
- 文件路径是否正确
- JSON格式是否有效
- 是否有写权限

### 应用模型失败

检查：
- OpenClaw Gateway 是否运行
- 模型ID或名称是否正确
- API密钥是否有效

### 配置文件损坏

如果 `model_config.json` 损坏，删除它会自动重建为空配置。
