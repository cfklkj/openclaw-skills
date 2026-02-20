"""
SSH管理器单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ssh_manager import SSHManager


class TestSSHManager(unittest.TestCase):

    def setUp(self):
        """创建测试环境"""
        self.ssh_manager = SSHManager(
            host='test-server',
            username='test-user',
            password='test-password'
        )

    @patch('ssh_manager.paramiko.SSHClient')
    def test_connect_with_password(self, mock_ssh_client_class):
        """测试使用密码连接"""
        # 设置mock
        mock_client = Mock()
        mock_ssh_client_class.return_value = mock_client

        # 调用连接
        result = self.ssh_manager.connect()

        # 验证
        self.assertTrue(result)
        mock_client.connect.assert_called_once()

    @patch('ssh_manager.paramiko.SSHClient')
    @patch('ssh_manager.paramiko.RSAKey')
    def test_connect_with_key(self, mock_rsa_key, mock_ssh_client_class):
        """测试使用SSH密钥连接"""
        # 设置mock
        mock_client = Mock()
        mock_key = Mock()
        mock_ssh_client_class.return_value = mock_client
        mock_rsa_key.from_private_key_file.return_value = mock_key

        # 创建使用密钥的SSH管理器
        ssh_manager = SSHManager(
            host='test-server',
            username='test-user',
            key_file='/path/to/key'
        )

        # 调用连接
        result = ssh_manager.connect()

        # 验证
        self.assertTrue(result)
        mock_rsa_key.from_private_key_file.assert_called_once_with('/path/to/key')

    @patch('ssh_manager.paramiko.SSHClient')
    def test_execute_command(self, mock_ssh_client_class):
        """测试执行远程命令"""
        # 设置mock
        mock_client = Mock()
        mock_ssh_client_class.return_value = mock_client

        # Mock exec_command返回值
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdout.read.return_value = b'output'
        mock_stderr.read.return_value = b'error'
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        # 建立连接
        self.ssh_manager.client = mock_client

        # 执行命令
        stdout, stderr = self.ssh_manager.execute_command('ls -la')

        # 验证
        self.assertEqual(stdout, 'output')
        self.assertEqual(stderr, 'error')
        mock_client.exec_command.assert_called_once_with('ls -la')

    @patch('ssh_manager.paramiko.SSHClient')
    def test_calculate_remote_md5(self, mock_ssh_client_class):
        """测试计算远程文件MD5"""
        # 设置mock
        mock_client = Mock()
        mock_ssh_client_class.return_value = mock_client

        # Mock exec_command返回值
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdout.read.return_value = b'abc123def456  /path/to/file\n'
        mock_stderr.read.return_value = b''
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        # 建立连接
        self.ssh_manager.client = mock_client

        # 计算MD5
        md5 = self.ssh_manager.calculate_remote_md5('/path/to/file')

        # 验证
        self.assertEqual(md5, 'abc123def456')

    @patch('ssh_manager.paramiko.SSHClient')
    def test_extract_archive_zip(self, mock_ssh_client_class):
        """测试解压ZIP文件"""
        # 设置mock
        mock_client = Mock()
        mock_ssh_client_class.return_value = mock_client

        # Mock exec_command返回值
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdout.read.return_value = b''
        mock_stderr.read.return_value = b''
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        # 建立连接
        self.ssh_manager.client = mock_client

        # 解压文件
        result = self.ssh_manager.extract_archive('/tmp/file.zip', '/tmp/extract')

        # 验证
        self.assertTrue(result)
        mock_client.exec_command.assert_called()

    @patch('ssh_manager.paramiko.SSHClient')
    def test_extract_archive_targz(self, mock_ssh_client_class):
        """测试解压TAR.GZ文件"""
        # 设置mock
        mock_client = Mock()
        mock_ssh_client_class.return_value = mock_client

        # Mock exec_command返回值
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdout.read.return_value = b''
        mock_stderr.read.return_value = b''
        mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        # 建立连接
        self.ssh_manager.client = mock_client

        # 解压文件
        result = self.ssh_manager.extract_archive('/tmp/file.tar.gz', '/tmp/extract')

        # 验证
        self.assertTrue(result)

    @patch('ssh_manager.paramiko.SSHClient')
    def test_close(self, mock_ssh_client_class):
        """测试关闭连接"""
        # 设置mock
        mock_scp = Mock()
        mock_client = Mock()
        mock_ssh_client_class.return_value = mock_client

        # 设置SCP和Client
        self.ssh_manager.scp = mock_scp
        self.ssh_manager.client = mock_client

        # 关闭连接
        self.ssh_manager.close()

        # 验证
        mock_scp.close.assert_called_once()
        mock_client.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
