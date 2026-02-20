"""
命令行接口模块
提供用户友好的命令行界面
"""

import click
import logging
import sys
from .uploader import UploadTool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@click.command()
@click.option('-l', '--local', 'local_path', required=True,
              help='本地文件或目录路径')
@click.option('-r', '--remote', 'remote_path', required=True,
              help='远程目录路径')
@click.option('-s', '--server', 'host', required=True,
              help='远程服务器地址')
@click.option('-u', '--user', 'username', required=True,
              help='用户名')
@click.option('-p', '--password', 'password', help='密码（与SSH密钥二选一）')
@click.option('-k', '--key', 'key_file', help='SSH私钥文件路径（与密码二选一）')
@click.option('-f', '--format', 'format_', type=click.Choice(['zip', 'tar.gz']),
              help='压缩格式：zip 或 tar.gz')
@click.option('--config', 'config_file', help='配置文件路径')
@click.option('--verify/--no-verify', 'verify', default=True,
              help='是否进行MD5校验（默认开启）')
@click.version_option(version='1.0.0')
def main(local_path, remote_path, host, username, password, key_file,
         format_, config_file, verify):
    """
    Upload Tool - 文件压缩上传工具

    压缩本地文件/目录并通过SSH上传到远程服务器，自动解压。

    基本用法示例：

      \b
      # 使用密码认证
      upload-tool -l ./project -r /var/www -s server.com -u username -p password

      # 使用SSH密钥认证
      upload-tool -l ./data -r /remote/data -s server.com -u user -k ~/.ssh/id_rsa

      # 指定压缩格式
      upload-tool -l ./docs -r /var/docs -s server.com -u user -f tar.gz

      # 使用配置文件
      upload-tool -l ./project -r /var/www -s server.com -u user --config config.json
    """
    # 验证认证方式
    if not password and not key_file:
        click.echo("错误：必须提供密码或SSH密钥文件", err=True)
        click.echo("使用 -p 提供密码或 -k 指定SSH密钥文件", err=True)
        sys.exit(1)

    # 创建上传工具实例
    tool = UploadTool(config_file)
    tool.config['verify_upload'] = verify

    # 执行上传
    success = tool.run(
        local_path=local_path,
        remote_path=remote_path,
        host=host,
        username=username,
        password=password,
        key_file=key_file,
        format=format_
    )

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
