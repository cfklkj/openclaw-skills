"""
主上传工具模块
协调整个上传流程：压缩、上传、校验、解压
"""

import os
from pathlib import Path
from typing import Optional
from tqdm import tqdm
import json
import logging

from .compressor import Compressor
from .ssh_manager import SSHManager

logger = logging.getLogger(__name__)


class UploadTool:
    """主上传工具类"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化上传工具

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.compressor = None
        self.ssh_manager = None

    def _load_config(self, config_file: Optional[str]) -> dict:
        """
        加载配置文件

        Returns:
            配置字典
        """
        default_config = {
            'compression_format': 'zip',
            'cleanup_temp': True,
            'verify_upload': True,
            'retry_count': 3,
            'retry_delay': 5,
            'exclude_patterns': [
                '__pycache__',
                '.git',
                '*.pyc',
                '.DS_Store',
                'node_modules'
            ]
        }

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                logger.info(f"Loaded config from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")

        return default_config

    def run(self, local_path: str, remote_path: str,
            host: str, username: str, password: Optional[str] = None,
            key_file: Optional[str] = None, format: Optional[str] = None) -> bool:
        """
        执行上传任务

        Args:
            local_path: 本地文件/目录路径
            remote_path: 远程目录路径
            host: 服务器地址
            username: 用户名
            password: 密码
            key_file: SSH私钥文件
            format: 压缩格式

        Returns:
            bool: 任务是否成功
        """
        try:
            # 1. 压缩本地文件
            print(f"\n{'='*60}")
            print(f"Step 1: Compressing {local_path}...")
            print(f"{'='*60}")

            compress_format = format or self.config['compression_format']
            self.compressor = Compressor(
                local_path,
                compress_format,
                exclude_patterns=self.config.get('exclude_patterns', [])
            )

            archive_path, local_md5 = self.compressor.compress()
            print(f"✓ Compressed to: {archive_path}")
            print(f"✓ MD5: {local_md5}")

            # 2. 建立SSH连接
            print(f"\n{'='*60}")
            print(f"Step 2: Connecting to {host}...")
            print(f"{'='*60}")

            self.ssh_manager = SSHManager(
                host=host,
                username=username,
                password=password,
                key_file=key_file
            )

            if not self.ssh_manager.connect():
                self.cleanup(archive_path)
                return False

            print(f"✓ Connected successfully")

            # 3. 上传文件（带进度条）
            print(f"\n{'='*60}")
            print(f"Step 3: Uploading file...")
            print(f"{'='*60}")

            file_size = os.path.getsize(archive_path)
            remote_archive_path = f"/tmp/{archive_path.name}"

            with tqdm(total=file_size, unit='B', unit_scale=True,
                      desc="Uploading", unit_divisor=1024) as pbar:

                def progress_callback(chunk_size, total_size):
                    pbar.update(chunk_size)

                success = self.ssh_manager.upload_file_with_retry(
                    str(archive_path),
                    remote_archive_path,
                    callback=progress_callback,
                    retry_count=self.config['retry_count'],
                    retry_delay=self.config['retry_delay']
                )

            if not success:
                print("✗ Upload failed after retries")
                self.cleanup(archive_path)
                return False

            print(f"✓ Uploaded to: {remote_archive_path}")

            # 4. 验证上传（可选）
            if self.config['verify_upload']:
                print(f"\n{'='*60}")
                print(f"Step 4: Verifying upload...")
                print(f"{'='*60}")

                remote_md5 = self.ssh_manager.calculate_remote_md5(remote_archive_path)

                if remote_md5 and remote_md5 != local_md5:
                    print(f"✗ MD5 mismatch!")
                    print(f"  Local:  {local_md5}")
                    print(f"  Remote: {remote_md5}")
                    self.cleanup(archive_path)
                    return False

                print(f"✓ MD5 verification passed")

            # 5. 远程解压
            print(f"\n{'='*60}")
            print(f"Step 5: Extracting to {remote_path}...")
            print(f"{'='*60}")

            # 创建远程目录
            self.ssh_manager.execute_command(f"mkdir -p {remote_path}")

            if not self.ssh_manager.extract_archive(remote_archive_path, remote_path):
                print("✗ Extraction failed")
                self.cleanup(archive_path)
                return False

            print(f"✓ Extracted successfully")

            # 6. 清理临时文件
            print(f"\n{'='*60}")
            print(f"Step 6: Cleaning up...")
            print(f"{'='*60}")

            self.cleanup(archive_path)

            print(f"✓ Cleanup completed")

            # 完成
            print(f"\n{'='*60}")
            print(f"✓ Upload completed successfully!")
            print(f"{'='*60}")
            print(f"\nSummary:")
            print(f"  Source: {local_path}")
            print(f"  Destination: {host}:{remote_path}")
            print(f"  Format: {compress_format}")

            return True

        except KeyboardInterrupt:
            print("\n\nUpload interrupted by user")
            self.cleanup(archive_path)
            return False

        except Exception as e:
            print(f"\n✗ Error: {e}")
            logger.exception("Upload failed")
            try:
                self.cleanup(archive_path)
            except:
                pass
            return False

    def cleanup(self, archive_path: Optional[Path]):
        """
        清理临时文件

        Args:
            archive_path: 压缩包路径
        """
        # 清理本地临时文件
        if self.config.get('cleanup_temp') and self.compressor and archive_path:
            try:
                self.compressor.cleanup(archive_path)
                print(f"✓ Cleaned local temp file")
            except Exception as e:
                logger.error(f"Failed to cleanup local file: {e}")

        # 关闭SSH连接
        if self.ssh_manager:
            try:
                self.ssh_manager.close()
            except Exception as e:
                logger.error(f"Failed to close SSH connection: {e}")
