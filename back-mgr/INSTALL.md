# OpenClaw 技能安装指南

## 安装方式

### 方式 1: 直接拷贝到 OpenClaw 技能目录

```bash
# 1. 找到你的 OpenClaw 技能目录
# 通常是 ~/.openclaw/skills/ 或通过 ClawdHub 安装

# 2. 复制整个技能文件夹
cp -r back-mgr ~/.openclaw/skills/

# 3. 设置脚本执行权限
chmod +x ~/.openclaw/skills/back-mgr/back-mgr.py
```

### 方式 2: 使用 npm 安装（推荐）

```bash
cd back-mgr
npm install -g .
```

### 方式 3: 通过 ClawdHub 安装（需要先发布到 ClawdHub）

```bash
clawdhub install back-mgr
```

## 安装后使用

重新启动 OpenClaw 后，即可在 Telegram 中使用：

```
# 查看项目列表
back-mgr list

# 添加项目（需要配置 SSH）
back-mgr add --name myapp --host example.com --user deploy --remote-path /var/www/myapp --local-path ~/backups/myapp

# 创建备份
back-mgr backup myapp

# 还原项目
back-mgr restore myapp
```

## 系统要求

- Python 3.8 或更高版本
- SSH 客户端（系统自带的 OpenSSH 或手动安装的）
- rsync（可选，推荐用于增量传输）

## Windows 特别说明

### 1. 确保已安装 Python

```powershell
# 检查 Python 版本
python --version
```

如果未安装，从 [python.org](https://www.python.org/downloads/) 下载安装。

### 2. OpenSSH

Windows 10/11 通常已经预装 OpenSSH：

```powershell
# 检查 SSH 是否可用
ssh -V
```

### 3. rsync（可选）

- 通过 Git for Windows 安装（包含 rsync）
- 或使用 WSL (Windows Subsystem for Linux)

### 4. 配置 PATH

确保 Python 在系统 PATH 中，以便 OpenClaw 可以找到并执行脚本。

## 测试安装

```bash
# 测试脚本是否能正常运行
back-mgr --help

# 测试基本命令
back-mgr list
```

如果能看到帮助信息，说明安装成功！

## 故障排除

### 问题: 找不到 back-mgr 命令

**解决方案:**
1. 检查 Python 是否在 PATH 中
2. 重新启动终端
3. 或者直接使用 `python back-mgr.py` 运行

### 问题: SSH 连接失败

**解决方案:**
1. 检查 OpenSSH 是否正确安装
2. 测试 SSH 连接：`ssh user@host -p port`
3. 配置 SSH 密钥以实现无密码登录

### 问题: rsync 不可用

**解决方案:**
1. 安装 Git for Windows（包含 rsync）
2. 或使用 WSL
3. 工具会自动回退到 scp（功能略有限制）

### 问题 Windows 中文字体编码乱码

**解决方案:**
这是 Windows 控制台的 GBK 编码问题，不影响功能。建议：
- 使用 Git Bash
- 使用 WSL
- 或修改控制台编码为 UTF-8

```powershell
# 在 PowerShell 中设置 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```

## 配置 SSH 密钥（推荐）

配置 SSH 密钥后可以免密码登录，自动化备份更方便：

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t rsa -b 4096

# 2. 复制公钥到远程服务器
ssh-copy-id -p 22 deploy@example.com

# 3. 测试无密码登录
ssh deploy@example.com
```

## 下一步

阅读 [SKILL.md](SKILL.md) 了解所有功能和使用方法。

查看 [README.md](README.md) 获取详细的使用文档和示例。
