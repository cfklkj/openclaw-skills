# back-mgr - 远程项目备份与还原工具

一个简单易用的命令行工具，用于管理远程项目的备份和还原。

## 功能特性

- ✅ 项目信息管理（添加、查看、删除）
- ✅ 完整备份和增量备份
- ✅ 支持文件系统和数据库备份
- ✅ 版本管理和选择性还原
- ✅ 支持 MySQL 和 PostgreSQL 数据库
- ✅ 使用 rsync/SCP 安全传输
- ✅ 跨平台支持（Windows、macOS、Linux）

## 安装

### 前置要求

- Python 3.8+
- SSH 客户端
- rsync（可选，推荐用于增量备份）

### Windows 上的准备工作

1. 安装 Python 3.8+
2. 安装 OpenSSH（Windows 10/11 通常已预装）
3. 安装 rsync（可选）：
   - 下载 Git for Windows（包含 rsync）
   - 或者使用 WSL

### 安装命令

```bash
# 使用 pip 安装
pip install -e .

# 或直接使用
python back-mgr.py --help
```

## 快速开始

### 1. 添加项目

```bash
back-mgr add \
  --name myapp \
  --host example.com \
  --user deploy \
  --port 22 \
  --remote-path /var/www/myapp \
  --local-path ~/backups/myapp \
  --db-type mysql \
  --db-name myapp_db \
  --db-user root
```

### 2. 查看项目列表

```bash
back-mgr list
```

### 3. 创建备份

```bash
# 完整备份（文件 + 数据库）
back-mgr backup myapp

# 仅备份文件
back-mgr backup myapp --files-only

# 增量备份
back-mgr backup myapp --incremental

# 排除特定文件
back-mgr backup myapp --exclude "node_modules/**" --exclude "*.log"
```

### 4. 查看备份版本

```bash
back-mgr versions myapp
```

### 5. 还原项目

```bash
# 还原到最新版本
back-mgr restore myapp

# 还原到指定版本
back-mgr restore myapp --version 2026-02-22_143022

# 仅还原文件
back-mgr restore myapp --files-only
```

### 6. 模拟运行

在执行前使用 `--dry-run` 查看将要执行的操作：

```bash
back-mgr backup myapp --dry-run
back-mgr restore myapp --dry-run
```

## 目录结构

```
~/.back-mgr/
├── projects.json          # 项目配置文件
├── logs/                  # 日志目录

~/backups/myapp/
└── backups/
    ├── 2026-02-22_143022/
    │   ├── files/         # 备份的文件
    │   ├── databases/     # 数据库备份
    │   └── manifest.json  # 备份清单
    ├── 2026-02-22_150000/
    └── ...
```

## 配置文件格式

项目配置存储在 `~/.back-mgr/projects.json`：

```json
{
  "projects": [
    {
      "name": "myapp",
      "host": "example.com",
      "user": "deploy",
      "port": 22,
      "remotePath": "/var/www/myapp",
      "localPath": "~/backups/myapp",
      "databases": [
        {
          "type": "mysql",
          "name": "myapp_db",
          "user": "root",
          "host": "localhost",
          "port": 3306
        }
      ],
      "exclude": [
        "node_modules/**",
        ".git/**",
        "*.log"
      ],
      "encryptSensitive": true
    }
  ]
}
```

## 数据库密码配置

### MySQL

```bash
export MYSQL_PASSWORD="your_password"
back-mgr backup myapp
```

### PostgreSQL

```bash
export PG_PASSWORD="your_password"
back-mgr backup myapp
```

## 高级用法

### 定时备份

使用 cron 或任务计划程序设置定时备份：

```bash
# 每天凌晨 2 点备份
0 2 * * * /usr/bin/back-mgr backup myapp
```

### 排除文件

添加项目时可以指定要排除的文件：

```bash
back-mgr add \
  --name myapp \
  --host example.com \
  --user deploy \
  --remote-path /var/www/myapp \
  --local-path ~/backups/myapp \
  --exclude "node_modules/**" \
  --exclude ".git/**" \
  --exclude "*.log" \
  --exclude "tmp/**"
```

### SSH 密钥

配置 SSH 密钥以实现无密码登录：

```bash
# 生成 SSH 密钥
ssh-keygen -t rsa -b 4096

# 复制公钥到远程服务器
ssh-copy-id -p 22 deploy@example.com
```

## 故障排除

### SSH 连接失败

检查 SSH 配置：
```bash
ssh deploy@example.com -p 22
```

### 权限错误

确保：
- 对远程路径有读取权限
- 对本地备份路径有写入权限
- 数据库用户有备份/还原权限

### rsync 不可用

如果系统没有 rsync，工具会自动回退到 scp：
```bash
# Windows 通过 Git Bash 或 WSL 安装 rsync
# 或直接使用 scp（功能受限）
```

### 数据库备份失败

检查：
1. 数据库是否运行
2. 用户权限是否正确
3. 密码是否通过环境变量设置

## 注意事项

1. ⚠️ **测试后使用**：首次使用前建议使用 `--dry-run` 测试
2. ⚠️ **备份前验证**：还原前先验证备份内容的完整性
3. ⚠️ **磁盘空间**：确保本地有足够的磁盘空间存储备份
4. ⚠️ **网络稳定**：备份大文件时建议使用稳定的网络环境
5. ⚠️ **保留配置**：备份和还原会覆盖目标，确保本地配置是可用的

## 开发

### 运行测试

```bash
python back-mgr.py --help
python back-mgr.py list
```

### 项目结构

```
back-mgr/
├── back-mgr.py           # 主程序
├── SKILL.md              # OpenClaw 技能文档
├── README.md             # 本文档
└── requirements.txt      # Python 依赖
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2026-02-22)

- ✅ 初始版本
- ✅ 基本项目管理功能
- ✅ 文件备份/还原
- ✅ MySQL/PostgreSQL 支持
- ✅ 版本管理
