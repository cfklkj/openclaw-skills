"""
快速开始示例
演示如何使用 Upload Tool
"""

from src.uploader import UploadTool


def example_with_password():
    """示例1：使用密码认证上传"""
    print("示例1：使用密码认证")
    print("-" * 60)

    tool = UploadTool()

    success = tool.run(
        local_path="./myproject",
        remote_path="/var/www/html",
        host="server.com",
        username="username",
        password="your_password"
    )

    if success:
        print("上传成功！")
    else:
        print("上传失败！")


def example_with_ssh_key():
    """示例2：使用SSH密钥认证上传"""
    print("\n示例2：使用SSH密钥认证")
    print("-" * 60)

    tool = UploadTool()

    success = tool.run(
        local_path="./data",
        remote_path="/remote/data",
        host="server.com",
        username="username",
        key_file="~/.ssh/id_rsa",
        format="tar.gz"  # 使用 tar.gz 格式
    )

    if success:
        print("上传成功！")
    else:
        print("上传失败！")


def example_with_config():
    """示例3：使用配置文件上传"""
    print("\n示例3：使用配置文件")
    print("-" * 60)

    tool = UploadTool(config_file="config/default_config.json")

    success = tool.run(
        local_path="./docs",
        remote_path="/var/docs",
        host="server.com",
        username="username",
        key_file="~/.ssh/id_rsa"
    )

    if success:
        print("上传成功！")
    else:
        print("上传失败！")


def example_skip_verification():
    """示例4：跳过MD5校验（提速）"""
    print("\n示例4：跳过MD5校验")
    print("-" * 60)

    tool = UploadTool()
    tool.config['verify_upload'] = False

    success = tool.run(
        local_path="./large_files",
        remote_path="/data/large_files",
        host="server.com",
        username="username",
        key_file="~/.ssh/id_rsa"
    )

    if success:
        print("上传成功！")
    else:
        print("上传失败！")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Upload Tool - 快速开始示例")
    print("="*60 + "\n")

    # 注意：这些示例需要您修改实际的路径和服务器信息
    print("注意：请修改示例中的实际路径和服务器信息后再运行！\n")

    # 取消注释你想运行的示例：
    # example_with_password()
    # example_with_ssh_key()
    # example_with_config()
    # example_skip_verification()
