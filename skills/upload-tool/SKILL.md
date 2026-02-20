# Upload Tool - 文件压缩上传工具

一个高效的本地文件压缩上传工具，支持自动压缩、SSH上传和远程解压。

## 功能特点

- **自动压缩**：支持单个文件或整个目录压缩为 ZIP/TAR.GZ 格式
- **SSH上传**：通过 SSH/SFTP 安全传输文件到远程服务器
- **远程解压**：上传完成后自动在服务器端解压文件
- **进度显示**：实时显示压缩和上传进度
- **MD5校验**：确保文件传输完整性
- **配置灵活**：支持配置文件自定义默认参数
- **断点续传**：支持上传中断后的续传功能

## 安装依赖

```bash
pip install paramiko scp tqdm click pydantic cryptography
```

或安装完整依赖：

```bash
pip install -r requirements.txt
```

## 安装工具

```bash
cd H:\tzj\pro2026\插件规划\2月\19\skills\upload-tool
pip install -e .
```

## 使用方法

### 基本用法

```bash
# 使用密码认证上传
upload-tool -l /本地路径 -r /远程路径 -s server.com -u username -p password

# 使用SSH密钥认证
upload-tool -l ./project -r /var/www -s server.com -u username -k ~/.ssh/id_rsa

# 指定压缩格式
upload-tool -l ./data -r /remote/data -s server.com -u user -c tar.gz

# 使用配置文件
upload-tool -l ./docs -r /var/docs -s server.com -u user --config config.json

# 跳过MD5校验
upload-tool -l ./project -r /var/www -s server.com -u user --no-verify
```

### 命令行参数

| 参数 | 说明 | 必需 |
|------|------|------|
| `-l, --local` | 本地文件或目录路径 | ✅ |
| `-r, --remote` | 远程目录路径 | ✅ |
| `-s, --server` | 远程服务器地址 | ✅ |
| `-u, --user` | 用户名 | ✅ |
| `-p, --password` | 密码（与SSH密钥二选一） | ❌ |
| `-k, --key` | SSH私钥文件路径（与密码二选一） | ❌ |
| `-f, --format` | 压缩格式：zip 或 tar.gz | ❌ |
| `--config` | 配置文件路径 | ❌ |
| `--verify` / `--no-verify` | 是否进行MD5校验（默认开启） | ❌ |

### 配置文件示例

创建 `config.json`：

```json
{
    "compression_format": "tar.gz",
    "temp_dir": "/tmp/upload_tool",
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

## 使用场景

### 场景1：上传项目代码

```bash
upload-tool -l ./myproject -r /var/www/html -s web-server.com -u developer -k ~/.ssh/id_rsa
```

### 场景2：批量上传数据文件

```bash
upload-tool -l ./data_2026 -r /data/backup -s backup-server.com -u admin -p password -c tar.gz
```

### 场景3：使用配置文件快速上传

```bash
# 先创建配置文件
cat > myconfig.json << EOF
{
    "compression_format": "zip",
    "verify_upload": true,
    "exclude_patterns": ["*.log", "temp"]
}
EOF

# 使用配置文件上传
upload-tool -l ./docs -r /var/docs -s server.com -u user --config myconfig.json
```

## 工作流程

1. **压缩**：将本地文件/目录压缩成指定格式
2. **连接**：建立SSH连接到远程服务器
3. **上传**：通过SFTP上传压缩包（带进度条）
4. **校验**：可选的MD5完整性验证
5. **解压**：远程自动解压到指定目录
6. **清理**：自动清理临时文件

## 技术要求

- **Python版本**：3.8+
- **远程服务器**：需安装 unzip 或 tar 命令
- **网络**：稳定的SSH连接

## 性能指标

- 压缩率：文本文件至少30%以上
- 传输速度：不低于5MB/s（视网络情况）
- 支持文件：支持大文件（>2GB）

## 错误处理

工具会在以下情况下自动重试（默认3次）：
- 网络连接不稳定
- SSH连接中断
- 文件传输失败

重试间隔默认为5秒，可在配置文件中自定义。

## 注意事项

1. 上传前请确保目标服务器有足够磁盘空间
2. 使用SSH密钥认证更安全
3. 压缩包上传完成后会自动删除
4. 工具会尝试保持原始文件权限和时间戳
5. Windows系统路径使用反斜杠或正斜杠都可以

## 调试

如需查看详细日志，修改 `src/cli.py` 中的日志级别：

```python
logging.basicConfig(level=logging.DEBUG)
```

## 卸载

```bash
pip uninstall upload-tool
```

## 开发和测试

运行测试：

```bash
python -m pytest tests/
```

## 未来优化方向

- 多线程压缩和上传
- 图形界面版本
- 定时任务支持
- 邮件通知功能
- Web管理界面

---

**开发者提示**：此工具已在 Windows 和 Linux 环境中测试通过，macOS 也完全兼容。如有问题，请查看日志文件或开启调试模式。
