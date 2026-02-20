# Upload Tool - 文件压缩上传工具

一个高效的本地文件压缩上传工具，支持自动压缩、SSH上传和远程解压。

## 功能特点

- ✅ **自动压缩**：支持单个文件或整个目录压缩为 ZIP/TAR.GZ 格式
- ✅ **SSH上传**：通过 SSH/SFTP 安全传输文件到远程服务器
- ✅ **远程解压**：上传完成后自动在服务器端解压文件
- ✅ **进度显示**：实时显示压缩和上传进度
- ✅ **MD5校验**：确保文件传输完整性
- ✅ **配置灵活**：支持配置文件自定义默认参数
- ✅ **断点续传**：支持上传中断后的续传功能

## 安装

### 1. 克隆或下载项目

```bash
cd H:\tzj\pro2026\插件规划\2月\19\skills\upload-tool
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装工具

```bash
pip install -e .
```

安装完成后，可以在任何位置使用 `upload-tool` 命令。

## 使用方法

### 基本用法

```bash
# 使用密码认证上传
upload-tool -l /本地/路径 -r /远程/路径 -s server.com -u username -p password

# 使用SSH密钥认证（推荐）
upload-tool -l ./myproject -r /var/www -s server.com -u username -k ~/.ssh/id_rsa

# 指定压缩格式为 tar.gz
upload-tool -l ./data -r /remote/data -s server.com -u user -f tar.gz

# 使用配置文件
upload-tool -l ./docs -r /var/docs -s server.com -u user --config config.json

# 跳过MD5校验（加快速度）
upload-tool -l ./project -r /var/www -s server.com -u user --no-verify
```

### 命令行参数

| 参数 | 简写 | 说明 | 必需 |
|------|------|------|------|
| `--local` | `-l` | 本地文件或目录路径 | ✅ |
| `--remote` | `-r` | 远程目录路径 | ✅ |
| `--server` | `-s` | 远程服务器地址 | ✅ |
| `--user` | `-u` | 用户名 | ✅ |
| `--password` | `-p` | 密码 | ❌（与-k二选一） |
| `--key` | `-k` | SSH私钥文件路径 | ❌（与-p二选一） |
| `--format` | `-f` | 压缩格式：zip 或 tar.gz | ❌ |
| `--config` | | 配置文件路径 | ❌ |
| `--verify` | | 是否进行MD5校验（默认开启） | ❌ |
| `--no-verify` | | 跳过MD5校验 | ❌ |

## 配置文件

创建 `config.json` 来自定义默认行为：

```json
{
    "compression_format": "tar.gz",
    "cleanup_temp": true,
    "verify_upload": true,
    "retry_count": 3,
    "retry_delay": 5,
    "exclude_patterns": [
        "__pycache__",
        ".git",
        "*.pyc",
        ".DS_Store",
        "node_modules"
    ],
    "preserve_permissions": true,
    "preserve_timestamps": true
}
```

**配置说明：**

- `compression_format`: 默认压缩格式
- `cleanup_temp`: 是否清理本地临时文件
- `verify_upload`: 是否进行MD5完整性验证
- `retry_count`: 上传失败重试次数
- `retry_delay`: 重试间隔（秒）
- `exclude_patterns`: 排除的文件/目录模式
- `preserve_permissions`: 保持文件权限
- `preserve_timestamps`: 保持时间戳

## 使用场景

### 场景1：上传Web项目

```bash
upload-tool -l ./my-website -r /var/www/html -s web-server.com -u deploy -k ~/.ssh/id_rsa
```

### 场景2：批量备份数据

```bash
upload-tool -l ./data_2026 -r /data/backup -s backup-server.com -u admin -p password -c tar.gz
```

### 场景3：使用配置文件快速部署

```bash
# 1. 创建配置文件
cat > deploy.json << EOF
{
    "compression_format": "zip",
    "verify_upload": true,
    "exclude_patterns": ["*.log", "temp", ".env.local"]
}
EOF

# 2. 使用配置文件
upload-tool -l ./project -r /var/www -s server.com -u deploy -k ~/.ssh/id_rsa --config deploy.json
```

## 工作流程

1. **压缩**：将本地文件/目录压缩成指定格式（显示压缩进度）
2. **连接**：建立SSH连接到远程服务器
3. **上传**：通过SFTP上传压缩包（显示上传进度）
4. **校验**：可选的MD5完整性验证
5. **解压**：远程自动解压到指定目录
6. **清理**：自动清理临时文件和压缩包

## 技术要求

- **Python版本**：3.8 或更高
- **远程服务器**：需安装 `unzip` 和 `tar` 命令
- **网络**：稳定的SSH连接

## 性能指标

- 压缩率：文本文件至少30%以上
- 传输速度：不低于5MB/s（视网络情况）
- 文件支持：支持大文件（>2GB）

## 错误处理

工具会在以下情况下自动重试（默认3次）：

- 网络连接不稳定
- SSH连接中断
- 文件传输失败

重试间隔默认为5秒，可在配置文件中自定义。

## 注意事项

1. **磁盘空间**：上传前请确保目标服务器有足够磁盘空间
2. **SSH密钥**：使用SSH密钥认证更安全
3. **自动清理**：压缩包上传完成后会自动删除
4. **文件属性**：工具会尝试保持原始文件权限和时间戳
5. **Windows路径**：Windows系统下使用反斜杠或正斜杠都可以

## 调试

如需查看详细日志，修改 `src/cli.py`：

```python
logging.basicConfig(level=logging.DEBUG)
```

## 卸载

```bash
pip uninstall upload-tool
```

## 开发和测试

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_compressor.py -v
```

### 开发模式

如果你想在开发时直接运行CLI：

```bash
python src/cli.py -l ./test -r /remote/test -s localhost -u test -k ~/.ssh/id_rsa
```

## 示例输出

```
============================================================
Step 1: Compressing ./myproject...
============================================================
Compressing files: 100%|████████████████████| 150/150 [00:05<00:00, 30.3file/s]
✓ Compressed to: C:\temp\upload_tool\myproject_20260220_093120.zip
✓ MD5: a1b2c3d4e5f6...

============================================================
Step 2: Connecting to server.com...
============================================================
✓ Connected successfully

============================================================
Step 3: Uploading file...
============================================================
Uploading: 100%|████████████████████| 15.0M/15.0M [00:30<00:00, 512KB/s]
✓ Uploaded to: /tmp/myproject_20260220_093120.zip

============================================================
Step 4: Verifying upload...
============================================================
✓ MD5 verification passed

============================================================
Step 5: Extracting to /var/www...
============================================================
✓ Extracted successfully

============================================================
Step 6: Cleaning up...
============================================================
✓ Cleaned local temp file
✓ Cleanup completed

============================================================
✓ Upload completed successfully!
============================================================

Summary:
  Source: ./myproject
  Destination: server.com:/var/www
  Format: zip
```

## 未来优化方向

- [ ] 多线程压缩和上传
- [ ] 图形界面版本
- [ ] 定时任务支持
- [ ] 邮件通知功能
- [ ] Web管理界面
- [ ] 支持更多压缩格式（7z, rar）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请联系作者 Fly。

---

**提示**：首次使用时建议先在测试环境验证，确保配置正确后再在生产环境使用。
