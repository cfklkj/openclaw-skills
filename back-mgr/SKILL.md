# back-mgr - 远程项目备份与还原管理

## 描述

back-mgr 是一个用于远程项目备份和还原的命令行工具。它可以：
- 管理多个远程项目的部署信息
- 从远程服务器备份项目文件到本地
- 将本地备份还原到远程服务器
- 支持数据库备份和还原
- 处理敏感配置文件（如 .env）
- 支持版本管理和选择性备份/还

## 快速开始

### 查看项目列表
```bash
back-mgr list
```

### 添加项目
```bash
back-mgr add \
  --name myapp \
  --host example.com \
  --user deploy \
  --remote-path /var/www/myapp \
  --local-path ~/backups/myapp
```

### 创建备份
```bash
# 完整备份（包含数据库）
back-mgr backup <project-name>

# 仅备份文件
back-mgr backup <project-name> --files-only

# 增量备份
back-mgr backup <project-name> --incremental
```

### 还原项目
```bash
# 还原到最新版本
back-mgr restore <project-name>

# 还原指定版本
back-mgr restore <project-name> --version 2026-02-22_143022

# 仅还原文件
back-mgr restore <project-name> --files-only
```

### 列出备份版本
```bash
back-mgr versions <project-name>
```

### 删除项目
```bash
back-mgr delete <project-name>
```

## 功能详解

### 项目管理命令

#### `back-mgr add` - 添加项目
配置一个新项目的部署信息。
- `--name`: 项目名称（必需）
- `--host`: 远程服务器地址（必需）
- `--user`: SSH 用户名（必需）[默认: root]
- `--port`: SSH 端口 [默认: 22]
- `--remote-path`: 远程项目路径（必需）
- `--local-path`: 本地备份路径（必需）
- `--db-type`: 数据库类型 (mysql/postgresql/mongodb) [可选]
- `--db-name`: 数据库名称 [可选]
- `--db-user`: 数据库用户 [可选]
- `--exclude`: 排除的文件模式（可多个）

#### `back-mgr list` - 列出项目
显示所有已配置的项目及其基本信息。

#### `back-mgr delete` - 删除项目
从配置中移除一个项目配置（备份文件不会被删除）。

### 备份命令

#### `back-mgr backup <project-name>`
创建项目备份。
- `--files-only`: 仅备份文件系统，不包含数据库
- `--db-only`: 仅备份数据库
- `--incremental`: 增量备份（仅备份修改的文件）
- `--exclude`: 额外排除的文件模式
- `--no-encrypt`: 不加密敏感文件
- `--dry-run`: 模拟运行，不实际执行

#### `back-mgr versions <project-name>`
查看项目的所有备份版本。

### 还原命令

#### `back-mgr restore <project-name>`
还原项目到远程服务器。
- `--version`: 指定还原的版本（默认：最新版本）
- `--files-only`: 仅还原文件
- `--db-only`: 仅还原数据库
- `--dry-run`: 模拟运行，不实际执行

## 配置文件

项目配置存储在 `~/.back-mgr/projects.json`，结构如下：
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

## 使用场景

### 场景 1: 首次配置项目
```bash
# 添加项目配置
back-mgr add \
  --name my-webapp \
  --host 192.168.1.100 \
  --user deploy \
  --remote-path /var/www/my-webapp \
  --local-path ~/backups/my-webapp \
  --db-type mysql \
  --db-name myapp_db

# 创建完整备份
back-mgr backup my-webapp
```

### 场景 2: 定期备份
```bash
# 每天创建增量备份
back-mgr backup my-webapp --incremental

# 每周创建完整备份
back-mgr backup my-webapp
```

### 场景 3: 快速回滚
```bash
# 查看可用版本
back-mgr versions my-webapp

# 还原到指定版本
back-mgr restore my-webapp --version 2026-02-21_100000
```

### 场景 4: 仅备份数据库
```bash
back-mgr backup my-webapp --db-only
```

## 自然语言调用示例

在 OpenClaw 中，你可以用自然语言与 back-mgr 技能交互，它会理解你的意图并执行相应操作。

### 查看项目管理

**查看所有项目：**
```
"查看所有已配置的项目"
"列出项目列表"
"我有哪些项目"
```

**添加新项目：**
```
"添加一个项目，名字是 myapp，服务器是 example.com，用户是 deploy，远程路径是 /var/www/myapp，本地备份到 ~/backups/myapp"
"帮我把 192.168.1.100 上的 webapp 添加到备份列表"
```

### 备份操作

**创建完整备份：**
```
"备份 myapp 项目"
"给 webapp 做个完整备份"
"备份我的网站数据"
```

**增量备份：**
```
"做个增量备份 myapp"
"快速备份一下 myapp 的改动"
```

**仅备份文件或数据库：**
```
"只备份 myapp 的数据库"
"不要数据库，只备份 myapp 的文件"
"database only backup for webapp"
```

**排除特定文件：**
```
"备份 myapp，不要 node_modules 文件夹"
"备份时排除所有 .log 文件"
```

**模拟运行：**
```
"模拟备份 myapp 看看会发生什么"
"dry run backup for webapp"
```

### 还原操作

**还原到最新版本：**
```
"还原 myapp"
"把 webapp 恢复到最新的备份"
"恢复我的网站"
```

**还原到指定版本：**
```
"还原 myapp 到 2026-02-21_100000 版本"
"把 webapp 恢复到昨天的备份"
"恢复到指定版本"
```

**仅还原文件或数据库：**
```
"只还原文件，不要数据库"
"只恢复数据库数据"
"restore files only"
```

**查看还原预览：**
```
"模拟还原 myapp 看看会做什么"
```

### 版本管理

**查看备份版本：**
```
"查看 myapp 的所有备份版本"
"webapp 有哪些备份版本"
"列出历史备份"
```

### 删除操作

**删除项目：**
```
"删除 myapp 项目配置"
"移除 webapp 备份配置"
"删除这个项目"
```

### 组合操作场景

**场景 1 - 首次设置：**
```
User: "帮我添加一个项目，生产服务器是 prod.example.com，用户是 deploy，路径是 /var/www/production，本地备份到 ~/backups/prod，数据库是 mysql 的 prod_db"
AI: "好的，我来帮你添加项目..." (执行 back-mgr add)
...
AI: "项目已添加到配置中。需要现在创建首次备份吗？"
User: "先做个完整备份"
AI: "正在备份..." (执行 back-mgr backup)
```

**场景 2 - 更新前备份：**
```
User: "我要更新生产环境了，先备份数据库"
AI: "好的，正在备份 prod 项目的数据库..." (执行 back-mgr backup --db-only)
...
AI: "数据库备份完成。更新完成后如果需要还原，随时告诉我。"
```

**场景 3 - 出问题回滚：**
```
User: "更新出问题了，赶紧帮我回滚！"
AI: "别慌，让我先查看可用的备份版本..." (执行 back-mgr versions)
...
AI: "有以下版本可选：
   1. 2026-02-22_100000 (更新前)
   2. 2026-02-21_150000 (昨天)
建议还原到刚才的备份（更新前）？"
User: "对，还原到更新前的版本"
AI: "正在还原到 2026-02-22_100000..." (执行 back-mgr restore)
```

**场景 4 - 定期备份：**
```
User: "每天下午帮我做个增量备份"
AI: "明白了。需要创建定时任务吗？可以用 cron 技能设置每天下午执行。"
User: "好的，设置一下"
AI: "设置完成：每天 17:00 自动对 myapp 执行增量备份。"
```

### 常见表达方式

OpenClaw 会理解以下类似的自然语言表达：

**备份：**
- "备份" / "做个备份" / "创建备份"
- "backup" / "做备份" / "保存一下"
- "快照" / "snapshot"

**还原：**
- "还原" / "恢复" / "回滚"
- "restore" / "恢复到" / "回退到"
- "还原到某个时点"

**查看：**
- "查看" / "列出" / "显示"
- "list" / "show" / "看看"
- "有什么版本" / "历史备份"

**删除：**
- "删除" / "移除" / "去掉"
- "delete" / "remove"

### 智能上下文理解

OpenClaw 会记住项目名称和上下文：

```
User: "添加 myweb 项目，服务器是..."
AI: "已添加项目。"
User: "现在备份它"  # 知道是指 myweb
AI: "正在备份 myweb..."
```

```
User: "看看有哪些版本"
AI: "哪个项目？"
User: "myweb"  # 明确指定
AI: "myweb 的备份版本：1. 2026-02-22_100000..."
```

## 注意事项

1. **SSH 访问**: 确保本地可以通过 SSH 访问远程服务器（配置好密钥或密码）
2. **路径权限**: 确保远程路径和本地备份路径有正确的读写权限
3. **磁盘空间**: 备份前确保本地有足够的磁盘空间
4. **网络稳定**: 备份大文件时建议稳定的网络环境
5. **敏感文件**: .env 文件默认会被加密存储

## 依赖要求

- Python 3.8+
- SSH 客户端 (OpenSSH 或 PuTTY on Windows)
- rsync (用于增量传输，可选)

## 故障排除

### SSH 连接失败
检查 SSH 配置和密钥：
```bash
ssh user@host -p port
```

### 权限错误
确保：
- 对远程路径有读取权限
- 对本地备份路径有写入权限
- 数据库有备份/还原权限

### 传输中断
- 增量备份支持断点续传
- 重新运行备份命令会自动跳过已传输的文件

## 高级功能

### 环境变量支持
可以通过环境变量配置 SSH 密码（不推荐，更安全的方式是使用 SSH 密钥）：
```bash
export BACKMGR_SSH_PASSWORD="your-password"
```

### 自定义备份前/后脚本
在项目目录中创建 `.back-mgr/pre-backup.sh` 和 `.back-mgr/post-backup.sh`，会在备份前后自动执行。

## 相关技能

- 如果你需要在备份后通知某人，可以结合消息类技能使用
- 如果需要定时备份，可以使用 cron 技能设置定时任务
