# back-mgr 快速参考卡

## 常用命令速查

### 项目管理
```bash
# 查看所有项目
back-mgr list

# 添加项目
back-mgr add --name <名称> --host <主机> --user <用户> \
            --remote-path <远程路径> --local-path <本地路径>

# 删除项目
back-mgr delete <项目名>
```

### 备份
```bash
# 完整备份（文件 + 数据库）
back-mgr backup <项目名>

# 仅备份文件
back-mgr backup <项目名> --files-only

# 仅备份数据库
back-mgr backup <项目名> --db-only

# 增量备份
back-mgr backup <项目名> --incremental

# 排除特定文件
back-mgr backup <项目名> --exclude "node_modules/**" --exclude "*.log"

# 模拟运行（查看将要执行的操作）
back-mgr backup <项目名> --dry-run
```

### 还原
```bash
# 还原到最新版本
back-mgr restore <项目名>

# 还原到指定版本
back-mgr restore <项目名> --version <版本号>

# 仅还原文件
back-mgr restore <项目名> --files-only

# 仅还原数据库
back-mgr restore <项目名> --db-only

# 模拟运行
back-mgr restore <项目名> --dry-run
```

### 查看版本
```bash
# 查看项目的所有备份版本
back-mgr versions <项目名>
```

## 完整示例流程

### 场景 1: 首次设置

```bash
# 1. 添加项目
back-mgr add \
  --name my-webapp \
  --host 192.168.1.100 \
  --user deploy \
  --remote-path /var/www/my-webapp \
  --local-path ~/backups/my-webapp \
  --db-type mysql \
  --db-name myapp_db

# 2. 创建首次备份
back-mgr backup my-webapp

# 3. 查看备份
back-mgr versions my-webapp
```

### 场景 2: 定期备份

```bash
# 每天创建增量备份（节省空间和时间）
back-mgr backup my-webapp --incremental

# 每周创建完整备份（数据完整性好）
back-mgr backup my-webapp
```

### 场景 3: 快速回滚

```bash
# 1. 查看可用版本
back-mgr versions my-webapp

# 2. 找到问题发生前的版本，比如 2026-02-21_100000
# 3. 还原到该版本
back-mgr restore my-webapp --version 2026-02-21_100000
```

### 场景 4: 数据库保护

```bash
# 在生产环境更新前备份数据库
back-mgr backup my-webapp --db-only

# 更新出问题后，快速还原数据库
back-mgr restore my-webapp --db-only
```

## 环境变量配置

### MySQL 数据库密码
```bash
export MYSQL_PASSWORD="your_mysql_password"
```

### PostgreSQL 数据库密码
```bash
export PG_PASSWORD="your_postgres_password"
```

## 常用排除模式

```bash
# Node.js 项目
--exclude "node_modules/**" --exclude "*.log"

# Python 项目
--exclude "__pycache__/**" --exclude "*.pyc" --exclude ".venv/**"

# Python 项目
--exclude "vendor/**" --exclude "*.log"

# 通用
--exclude ".git/**" --exclude "tmp/**" --exclude "cache/**"
```

## SSH 密钥配置（推荐）

```bash
# 1. 生成密钥
ssh-keygen -t rsa -b 4096

# 2. 复制到远程服务器
ssh-copy-id -p 22 user@host

# 3. 测试无密码登录
ssh user@host -p 22
```

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| SSH 连接失败 | 检查 `ssh user@host` 是否能连接 |
| rsync 不可用 | 安装 Git for Windows 或使用 WSL |
| 权限错误 | 检查远程路径和本地路径的读写权限 |
| 数据库失败 | 检查数据库密码已设置为环境变量 |
| 磁盘空间不足 | 清理旧备份或增加磁盘空间 |

## 备份最佳实践

1. ✅ 定期创建完整备份（如每周）
2. ✅ 日常使用增量备份（节省空间）
3. ✅ 更新前先备份
4. ✅ 测试备份的可恢复性
5. ✅ 清理过期的旧备份
6. ✅ 将备份存储在不同的物理位置（异地备份）

## 定时任务设置

### Linux/Mac (crontab)

```bash
# 编辑 crontab
crontab -e

# 添加任务
# 每天凌晨 2 点增量备份
0 2 * * * /usr/bin/back-mgr backup myapp --incremental >> ~/.back-mgr/logs/daily.log 2>&1

# 每周日凌晨 3 点完整备份
0 3 * * 0 /usr/bin/back-mgr backup myapp >> ~/.back-mgr/logs/weekly.log 2>&1
```

### Windows (任务计划程序)

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（如每天凌晨 2 点）
4. 操作：启动程序
   - 程序：`python`
   - 参数：`C:\back-mgr\back-mgr.py backup myapp --incremental`

## 目录结构

```
~/.back-mgr/
├── projects.json          # 项目配置
└── logs/                  # 日志文件

~/backups/<project>/
└── backups/
    └── <timestamp>/       # 备份版本目录
        ├── files/         # 文件备份
        ├── databases/     # 数据库备份
        └── manifest.json  # 备份清单
```

## 更多帮助

- 详细文档：查看 [README.md](README.md)
- 安装指南：查看 [INSTALL.md](INSTALL.md)
- 技能文档：查看 [SKILL.md](SKILL.md)
- 问题报告：提交 Issue 到项目仓库

---

版本：1.0.0
更新日期：2026-02-22
