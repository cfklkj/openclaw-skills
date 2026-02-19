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

## 安装技能

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

## 使用技能

重启后，OpenClaw 会自动加载新技能。你可以通过以下方式使用：

- 在对话中描述你的需求，AI 会自动调用相应的技能
- 查看技能的 README_USAGE.md 文件了解详细用法

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
