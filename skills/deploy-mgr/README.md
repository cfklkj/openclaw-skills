# Deploy Mgr - 远程服务部署管理工具

一个简单易用的命令行工具，用于管理远程服务器上的项目部署和运行状态。

## ✨ 特性

- 🚀 **简单快速**: 一键启动、停止、重启远程服务
- 🔒 **安全认证**: 支持密码和 SSH 密钥两种认证方式
- 📊 **状态监控**: 实时查看服务运行状态
- 📝 **日志查看**: 远程查看服务日志
- 💾 **数据持久化**: 自动保存部署配置到本地
- 🎯 **易于使用**: 直观的命令行界面

## 📦 安装

### 环境要求

- Python 3.8+
- Paramiko (SSH 库)
- Click (CLI 框架)

### 安装步骤

```bash
# 克隆项目
cd skills/deploy-mgr

# 安装依赖
pip install paramiko click

# 或使用 requirements.txt
pip install -r requirements.txt
```

## 🚀 快速开始

### 1. 添加部署

```bash
# 使用 SSH 密钥认证（推荐）
deploy-mgr add \
  --name myapp \
  --host server.com \
  --username deploy \
  --auth-type key \
  --auth-data ~/.ssh/id_rsa \
  --deploy-path /var/www/myapp \
  --start-command "npm start" \
  --stop-command "npm stop" \
  --log-path /var/log/myapp/app.log \
  --description "生产环境应用"
```

### 2. 列出所有部署

```bash
deploy-mgr list
```

输出：
```
====================================================================================================
ID    Name                 Host                      Path                          Description
====================================================================================================
1     myapp                server.com                /var/www/myapp                 生产环境应用

Total: 1 deployment(s)
```

### 3. 查看状态

```bash
deploy-mgr status myapp
```

输出：
```
============================================================
Status: myapp
============================================================
✅ Status:  RUNNING
📝 Message: Found 1 process(es) matching 'myapp'
============================================================
```

### 4. 启动/停止/重启服务

```bash
# 启动
deploy-mgr start myapp

# 停止
deploy-mgr stop myapp

# 重启
deploy-mgr restart myapp
```

### 5. 查看日志

```bash
# 查看最近 100 行日志
deploy-mgr logs myapp

# 查看最近 50 行
deploy-mgr logs myapp --lines 50
```

## 📖 详细文档

### 命令参考

#### deploy-mgr list
列出所有已配置的部署

```bash
deploy-mgr list
```

#### deploy-mgr info
查看部署详细信息

```bash
deploy-mgr info <name_or_id>
```

#### deploy-mgr add
添加新部署

参数：
- `--name`: 项目名称（必需）
- `--host`: 服务器地址（必需）
- `--port`: SSH 端口（默认 22）
- `--username`: 用户名（必需）
- `--auth-type`: 认证类型（password/key，默认 password）
- `--auth-data`: 密码或 SSH 密钥路径（必需）
- `--deploy-path`: 部署路径（必需）
- `--start-command`: 启动命令（可选）
- `--stop-command`: 停止命令（可选）
- `--status-command`: 状态检查命令（可选）
- `--log-path`: 日志文件路径（可选）
- `--description`: 描述信息（可选）

#### deploy-mgr update
更新部署配置

```bash
deploy-mgr update <name_or_id> [--option value]
```

#### deploy-mgr remove
删除部署

```bash
deploy-mgr remove <name_or_id>
```

#### deploy-mgr status
查看服务状态

```bash
deploy-mgr status <name_or_id>
```

#### deploy-mgr start
启动服务

```bash
deploy-mgr start <name_or_id>
```

#### deploy-mgr stop
停止服务

```bash
deploy-mgr stop <name_or_id>
```

#### deploy-mgr restart
重启服务

```bash
deploy-mgr restart <name_or_id>
```

#### deploy-mgr logs
查看日志

```bash
deploy-mgr logs <name_or_id> [--lines N]
```

## 🔧 配置

### 数据存储位置

部署配置存储在本地的 SQLite 数据库中：

- **Windows**: `C:\Users\<用户名>\.deploy-mgr\deployments.db`
- **Linux/Mac**: `~/.deploy-mgr/deployments.db`

### 认证方式

#### SSH 密钥认证（推荐）

```bash
deploy-mgr add \
  --auth-type key \
  --auth-data ~/.ssh/id_rsa \
  ...
```

优点：更安全，无需每次输入密码

#### 密码认证

```bash
deploy-mgr add \
  --auth-type password \
  --auth-data "your_password" \
  ...
```

注意：密码会明文存储，不建议在生产环境使用

## 💡 使用示例

### Node.js 应用

```bash
deploy-mgr add \
  --name node-app \
  --host server.com \
  --username node \
  --auth-type key \
  --auth-data ~/.ssh/id_rsa \
  --deploy-path /var/www/node-app \
  --start-command "node app.js" \
  --stop-command "pkill -f 'node app.js'" \
  --log-path /var/log/node-app/app.log
```

### Python 应用

```bash
deploy-mgr add \
  --name python-api \
  --host server.com \
  --username python \
  --auth-type key \
  --auth-data ~/.ssh/id_rsa \
  --deploy-path /var/www/python-api \
  --start-command "python3 app.py" \
  --stop-command "pkill -f 'python3 app.py'" \
  --log-path /var/log/python-api/app.log
```

### Docker 容器

```bash
deploy-mgr add \
  --name webapp \
  --host server.com \
  --username docker \
  --auth-type key \
  --auth-data ~/.ssh/id_rsa \
  --deploy-path /opt/webapp \
  --start-command "docker start webapp" \
  --stop-command "docker stop webapp" \
  --status-command "docker ps | grep webapp" \
  --log-path /var/log/webapp/container.log
```

## 🛠️ 高级用法

### 批量操作

使用 shell 脚本批量操作：

```bash
#!/bin/bash
# 批量启动所有服务
services=("api" "web" "worker")

for service in "${services[@]}"; do
  echo "Starting $service..."
  deploy-mgr start $service
done
```

### 定时检查

使用 cron 定时检查服务状态：

```bash
# 每分钟检查一次服务状态
* * * * * deploy-mgr status myapp >> /var/tmp/service-status.log
```

### 集成到 CI/CD

GitHub Actions 示例：

```yaml
- name: Deploy to production
  run: |
    deploy-mgr stop prod-app
    # 部署新版本
    deploy-mgr start prod-app
    deploy-mgr status prod-app
```

## 🐛 故障排查

### 连接失败

1. 检查服务器地址和端口
2. 确认 SSH 服务运行中
3. 验证认证信息（密码或密钥正确）
4. 检查网络连接
5. 查看防火墙设置

### 命令执行失败

1. 检查部署路径是否存在
2. 验证命令在服务器上是否可用
3. 确认用户有执行权限
4. 查看详细错误信息

### 日志文件未找到

1. 确认日志路径配置正确
2. 检查日志文件是否存在
3. 验证读取权限

## 🔒 安全建议

1. 使用 SSH 密钥认证而非密码
2. 确保 `.deploy-mgr` 目录权限正确
3. 定期审查部署配置
4. 不要在公共环境中使用密码认证
5. 使用最少权限原则配置远程用户

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- 项目主页: https://github.com/cfklkj/openclaw-skills
- 问题反馈: GitHub Issues

---

**版本**: 1.0.0
**更新**: 2026-02-20
