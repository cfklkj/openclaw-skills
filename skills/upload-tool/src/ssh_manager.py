"""
SSH连接管理模块
处理SSH连接、文件上传和远程命令执行
"""

import paramiko
from scp import SCPClient
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SSHManager:
    """SSH连接管理器"""

    def __init__(self, host: str, username: str, password: Optional[str] = None,
                 key_file: Optional[str] = None, port: int = 22):
        """
        初始化SSH管理器

        Args:
            host: 服务器地址
            username: 用户名
            password: 密码（与key_file二选一）
            key_file: SSH私钥文件路径（与password二选一）
            port: SSH端口，默认22
        """
        self.host = host
        self.username = username
        self.password = password
        self.key_file = key_file
        self.port = port
        self.client = None
        self.scp = None

    def connect(self) -> bool:
        """
        建立SSH连接

        Returns:
            bool: 连接是否成功
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.key_file:
                key = paramiko.RSAKey.from_private_key_file(self.key_file)
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=key,
                    timeout=30
                )
                logger.info(f"Connected to {self.host} using SSH key")
            else:
                if not self.password:
                    raise ValueError("Password or SSH key file is required")
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=30
                )
                logger.info(f"Connected to {self.host} using password")

            self.scp = SCPClient(self.client.get_transport())
            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def upload_file(self, local_path: str, remote_path: str,
                   callback: Optional[callable] = None) -> bool:
        """
        上传文件

        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径
            callback: 进度回调函数

        Returns:
            bool: 上传是否成功
        """
        try:
            self.scp.put(local_path, remote_path, callback=callback)
            logger.info(f"File uploaded: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    def upload_file_with_retry(self, local_path: str, remote_path: str,
                              callback: Optional[callable] = None,
                              retry_count: int = 3, retry_delay: int = 5) -> bool:
        """
        带重试的文件上传

        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径
            callback: 进度回调函数
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）

        Returns:
            bool: 上传是否成功
        """
        import time

        for attempt in range(retry_count):
            if self.upload_file(local_path, remote_path, callback):
                return True

            if attempt < retry_count - 1:
                logger.warning(f"Upload failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)

        return False

    def execute_command(self, command: str) -> Tuple[str, str]:
        """
        执行远程命令

        Args:
            command: 要执行的命令

        Returns:
            (stdout, stderr)
        """
        stdin, stdout, stderr = self.client.exec_command(command)
        stdout_str = stdout.read().decode()
        stderr_str = stderr.read().decode()
        return stdout_str, stderr_str

    def extract_archive(self, remote_path: str, extract_to: str) -> bool:
        """
        远程解压文件

        修复：直接在 extract_to 目录下解压，避免双重嵌套

        Args:
            remote_path: 远程压缩包路径
            extract_to: 解压目标目录

        Returns:
            bool: 解压是否成功
        """
        try:
            # 根据文件扩展名选择解压命令
            # 直接在 extract_to 目录下解压，压缩包内的目录会保留
            if remote_path.endswith('.zip'):
                # 使用 cd 确保解压到正确位置，避免双重嵌套
                cmd = f"cd {extract_to} && unzip -o {remote_path} && rm {remote_path}"
            elif remote_path.endswith('.tar.gz') or remote_path.endswith('.tgz'):
                cmd = f"cd {extract_to} && tar -xzf {remote_path} && rm {remote_path}"
            else:
                raise ValueError(f"Unsupported archive format: {remote_path}")

            stdout, stderr = self.execute_command(cmd)

            if stderr and not stderr.strip().endswith('removing:'):
                logger.warning(f"Extraction warning: {stderr}")

            logger.info(f"Extracted {remote_path} to {extract_to}")
            return True

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return False

    def calculate_remote_md5(self, remote_path: str) -> Optional[str]:
        """
        计算远程文件的MD5

        Args:
            remote_path: 远程文件路径

        Returns:
            MD5值，失败返回None
        """
        try:
            stdout, stderr = self.execute_command(f"md5sum {remote_path}")
            if stdout:
                return stdout.split()[0]
        except Exception as e:
            logger.error(f"Failed to calculate remote MD5: {e}")
        return None

    def close(self):
        """关闭连接"""
        try:
            if self.scp:
                self.scp.close()
            if self.client:
                self.client.close()
            logger.info("SSH connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
