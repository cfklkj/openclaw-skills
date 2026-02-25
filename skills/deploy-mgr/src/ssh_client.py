"""SSH 客户端模块 - 管理 SSH 连接和远程命令执行"""

import paramiko
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SSHClient:
    """SSH 连接管理类"""
    
    def __init__(self, host: str, port: int, username: str, auth_type: str, auth_data: str, timeout: int = 30):
        """
        初始化 SSH 客户端
        
        Args:
            host: 服务器地址
            port: SSH 端口
            username: 用户名
            auth_type: 认证类型 (password/key)
            auth_data: 密码或密钥路径
            timeout: 连接超时（秒）
        """
        self.host = host
        self.port = port
        self.username = username
        self.auth_type = auth_type
        self.auth_data = auth_data
        self.timeout = timeout
        self.client = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        建立 SSH 连接
        
        Returns:
            是否连接成功
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.auth_type == 'key':
                # 使用 SSH 密钥认证
                key_path = Path(self.auth_data).expanduser()
                if not key_path.exists():
                    raise FileNotFoundError(f"SSH key file not found: {key_path}")
                
                # 支持多种密钥类型：RSA, ED25519, ECDSA
                key = None
                key_errors = []
                for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]:
                    try:
                        key = key_class.from_private_key_file(str(key_path))
                        break
                    except Exception as e:
                        key_errors.append(f"{key_class.__name__}: {e}")
                
                if key is None:
                    raise ValueError(f"Failed to load SSH key. Tried: {'; '.join(key_errors)}")
                
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=key,
                    timeout=self.timeout
                )
                logger.info(f"Connected to {self.host}:{self.port} using SSH key")
            else:
                # 使用密码认证
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.auth_data,
                    timeout=self.timeout
                )
                logger.info(f"Connected to {self.host}:{self.port} using password")
            
            self._connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
            return False
    
    def execute_command(self, command: str, timeout: int = 30) -> Tuple[int, str, str]:
        """
        执行远程命令
        
        Args:
            command: 要执行的命令
            timeout: 命令超时（秒）
            
        Returns:
            (退出码, 标准输出, 标准错误)
        """
        if not self._connected:
            raise ConnectionError("Not connected to remote server")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            
            # 读取输出
            stdout_str = stdout.read().decode('utf-8', errors='ignore')
            stderr_str = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()
            
            return exit_code, stdout_str, stderr_str
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return -1, "", str(e)
    
    def execute_command_with_output(self, command: str, timeout: int = 30) -> str:
        """
        执行命令并返回输出（忽略错误）
        
        Args:
            command: 要执行的命令
            timeout: 命令超时（秒）
            
        Returns:
            命令输出
        """
        exit_code, stdout, stderr = self.execute_command(command, timeout)
        if exit_code != 0 and stderr:
            return stdout + stderr
        return stdout
    
    def check_process_status(self, process_name: str) -> Tuple[int, str]:
        """
        检查进程状态
        
        Args:
            process_name: 进程名称
            
        Returns:
            (进程数量, 状态信息)
        """
        # 使用 ps 命令检查进程
        command = f"ps aux | grep -v grep | grep -i '{process_name}' | wc -l"
        exit_code, stdout, stderr = self.execute_command(command)
        
        try:
            count = int(stdout.strip())
            status = "running" if count > 0 else "stopped"
            return count, status
        except:
            return 0, "unknown"
    
    def tail_file(self, file_path: str, lines: int = 100) -> str:
        """
        获取文件尾部内容
        
        Args:
            file_path: 文件路径
            lines: 要获取的行数
            
        Returns:
            文件内容
        """
        command = f"tail -n {lines} {file_path}"
        return self.execute_command_with_output(command)
    
    def read_file(self, file_path: str) -> str:
        """
        读取远程文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        command = f"cat {file_path}"
        return self.execute_command_with_output(command)
    
    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info(f"Connection to {self.host}:{self.port} closed")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
