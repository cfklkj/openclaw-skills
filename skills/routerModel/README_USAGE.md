# Router Model 技能 - 使用指南

## 技能概览

`routerModel` 技能提供了一套完整的自定义模型管理解决方案，支持：

- ✅ 添加、更新、删除自定义模型配置
- ✅ 按提供商搜索和筛选模型
- ✅ 一键列出所有已配置的模型
- ✅ 将模型应用到当前 OpenClaw 会话

## 目录结构

```
routerModel-skill/
├── SKILL.md                    # 技能主文件（AI 代理读取）
├── README_USAGE.md            # 本使用指南
└── scripts/
    ├── model_config.json      # 模型配置存储
    ├── model_manager.py       # 模型管理脚本
    └── model_apply.py         # 模型应用脚本
```

## 快速示例

### 1. 添加 NVIDIA 模型

```bash
cd "H:\tzj\pro2026\插件规划\2月\19\routerModel-skill\scripts"
python model_manager.py add --provider nvidia --api-key "nvapi-your-key" --model-name "nvidia/nemotron-3-nano-30b-a3b" --base-url "https://integrate.api.nvidia.com/v1"
```

输出：
```
✓ 模型添加成功
  ID: nvidia-001
  提供商: nvidia
  模型名称: nvidia/nemotron-3-nano-30b-a3b
  Base URL: https://integrate.api.nvidia.com/v1
```

### 2. 查看所有模型

```bash
python model_manager.py list
```

输出：
```
ID              提供商          模型名称                                     创建时间
---------------------------------------------------------------------------------------
nvidia-001      nvidia       nvidia/nemotron-3-nano-30b-a3b           2026-02-19 12:00:00
openai-001      openai       gpt-4                                     2026-02-19 12:05:00

总计: 2 个模型
```

### 3. 应用模型到会话

```bash
python model_apply.py --id nvidia-001
```

或使用名称模糊匹配：
```bash
python model_apply.py --name nemotron
```

### 4. 搜索特定提供商的模型

```bash
python model_manager.py search --provider nvidia
```

### 5. 更新模型配置

```bash
python model_manager.py update --id nvidia-001 --api-key "new-api-key"
```

### 6. 删除模型

```bash
python model_manager.py delete --id nvidia-001
```

## 完整命令参考

### model_manager.py

```bash
# 添加模型
python model_manager.py add --provider <提供商> --api-key <密钥> --model-name <模型名> [--base-url <端点>]

# 列出所有模型
python model_manager.py list

# 列出特定提供商的模型
python model_manager.py list --provider <提供商>

# 搜索模型
python model_manager.py search --provider <提供商>

# 更新模型
python model_manager.py update --id <模型ID> [--api-key <新密钥>] [--model-name <新模型名>] [--base-url <新端点>]

# 删除模型
python model_manager.py delete --id <模型ID>

# 获取模型详情（JSON）
python model_manager.py get --id <模型ID>
python model_manager.py get --name <模型名>
```

### model_apply.py

```bash
# 列出所有可用模型
python model_apply.py --list

# 通过ID应用模型
python model_apply.py --id <模型ID>

# 通过名称模糊匹配应用模型
python model_apply.py --name <模型名>

# 预览应用（不实际执行）
python model_apply.py --id <模型ID> --dry-run
```

## 配置文件说明

`model_config.json` 存储所有模型配置：

```json
{
  "models": [
    {
      "id": "nvidia-001",
      "provider": "nvidia",
      "api_key": "nvapi-xxx",
      "base_url": "https://integrate.api.nvidia.com/v1",
      "model_name": "nvidia/nemotron-3-nano-30b-a3b",
      "created_at": "2026-02-19T12:00:00Z",
      "last_used": "2026-02-19T12:30:00Z"
    }
  ]
}
```

### 字段说明

- `id`: 模型唯一标识（自动生成，格式：`{provider}-{序号}`）
- `provider`: 提供商名称
- `api_key`: API 密钥
- `base_url`: 自定义API端点（可选）
- `model_name`: 模型完整名称
- `created_at`: 创建时间（ISO 8601 格式）
- `last_used`: 最后使用时间（如果未使用则为 null）

## 支持的模型提供商示例

### NVIDIA

```bash
python model_manager.py add --provider nvidia --api-key "nvapi-xxx" --model-name "nvidia/nemotron-3-nano-30b-a3b" --base-url "https://integrate.api.nvidia.com/v1"
```

### OpenAI

```bash
python model_manager.py add --provider openai --api-key "sk-xxx" --model-name "gpt-4"
```

### Anthropic

```bash
python model_manager.py add --provider anthropic --api-key "sk-ant-xxx" --model-name "claude-3-opus-20240229"
```

### 其他提供商

根据需求添加即可，脚本不限制提供商类型。

## 安全注意事项

⚠️ **重要安全提示：**

1. **不要将 `model_config.json` 提交到版本控制系统**
2. 文件包含明文 API 密钥，应妥善保管
3. 建议将配置文件路径添加到 `.gitignore`

## 故障排除

### 问题：执行时出现编码错误

**解决方案：** 脚本已经内置了 UTF-8 编码处理，如果仍有问题，请确保终端支持 UTF-8。

### 问题：无法应用模型到会话

**可能原因：**
- OpenClaw Gateway 未运行
- 模型配置不正确
- API 密钥无效

**解决方案：**
```bash
# 检查 OpenClaw Gateway 状态
openclaw gateway status

# 预览应用以检查配置
python model_apply.py --id <模型ID> --dry-run
```

### 问题：配置文件损坏

**解决方案：** 删除 `model_config.json`，它会自动重建为空配置。

```bash
del "H:\tzj\pro2026\插件规划\2月\19\routerModel-skill\scripts\model_config.json"
```

## 开发说明

### 修改脚本

脚本使用 Python 3 编写，可以直接编辑：

- `model_manager.py` - 模型的增删查改逻辑
- `model_apply.py` - 应用模型到会话的逻辑

### 测试

所有功能已通过测试，验证命令：

```bash
# 测试添加
python model_manager.py add --provider test --api-key "test-key" --model-name "test-model"

# 测试列出
python model_manager.py list

# 测试获取
python model_manager.py get --id test-001

# 测试更新
python model_manager.py update --id test-001 --api-key "updated-key"

# 测试删除
python model_manager.py delete --id test-001
```

## 未来扩展

可以考虑的增强功能：

- [ ] 模型使用统计和成本追踪
- [ ] API 密钥加密存储
- [ ] 模型性能测试和基准
- [ ] 自动模型切换策略
- [ ] Web UI 或 GUI 配置界面

## 联系支持

如遇到问题，请检查：
1. Python 版本（需要 Python 3.6+）
2. OpenClaw 版本
3. 错误日志和输出

---

**技能创建日期：** 2026-02-19
**版本：** 1.0.0
**作者：** OpenClaw + 包打听的AI助手
