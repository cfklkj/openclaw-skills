# OpenClaw Skills

OpenClaw 技能集合，用于扩展 OpenClaw AI 代理的能力。

## 关于本项目

这个仓库包含各种自定义技能，每个技能都是一个独立的模块，可以为 OpenClaw 代理提供特定领域的能力和工作流程。

## 包含的技能

### routerModel

**自定义模型管理技能**

- **描述**: 提供模型的增删查改和应用功能，管理多个AI模型提供商的API密钥和模型配置
- **功能**:
  - 添加、更新、删除自定义模型配置
  - 按提供商搜索和筛选模型
  - 一键列出所有已配置的模型
  - 将模型应用到当前 OpenClaw 会话
- **支持提供商**: NVIDIA、OpenAI、Anthropic 等
- **详情**: 见 [skills/routerModel/README_USAGE.md](skills/routerModel/README_USAGE.md)

### Upload Tool

**文件压缩上传工具**

- **描述**: 高效的本地文件压缩上传工具，通过SSH自动压缩、上传并解压文件到远程服务器
- **功能**:
  - 自动压缩单个文件或整个目录（支持 ZIP 和 TAR.GZ 格式）
  - 通过 SSH/SFTP 安全传输文件
  - 远程自动解压到指定目录
  - 实时显示压缩和上传进度
  - MD5 完整性校验
  - 断点续传和重试机制
  - 支持密码和 SSH 密钥两种认证方式
  - 灵活的配置文件支持
  - 文件排除模式（可排除 node_modules、.git 等）
- **适用场景**:
  - Web 项目部署
  - 数据备份传输
  - 大批量文件上传
  - 运维自动化
- **技术栈**: Python 3.8+, Paramiko, SCP, tqdm, Click
- **详情**: 见 [skills/upload-tool/README.md](skills/upload-tool/README.md)
- **快速开始**: 见 [skills/upload-tool/INSTALLATION_NOTE.md](skills/upload-tool/INSTALLATION_NOTE.md)

**使用示例**:
```bash
# 使用SSH密钥上传
upload-tool -l ./project -r /var/www -s server.com -u user -k ~/.ssh/id_rsa

# 使用密码上传
upload-tool -l ./data -r /remote/data -s server.com -u user -p password

# 指定压缩格式
upload-tool -l ./docs -r /var/docs -s server.com -u user -f tar.gz
```

## 安装技能

### routerModel

1. 克隆本仓库：
   ```bash
   git clone https://github.com/cfklkj/openclaw-skills.git
   ```

2. 将技能文件夹复制到 OpenClaw 的技能目录：
   ```bash
   cp -r openclaw-skills/skills/routerModel ~/.openclaw/skills/
   ```

3. 重启 OpenClaw Gateway：
   ```bash
   openclaw gateway restart
   ```

### Upload Tool

1. 将技能文件夹复制到 OpenClaw 的技能目录：
   ```bash
   cp -r openclaw-skills/skills/upload-tool ~/.openclaw/skills/
   ```

2. 安装 Python 依赖：
   ```bash
   cd ~/.openclaw/skills/upload-tool
   pip install -r requirements.txt
   ```

3. 可选：安装为全局命令（方便直接使用）：
   ```bash
   pip install -e .
   ```

4. 重启 OpenClaw Gateway（如果需要在 OpenClow 中使用）：
   ```bash
   openclaw gateway restart
   ```

## 使用技能

重启后，OpenClaw 会自动加载新技能。你可以通过以下方式使用：

### routerModel

**对话示例**:
```
用户: 帮我添加一个新的模型，提供商是 test，API密钥是 test-key，模型名称是 test/model,  baseUrl是 https://xxx/v1

用户: 列出我所有的模型

用户: 把默认模型切换到 nvidia/nemotron-3-nano-30b-a3b

用户: 查看当前使用的是什么模型
```

### Upload Tool

**通过命令行使用**:
```bash
# 使用SSH密钥上传
upload-tool -l ./project -r /var/www -s server.com -u user -k ~/.ssh/id_rsa

# 使用密码上传
upload-tool -l ./data -r /remote/data -s server.com -u user -p password

# 指定压缩格式
upload-tool -l ./docs -r /var/docs -s server.com -u user -f tar.gz

# 查看帮助
upload-tool --help
```

**通过 OpenClaw 使用**:
```
用户: 帮我把 ./myproject 目录上传到 server.com 的 /var/www

用户: 上传本地文件 ./data 到远程服务器 example.com 的 /backup 目录

用户: 把项目打包上传到测试服务器
```

### 通用使用方式

- 在对话中描述你的需求，AI 会自动调用相应的技能
- 查看技能的 README.md 和相关文档了解详细用法
- 对于具有命令行接口的技能（如 upload-tool），可以直接在终端运行

## 开发技能

如果你想添加新技能：

1. 在 `skills/` 目录下创建新的技能文件夹
2. 创建 `SKILL.md` 文件（必需）：
   ```yaml
   ---
   name: your-skill-name
   description: 描述技能的功能和使用场景
   ---
   ```
3. 根据需要添加脚本、资源等文件
4. 提交你的技能到本仓库

## 贡献

欢迎提交 PR 或 Issue 来改进现有技能或添加新技能！

## 许可证

本项目采用 MIT 许可证。

---

**仓库维护者**: [cfklkj](https://github.com/cfklkj)
**OpenClaw 官网**: [https://github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
