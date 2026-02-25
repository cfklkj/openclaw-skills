"""数据存储模块 - 管理部署信息持久化存储"""

import sqlite3
from typing import List, Dict, Optional
from pathlib import Path


class Storage:
    """数据存储管理类"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化存储管理器

        Args:
            db_path: 数据库文件路径
        """
        if db_path:
            self.db_path = db_path
        else:
            # 默认使用用户主目录下的 .deploy-mgr 目录
            home_dir = Path.home()
            self.db_dir = home_dir / ".deploy-mgr"
            self.db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(self.db_dir / "deployments.db")
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建部署表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                host TEXT NOT NULL,
                port INTEGER DEFAULT 22,
                username TEXT NOT NULL,
                auth_type TEXT NOT NULL,
                auth_data TEXT NOT NULL,
                deploy_path TEXT NOT NULL,
                start_command TEXT,
                stop_command TEXT,
                status_command TEXT,
                log_path TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建操作日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id INTEGER,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deployment_id) REFERENCES deployments(id)
            )
        """)

        conn.commit()
        conn.close()

    def add_deployment(self, deployment: Dict) -> int:
        """
        添加部署记录

        Args:
            deployment: 部署信息字典

        Returns:
            新记录的ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO deployments (
                    name, host, port, username, auth_type, auth_data,
                    deploy_path, start_command, stop_command, status_command,
                    log_path, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deployment['name'],
                deployment['host'],
                deployment.get('port', 22),
                deployment['username'],
                deployment['auth_type'],
                deployment['auth_data'],
                deployment['deploy_path'],
                deployment.get('start_command'),
                deployment.get('stop_command'),
                deployment.get('status_command'),
                deployment.get('log_path'),
                deployment.get('description')
            ))
            deployment_id = cursor.lastrowid
            conn.commit()
            return deployment_id
        except sqlite3.IntegrityError:
            raise ValueError(f"Deployment with name '{deployment['name']}' already exists")
        finally:
            conn.close()

    def get_deployment(self, identifier: str) -> Optional[Dict]:
        """
        获取部署信息

        Args:
            identifier: 部署名称或ID

        Returns:
            部署信息字典，不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 尝试按名称查询
            cursor.execute("SELECT * FROM deployments WHERE name = ?", (identifier,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row, cursor.description)

            # 尝试按ID查询
            cursor.execute("SELECT * FROM deployments WHERE id = ?", (identifier,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row, cursor.description)

            return None
        finally:
            conn.close()

    def list_deployments(self) -> List[Dict]:
        """
        列出所有部署

        Returns:
            部署列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deployments ORDER BY name")
        rows = cursor.fetchall()
        deployments = [self._row_to_dict(row, cursor.description) for row in rows]
        conn.close()
        return deployments

    def update_deployment(self, identifier: str, updates: Dict) -> bool:
        """
        更新部署信息

        Args:
            identifier: 部署名称或ID
            updates: 更新的部署信息

        Returns:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 先检查是否存在
            existing = self.get_deployment(identifier)
            if not existing:
                return False

            # 使用ID更新
            deployment_id = existing['id']

            # 构建更新语句
            update_fields = []
            update_values = []
            for field in ['host', 'port', 'username', 'auth_type', 'auth_data',
                          'deploy_path', 'start_command', 'stop_command',
                          'status_command', 'log_path', 'description']:
                if field in updates:
                    update_fields.append(f"{field} = ?")
                    update_values.append(updates[field])

            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(deployment_id)
                query = f"UPDATE deployments SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
                conn.commit()

            return True
        finally:
            conn.close()

    def remove_deployment(self, identifier: str) -> bool:
        """
        删除部署记录

        Args:
            identifier: 部署名称或ID

        Returns:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            existing = self.get_deployment(identifier)
            if not existing:
                return False

            deployment_id = existing['id']

            # 删除相关日志
            cursor.execute("DELETE FROM operation_logs WHERE deployment_id = ?", (deployment_id,))

            # 删除部署
            cursor.execute("DELETE FROM deployments WHERE id = ?", (deployment_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    def log_operation(self, deployment_id: int, operation: str, status: str, message: str = ""):
        """
        记录操作日志

        Args:
            deployment_id: 部署ID
            operation: 操作类型
            status: 操作状态
            message: 操作消息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO operation_logs (deployment_id, operation, status, message)
            VALUES (?, ?, ?, ?)
        """, (deployment_id, operation, status, message))
        conn.commit()
        conn.close()

    def _row_to_dict(self, row, description) -> Dict:
        """将数据库行转换为字典"""
        return {desc[0]: value for desc, value in zip(description, row)}
