"""
部署管理核心模块
管理所有部署操作
"""

import logging
from typing import List, Dict, Optional
from .storage import Storage
from .ssh_client import SSHClient

logger = logging.getLogger(__name__)


class DeploymentManager:
    """部署管理器类"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化部署管理器

        Args:
            db_path: 数据库文件路径
        """
        self.storage = Storage(db_path)
        self.connections = {}

    def list_deployments(self) -> List[Dict]:
        """
        列出所有部署

        Returns:
            部署列表
        """
        deployments = self.storage.list_deployments()

        # 返回敏感信息（auth_data）已过滤的数据
        safe_deployments = []
        for dep in deployments:
            safe_dep = dep.copy()
            safe_dep['auth_data'] = '***' if dep.get('auth_type') == 'password' else '*** KEY ***'
            safe_deployments.append(safe_dep)

        return safe_deployments

    def get_deployment(self, identifier: str, include_auth: bool = False) -> Optional[Dict]:
        """
        获取部署信息

        Args:
            identifier: 部署名称或ID
            include_auth: 是否包含认证信息

        Returns:
            部署信息字典
        """
        deployment = self.storage.get_deployment(identifier)

        if deployment and not include_auth:
            # 返回前过滤敏感信息
            deployment['auth_data'] = '***' if deployment.get('auth_type') == 'password' else '*** KEY ***'

        return deployment

    def add_deployment(self, name: str, host: str, port: int, username: str,
                      auth_type: str, auth_data: str, deploy_path: str,
                      start_command: str = None, stop_command: str = None,
                      status_command: str = None, log_path: str = None,
                      description: str = None) -> int:
        """
        添加部署

        Args:
            name: 项目名称
            host: 服务器地址
            port: SSH 端口
            username: 用户名
            auth_type: 认证类型 (password/key)
            auth_data: 密码或密钥路径
            deploy_path: 部署路径
            start_command: 启动命令
            stop_command: 停止命令
            status_command: 状态检查命令
            log_path: 日志路径
            description: 描述信息

        Returns:
            新部署的ID
        """
        deployment = {
            'name': name,
            'host': host,
            'port': port,
            'username': username,
            'auth_type': auth_type,
            'auth_data': auth_data,
            'deploy_path': deploy_path,
            'start_command': start_command,
            'stop_command': stop_command,
            'status_command': status_command,
            'log_path': log_path,
            'description': description
        }

        deployment_id = self.storage.add_deployment(deployment)
        logger.info(f"Added deployment: {name} (ID: {deployment_id})")

        return deployment_id

    def update_deployment(self, identifier: str, **kwargs) -> bool:
        """
        更新部署信息

        Args:
            identifier: 部署名称或ID
            **kwargs: 要更新的字段

        Returns:
            是否成功
        """
        success = self.storage.update_deployment(identifier, kwargs)

        if success:
            logger.info(f"Updated deployment: {identifier}")

        return success

    def remove_deployment(self, identifier: str) -> bool:
        """
        删除部署

        Args:
            identifier: 部署名称或ID

        Returns:
            是否成功
        """
        success = self.storage.remove_deployment(identifier)

        if success:
            logger.info(f"Removed deployment: {identifier}")

        return success

    def _get_ssh_client(self, deployment_id: int) -> Optional[SSHClient]:
        """
        获取或创建 SSH 客户端连接

        Args:
            deployment_id: 部署ID

        Returns:
            SSH 客户端实例
        """
        if deployment_id in self.connections:
            return self.connections[deployment_id]

        deployment = self.storage.get_deployment(deployment_id)
        if not deployment:
            return None

        client = SSHClient(
            host=deployment['host'],
            port=deployment['port'],
            username=deployment['username'],
            auth_type=deployment['auth_type'],
            auth_data=deployment['auth_data']
        )

        if client.connect():
            self.connections[deployment_id] = client
            return client

        return None

    def get_status(self, identifier: str) -> Dict:
        """
        获取部署状态

        Args:
            identifier: 部署名称或ID

        Returns:
            状态信息字典
        """
        deployment = self.storage.get_deployment(identifier)
        if not deployment:
            raise ValueError(f"Deployment not found: {identifier}")

        client = self._get_ssh_client(deployment['id'])
        if not client:
            return {
                'name': deployment['name'],
                'status': 'unknown',
                'message': 'Failed to connect to server'
            }

        # 使用自定义状态命令或默认检查
        if deployment.get('status_command'):
            exit_code, stdout, stderr = client.execute_command(deployment['status_command'])
            status = "running" if exit_code == 0 else "stopped"
            message = stdout or stderr
        else:
            # 从部署路径或进程名推断
            process_name = deployment['name']
            count, status = client.check_process_status(process_name)
            message = f"Found {count} process(es) matching '{process_name}'"

        self.storage.log_operation(deployment['id'], 'status', 'success', message)

        return {
            'name': deployment['name'],
            'status': status,
            'message': message
        }

    def start_service(self, identifier: str) -> Dict:
        """
        启动服务

        Args:
            identifier: 部署名称或ID

        Returns:
            操作结果
        """
        deployment = self.storage.get_deployment(identifier)
        if not deployment:
            raise ValueError(f"Deployment not found: {identifier}")

        if not deployment.get('start_command'):
            raise ValueError(f"No start_command configured for {identifier}")

        client = self._get_ssh_client(deployment['id'])
        if not client:
            return {
                'success': False,
                'name': deployment['name'],
                'message': 'Failed to connect to server'
            }

        # 切换到部署目录并执行启动命令
        command = f"cd {deployment['deploy_path']} && {deployment['start_command']}"
        exit_code, stdout, stderr = client.execute_command(command)

        success = exit_code == 0
        message = stdout or stderr or "Command executed"

        self.storage.log_operation(
            deployment['id'],
            'start',
            'success' if success else 'failed',
            message
        )

        return {
            'success': success,
            'name': deployment['name'],
            'exit_code': exit_code,
            'message': message
        }

    def stop_service(self, identifier: str) -> Dict:
        """
        停止服务

        Args:
            identifier: 部署名称或ID

        Returns:
            操作结果
        """
        deployment = self.storage.get_deployment(identifier)
        if not deployment:
            raise ValueError(f"Deployment not found: {identifier}")

        if not deployment.get('stop_command'):
            raise ValueError(f"No stop_command configured for {identifier}")

        client = self._get_ssh_client(deployment['id'])
        if not client:
            return {
                'success': False,
                'name': deployment['name'],
                'message': 'Failed to connect to server'
            }

        # 切换到部署目录并执行停止命令
        command = f"cd {deployment['deploy_path']} && {deployment['stop_command']}"
        exit_code, stdout, stderr = client.execute_command(command)

        success = exit_code == 0
        message = stdout or stderr or "Command executed"

        self.storage.log_operation(
            deployment['id'],
            'stop',
            'success' if success else 'failed',
            message
        )

        return {
            'success': success,
            'name': deployment['name'],
            'exit_code': exit_code,
            'message': message
        }

    def restart_service(self, identifier: str) -> Dict:
        """
        重启服务

        Args:
            identifier: 部署名称或ID

        Returns:
            操作结果
        """
        deployment = self.storage.get_deployment(identifier)
        if not deployment:
            raise ValueError(f"Deployment not found: {identifier}")

        # 先停止
        stop_result = self.stop_service(identifier)

        if not stop_result['success']:
            return {
                'success': False,
                'name': deployment['name'],
                'message': f"Failed to stop service: {stop_result['message']}"
            }

        # 再启动
        start_result = self.start_service(identifier)

        return {
            'success': start_result['success'],
            'name': deployment['name'],
            'message': start_result['message']
        }

    def get_logs(self, identifier: str, lines: int = 100) -> Dict:
        """
        获取日志

        Args:
            identifier: 部署名称或ID
            lines: 获取的行数

        Returns:
            日志内容
        """
        deployment = self.storage.get_deployment(identifier)
        if not deployment:
            raise ValueError(f"Deployment not found: {identifier}")

        if not deployment.get('log_path'):
            raise ValueError(f"No log_path configured for {identifier}")

        client = self._get_ssh_client(deployment['id'])
        if not client:
            return {
                'success': False,
                'name': deployment['name'],
                'message': 'Failed to connect to server'
            }

        logs = client.tail_file(deployment['log_path'], lines)

        return {
            'success': True,
            'name': deployment['name'],
            'log_path': deployment['log_path'],
            'logs': logs
        }

    def close_all(self):
        """关闭所有 SSH 连接"""
        for client in self.connections.values():
            client.close()

        self.connections.clear()
        logger.info("All SSH connections closed")
