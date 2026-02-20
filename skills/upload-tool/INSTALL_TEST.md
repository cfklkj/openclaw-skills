# Upload Tool - 安装和测试指南

## 快速开始

### 1. 安装步骤

```bash
# 进入项目目录
cd H:\tzj\pro2026\插件规划\2月\19\skills\upload-tool

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装（可选）
pip install -e .
```

**安装完成后，可以在任何位置使用 `upload-tool` 命令。**

### 2. 验证安装

```bash
# 检查版本
upload-tool --version

# 查看帮助
upload-tool --help
```

## 测试

### 运行单元测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_compressor.py -v
python -m pytest tests/test_ssh_manager.py -v

# 查看测试覆盖率
python -m pytest tests/ --cov=src --cov-report=html
```

### 手动测试

#### 测试1：压缩功能

```python
from src.compressor import Compressor

# 压缩单个文件
compressor = Compressor("./test.txt", "zip")
archive_path, md5 = compressor.compress()
print(f"压缩完成: {archive_path}, MD5: {md5}")

# 清理
compressor.cleanup(archive_path)
```

#### 测试2：SSH连接（需要真实服务器）

```python
from src.ssh_manager import SSHManager

ssh = SSHManager(
    host="your-server.com",
    username="your-username",
    key_file="~/.ssh/id_rsa"
)

if ssh.connect():
    print("连接成功！")
    stdout, stderr = ssh.execute_command("ls -la")
    print(stdout)
    ssh.close()
else:
    print("连接失败！")
```

## 功能演示

### 演示1：基本用法

```bash
# 使用密码认证
upload-tool -l ./test -r /tmp/test -s local-server -u test -p test123
```

### 演示2：SSH密钥认证（推荐）

```bash
# 使用SSH密钥
upload-tool -l ./test -r /tmp/test -s local-server -u test -k ~/.ssh/id_rsa
```

### 演示3：自定义配置

```bash
# 使用配置文件
upload-tool -l ./test -r /tmp/test -s local-server -u test -k ~/.ssh/id_rsa --config config/default_config.json
```

## 配置说明

### 创建自定义配置文件

```bash
# 创建项目配置文件
cat > myconfig.json << EOF
{
    "compression_format": "tar.gz",
    "cleanup_temp": true,
    "verify_upload": true,
    "retry_count": 5,
    "retry_delay": 10,
    "exclude_patterns": [
        "*.log",
        "temp",
        "*.tmp"
    ]
}
EOF

# 使用自定义配置
upload-tool -l ./project -r /var/www -s server.com -u user -k ~/.ssh/id_rsa --config myconfig.json
```

## 常见问题

### Q1: 安装失败

**问题**: `pip install -r requirements.txt` 失败

**解决方案**:
```bash
# 更新pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 连接超时

**问题**: SSH连接超时

**解决方案**:
1. 检查网络连接
2. 检查服务器地址和端口
3. 检查防火墙设置
4. 尝试增加超时时间（修改ssh_manager.py中的timeout参数）

### Q3: 权限错误

**问题**: 无法写入临时目录

**解决方案**:
```python
# 修改临时目录（在compressor.py中）
self.temp_dir = Path(os.environ.get('TEMP', 'C:\\temp')) / 'upload_tool'
```

### Q4: 远程解压失败

**问题**: 解压命令不存在

**解决方案**:
```bash
# 在远程服务器上安装必要的工具
sudo apt-get install unzip tar  # Ubuntu/Debian
sudo yum install unzip tar      # CentOS/RHEL
brew install unzip              # macOS
```

## 日志调试

### 启用详细日志

编辑 `src/cli.py`，修改日志级别：

```python
# 修改前
logging.basicConfig(level=logging.INFO, ...)

# 修改后
logging.basicConfig(level=logging.DEBUG, ...)
```

### 查看日志

运行命令时会实时输出日志，包括：
- 压缩进度
- 连接状态
- 上传进度
- MD5校验结果
- 解压状态

## 性能优化建议

### 1. 跳过MD5校验（提速20-30%）

```bash
upload-tool -l ./largefiles -r /remote/path -s server.com -u user -k ~/.ssh/id_rsa --no-verify
```

### 2. 使用更快的压缩格式

TAR.GZ 通常比 ZIP 压缩率更高，但速度稍慢：
```bash
upload-tool -l ./project -r /var/www -s server.com -u user -k ~/.ssh/id_rsa -f tar.gz
```

### 3. 调整重试策略

在配置文件中减少重试次数可以节省时间：
```json
{
    "retry_count": 1,
    "retry_delay": 2
}
```

## 卸载

```bash
# 卸载工具
pip uninstall upload-tool

# 选择性清理
rm -rf ~/.uploadtool  # 如果存在配置目录
```

## 下一步

1. 阅读 [README.md](README.md) 了解完整功能
2. 查看 [examples/quick_start.py](examples/quick_start.py) 学习更多示例
3. 查看 [SKILL.md](SKILL.md) 了解OpenClaw集成

## 获取帮助

如有问题：
1. 查看日志输出
2. 启用DEBUG模式
3. 查阅文档
4. 联系开发者

---

**提示**: 首次使用建议在测试环境验证，确认无误后再在生产环境使用。
