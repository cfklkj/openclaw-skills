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

### 🤖 在 OpenClaw 中使用

Upload Tool 技能可以与 OpenClaw 无缝集成，通过自然语言描述就能完成文件上传任务。

#### 自然语言调用示例

**基本上传**:
```
上传 ./project 目录到服务器 ws.flys.fun 的 /tmp
```

**使用 SSH 密钥**:
```
把 H:\tzj\pro2023\proTzj\basic_24.4.29\www\ade 上传到 ws.flys.fun 的 root:/tmp 目录，使用 SSH 密钥 ~/.ssh/id_rsa
```

**指定压缩格式**:
```
打包上传 ./data 到 server.com，使用 tar.gz 格式压缩
```

**批量上传**:
```
帮我上传这三个目录到备份服务器：./project1 ./project2 ./project3，目标路径是 /backup
```

**跳过验证**:
```
快速上传 ./files 到 remote-server:/var/www，不要 MD5 校验
```

#### OpenClow 工作原理

当你在 OpenClaw 对话中描述上传需求时：

1. **识别意图**: OpenClow 识别出你想要上传文件
2. **调用技能**: 自动调用 Upload Tool 技能
3. **解析参数**: 从自然语言中提取关键信息
   - 本地路径
   - 远程服务器
   - 用户名
   - SSH 密钥或密码
   - 其他可选参数
4. **执行任务**: 完成 压缩 → 上传 → 解压 流程
5. **返回结果**: 告诉你是否成功

#### 典型对话示例

**示例 1: 简单上传**
```
你: 上传 ./test 到 server.com 的 /tmp

OpenClow: 好的，正在上传 ./test 到 server.com:/tmp...

         压缩完成，共 10 个文件
         ✓ 已连接到 server.com
         ✓ 上传完成
         ✓ 解压完成

         ✓ 上传任务完成！
         本地: ./test
         远程: server.com:/tmp/test
```

**示例 2: 使用 SSH 密钥**
```
你: 帮我把 H:\data\project 上传到 myserver.com，使用用户 root 和 SSH 密钥 ~/.ssh/id_rsa

OpenClow: 好的，将使用 SSH 密钥 ~/.ssh/id_rsa 连接到 myserver.com (root 用户)

         开始上传 H:\data\project...

         [显示详细的压缩和上传进度]

         ✓ 上传完成！
```

**示例 3: 指定格式**
```
你: 上传 ./docs 到 webserver.com 的 /var/www/html，用 tar.gz 格式压缩

OpenClaw: 正在使用 tar.gz 格式压缩 ./docs...

         ✓ 上传完成！
```

### 💻 命令行使用

如果你喜欢直接使用命令行，可以安装工具后通过命令操作：

#### 安装工具

```bash
cd H:\tzj\pro2026\插件规划\2月\19\skills\upload-tool
pip install -e .
```

#### 基本用法

```bash
# 使用密码认证上传
upload-tool -l /本地路径 -r /远程路径 -s server.com -u username -p password

# 使用SSH密钥认证
upload-tool -l ./project -r /var/www -s server.com -u username -k ~/.ssh/id_rsa

# 指定压缩格式
upload-tool -l ./data -r /remote/data -s server.com -u user -f tar.gz

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

**命令行**:
```bash
upload-tool -l ./myproject -r /var/www/html -s web-server.com -u developer -k ~/.ssh/id_rsa
```

**OpenClow 对话**:
```
你: 部署 ./myproject 到 web-server.com 的 /var/www/html

OpenClaw: [执行上传流程]
```

### 场景2：批量上传数据文件

**命令行**:
```bash
upload-tool -l ./data_2026 -r /data/backup -s backup-server.com -u admin -p password -f tar.gz
```

**OpenClow 对话**:
```
你: 把数据库备份 ./data_2026 上传到 backup-server.com:/data/backup

OpenClaw: 正在压缩并上传数据库备份...
```

### 场景3：使用配置文件快速上传

**命令行**:
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

**OpenClow 对话**:
```
你: 使用默认配置上传 ./docs 到 server.com:/var/docs

OpenClaw: 加载配置文件并执行上传...
```

### 场景4：快速部署到生产环境

**OpenClow 对话**:
```
你: 把上线代码 ./build 打包上传到生产服务器 prod.company.com 的 /var/www/html，排除 node_modules 和日志文件

OpenClow: 收到任务：
         - 源路径: ./build
         - 目标: prod.company.com:/var/www/html
         - 排除: node_modules, *.log

         [执行上传流程]
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

## 🚀 OpenClow 用户快速指南

### 首次使用

1. **检查权限**: 确保有权限访问本地文件和远程服务器
2. **准备认证**: SSH 密钥或密码准备好了吗？
3. **直接对话**: 直接告诉 OpenClow 你要上传什么

### 常见模式

**最简单**:
```
上传 [本地路径] 到 [服务器]
```

**指定用户和目标**:
```
上传 [路径] 到 [服务器] 的 用户:[目标路径]
```

**使用 SSH 密钥**:
```
上传 [路径] 到 [服务器]，使用 SSH 密钥 [密钥路径]
```

**跳过验证加速**:
```
快速上传 [路径] 到 [服务器]，不需要 MD5 校验
```

### 参数说明（自然语言识别）

| 参数 | 自然语言关键词 | 示例 |
|------|---------------|------|
| 本地路径 | 上传/打包/发送的路径，`./` 开头或完整路径 | `./project` 或 `H:\data\files` |
| 远程服务器 | `到` + 服务器地址 | `到 ws.flys.fun` |
| 用户名 | `用户` 或 `@` 符号后 | `root@example.com` |
| 目标路径 | `:` 后的路径 | `: /var/www` |
| SSH 密钥 | `SSH 密钥`、`密钥文件` | `使用 ~/.ssh/id_rsa` |
| 压缩格式 | `zip`、`tar.gz`、`tgz` | `用 tar.gz 压缩` |
| 跳过校验 | `快速`、`不要校验`、`跳过 MD5` | `快速上传`、`不要校验` |
| 排除文件 | `排除`、`不要`、`忽略` | `排除 node_modules` |

### 完整示例

**完整对话示例 1**:
```
你: 我要上传项目到服务器

OpenClow: 好的，请告诉我：
         1. 本地项目路径是什么？
         2. 目标服务器地址？

你: 本地是 H:\projects\myapp，服务器是 ws.flys.fun

OpenClow: 需要使用 SSH 密钥吗？还是用密码？

你: 用 SSH 密钥 ~/.ssh/id_rsa，用户是 root

OpenClow: 好的，正在上传 H:\projects\myapp 到 ws.flys.fun:/tmp

         [显示上传进度]

         ✓ 上传完成！
```

**完整对话示例 2**:
```
你: 帮我部署这个项目到生产环境：./build -> prod.company.com:/var/www/html

OpenClow: 收到！正在部署生产环境...

         源: ./build
         目标: prod.company.com:/var/www/html

         ✓ 压缩完成（245 个文件）
         ✓ 上传完成（12.8 MB）
         ✓ 解压完成

         ✓ 部署成功！
```

### 故障排查

**问题 1: OpenClow 识别不了意图**
- ✅ 确保提到"上传"、"部署"、"发送"等关键词
- ✅ 明确指定服务器地址

**问题 2: 连接超时**
- ✅ 检查服务器地址是否正确
- ✅ 确认网络连接正常
- ✅ 检查 SSH 密钥路径是否正确

**问题 3: 权限错误**
- ✅ 确认用户名正确
- ✅ 检查是否有写入目标目录的权限
- ✅ 确认 SSH 密钥对应正确的用户

### 提示和技巧

1. **简洁表达**: 自然语言越简洁，识别越准确
   ```
   好: 上传 ./test 到 server.com
   不好: 我有个文件夹叫 test，想要把它发送到 server.com 服务器上去
   ```

2. **明确路径**: 使用完整路径或明确的相对路径
   ```
   好: H:\data\files
   不好: 那个文件夹
   ```

3. **一次一个**: 建议每次上传一个目标，OpenClow 支持多次对话
4. **使用 SSH 密钥**: 更安全且不需要每次输入密码
5. **描述目标**: 明确说明是部署还是备份，OpenClow 可以优化处理

### 与命令行的对比

| 任务 | OpenClow 自然语言 | 命令行 |
|------|------------------|--------|
| 简单上传 | 1 行 | 1 行 |
| 复杂参数 | 1-2 行 | 很长 |
| 多步任务 | 多次对话 | 多个脚本 |
| 学习成本 | 低 | 中 |
| 灵活性 | 高 | 最高 |

---

**开发者提示**：此工具已在 Windows 和 Linux 环境中测试通过，macOS 也完全兼容。如有问题，请查看日志文件或开启调试模式。

**OpenClow 用户提示**：最简单的使用方式就是用自然语言描述你的需求，OpenClow 会自动处理细节！
