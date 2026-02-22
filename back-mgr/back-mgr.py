#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
back-mgr - 远程项目备份与还原工具
"""

import os
import sys
import json
import subprocess
import datetime
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置目录和文件
CONFIG_DIR = Path.home() / ".back-mgr"
PROJECTS_FILE = CONFIG_DIR / "projects.json"
LOG_DIR = CONFIG_DIR / "logs"


class Colors:
    """终端颜色输出"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def _print(prefix: str, color: str, msg: str):
        """安全打印（处理 Windows 编码问题）"""
        try:
            print(f"{color}{prefix} {msg}{Colors.RESET}")
        except UnicodeEncodeError:
            # Windows 回退到 ASCII
            prefix_alt = {
                '✓': '[OK]',
                '⚠': '[WARN]',
                '✗': '[ERROR]',
                'ℹ': '[INFO]',
            }
            safe_prefix = prefix_alt.get(prefix, prefix)
            print(f"{color}{safe_prefix} {msg}{Colors.RESET}")

    @staticmethod
    def success(msg):
        Colors._print('✓', Colors.GREEN, msg)

    @staticmethod
    def warning(msg):
        Colors._print('⚠', Colors.YELLOW, msg)

    @staticmethod
    def error(msg):
        try:
            print(f"{Colors.RED}✗ {msg}{Colors.RESET}", file=sys.stderr)
        except UnicodeEncodeError:
            print(f"{Colors.RED}[ERROR] {msg}{Colors.RESET}", file=sys.stderr)
        sys.stderr.flush()

    @staticmethod
    def info(msg):
        Colors._print('ℹ', Colors.BLUE, msg)

    @staticmethod
    def header(msg):
        try:
            print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
            print(f"  {msg}")
            print(f"{'='*60}{Colors.RESET}\n")
        except UnicodeEncodeError:
            print(f"\n{'='*60}")
            print(f"  {msg}")
            print(f"{'='*60}\n")


class ProjectConfig:
    """项目配置管理"""

    def __init__(self):
        self.projects = []
        self.config_dir = CONFIG_DIR
        self._ensure_config_dir()
        self._load_projects()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_projects(self):
        """加载项目配置"""
        if PROJECTS_FILE.exists():
            try:
                with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.projects = data.get('projects', [])
            except Exception as e:
                Colors.error(f"加载配置失败: {e}")
                self.projects = []

    def _save_projects(self):
        """保存项目配置"""
        try:
            with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'projects': self.projects}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            Colors.error(f"保存配置失败: {e}")
            raise

    def add_project(self, project: Dict) -> bool:
        """添加项目"""
        if self.get_project(project['name']):
            Colors.error(f"项目 '{project['name']}' 已存在")
            return False

        project['exclude'] = project.get('exclude', [])
        project['databases'] = project.get('databases', [])
        project['encryptSensitive'] = project.get('encryptSensitive', True)

        self.projects.append(project)
        self._save_projects()
        Colors.success(f"项目 '{project['name']}' 已添加")
        return True

    def get_project(self, name: str) -> Optional[Dict]:
        """获取项目"""
        for p in self.projects:
            if p['name'] == name:
                return p
        return None

    def list_projects(self) -> List[Dict]:
        """列出所有项目"""
        return self.projects

    def delete_project(self, name: str) -> bool:
        """删除项目"""
        project = self.get_project(name)
        if not project:
            Colors.error(f"项目 '{name}' 不存在")
            return False

        self.projects.remove(project)
        self._save_projects()
        Colors.success(f"项目 '{name}' 已删除")
        return True


class BackupManager:
    """备份管理器"""

    def __init__(self, project: Dict):
        self.project = project
        self.local_path = Path(project['localPath']).expanduser()
        self.backup_base = self.local_path / "backups"

    def create_backup(self, incremental: bool = False, db_only: bool = False,
                      files_only: bool = False, exclude: List[str] = None,
                      dry_run: bool = False) -> bool:
        """创建备份"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_path = self.backup_base / timestamp

        if dry_run:
            Colors.info(f"[模拟] 将创建备份: {backup_path}")
            if not db_only:
                Colors.info(f"[模拟] 从 {self._get_remote_full_path()} 备份文件")
            if not files_only and self.project.get('databases'):
                Colors.info(f"[模拟] 备份数据库: {', '.join([db['name'] for db in self.project['databases']])}")
            return True

        # 创建备份目录
        backup_path.mkdir(parents=True, exist_ok=True)

        Colors.header(f"开始备份 {self.project['name']}")

        # 备份文件
        if not db_only:
            if not self._backup_files(backup_path, incremental, exclude):
                return False

        # 备份数据库
        if not files_only and self.project.get('databases'):
            if not self._backup_databases(backup_path):
                return False

        # 创建备份清单
        self._create_manifest(backup_path)

        Colors.success(f"备份完成: {backup_path}")
        return True

    def _get_remote_full_path(self) -> str:
        """获取远程完整路径"""
        port = self.project.get('port', 22)
        user = self.project['user']
        host = self.project['host']
        remote_path = self.project['remotePath']
        return f"-p {port} {user}@{host}:{remote_path}"

    def _backup_files(self, backup_path: Path, incremental: bool, exclude: List[str]) -> bool:
        """备份文件 - 使用压缩包方式"""
        Colors.info("备份文件系统...")

        backup_dir = backup_path / "files"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # 构建排除列表
        exclude_list = self.project.get('exclude', [])
        if exclude:
            exclude_list.extend(exclude)

        if incremental and self._is_command_available('rsync'):
            # 增量备份使用 rsync
            Colors.info("使用 rsync 进行增量备份...")
            return self._backup_with_rsync(backup_dir, exclude_list)
        else:
            # 使用压缩包方式（推荐，支持排除规则）
            Colors.info("使用压缩包方式备份...")
            return self._backup_with_archive(backup_dir, exclude_list)

    def _is_command_available(self, cmd: str) -> bool:
        """检查命令是否可用"""
        return shutil.which(cmd) is not None

    def _backup_with_rsync(self, backup_dir: Path, exclude: List[str]) -> bool:
        """使用 rsync 增量备份"""
        previous = self._get_latest_backup()
        if previous and previous.exists():
            link_dest = previous / "files"
            cmd = f'rsync -avz -e "ssh -p {self.project["port"]}" --link-dest="{link_dest}" '

            # 添加排除项
            for pattern in exclude:
                cmd += f'--exclude="{pattern}" '
        else:
            cmd = f'rsync -avz -e "ssh -p {self.project["port"]}" '
            for pattern in exclude:
                cmd += f'--exclude="{pattern}" '

        remote = f'{self.project["user"]}@{self.project["host"]}:{self.project["remotePath"]}/'
        cmd += f'{remote} {backup_dir}/'

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                Colors.success("rsync 增量备份完成")
                return True
            else:
                Colors.error(f"rsync 失败: {result.stderr.strip()}")
                return False
        except Exception as e:
            Colors.error(f"备份文件失败: {e}")
            return False

    def _backup_with_archive(self, backup_dir: Path, exclude: List[str]) -> bool:
        """使用压缩包备份（推荐）"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"backup_{timestamp}.tar.gz"
        remote_archive = f"/tmp/{archive_name}"

        # 在远程服务器上创建压缩包
        if not self._create_remote_tar(remote_archive, exclude):
            return False

        # 下载压缩包到本地
        local_archive = backup_dir / archive_name
        if not self._download_archive(remote_archive, local_archive):
            return False

        # 清理远程临时文件
        Colors.info("清理远程临时文件...")
        cleanup_cmd = f'ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "rm -f {remote_archive}"'
        subprocess.run(cleanup_cmd, shell=True, capture_output=True)

        Colors.success(f"文件备份完成: {archive_name}")
        return True

    def _create_remote_tar(self, remote_archive: str, exclude: List[str]) -> bool:
        """在远程服务器上创建压缩包"""
        Colors.info("在远程服务器创建压缩包...")

        # 构建 tar 排除参数
        tar_excludes = ""
        for pattern in exclude:
            # 转换 rsync 模式到 tar 模式
            tar_pattern = pattern.replace("/**", "").rstrip("/")
            tar_excludes += f" --exclude='{tar_pattern}'"

        # 创建压缩包命令 - 分两步执行
        dir_name = os.path.basename(self.project['remotePath'])
        parent_dir = os.path.dirname(self.project['remotePath'])
        if not parent_dir:
            parent_dir = '.'

        tar_cmd = f'ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "cd {parent_dir} && tar -czf {remote_archive} {tar_excludes} {dir_name}"'

        try:
            Colors.info(f"正在压缩... (排除: {len(exclude)} 个规则)")
            result = subprocess.run(tar_cmd, shell=True, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                # 验证文件是否存在
                check_cmd = f'ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "test -f {remote_archive} && ls -lh {remote_archive}"'
                check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)

                if check_result.returncode == 0:
                    Colors.success(f"远程压缩包创建成功\n{check_result.stdout.strip()}")
                    return True
                else:
                    Colors.error(f"压缩文件创建失败: {check_result.stderr.strip()}")
                    return False
            else:
                Colors.error(f"创建压缩包失败: {result.stderr.strip()}")
                return False
        except subprocess.TimeoutExpired:
            Colors.error("压缩超时（可能文件太大）")
            return False
        except Exception as e:
            Colors.error(f"创建压缩包异常: {e}")
            return False

    def _download_archive(self, remote_archive: str, local_archive: Path) -> bool:
        """从远程下载压缩包"""
        Colors.info("下载压缩包...")

        scp_cmd = f'scp -P {self.project["port"]} {self.project["user"]}@{self.project["host"]}:{remote_archive} "{local_archive}"'

        try:
            result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and local_archive.exists():
                size = local_archive.stat().st_size
                Colors.success(f"下载完成 ({self._format_size(size)})")
                return True
            else:
                Colors.error(f"下载失败: {result.stderr.strip()}")
                return False
        except Exception as e:
            Colors.error(f"下载异常: {e}")
            return False

    def _format_size(self, size: int) -> str:
        """格式化大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def _backup_databases(self, backup_path: Path) -> bool:
        """备份数据库"""
        Colors.info("备份数据库...")

        db_dir = backup_path / "databases"
        db_dir.mkdir(parents=True, exist_ok=True)

        success = True
        for db in self.project.get('databases', []):
            if not self._backup_single_database(db, db_dir):
                success = False

        if success:
            Colors.success("数据库备份完成")
        return success

    def _backup_single_database(self, db: Dict, output_dir: Path) -> bool:
        """备份单个数据库"""
        db_type = db['type']
        db_name = db['name']

        Colors.info(f"备份 {db_type} 数据库: {db_name}")

        if db_type == 'mysql':
            return self._backup_mysql(db, output_dir)
        elif db_type == 'postgresql':
            return self._backup_postgresql(db, output_dir)
        else:
            Colors.warning(f"暂不支持 {db_type} 数据库类型")
            return True  # 不阻止其他数据库备份

    def _backup_mysql(self, db: Dict, output_dir: Path) -> bool:
        """备份 MySQL 数据库"""
        output_file = output_dir / f"{db['name']}.sql"

        cmd = [
            'ssh', f'-p {self.project["port"]}',
            f'{self.project["user"]}@{self.project["host"]}',
            f'mysqldump -u {db["user"]} -p$MYSQL_PWD {db["name"]}'
        ]

        try:
            result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True,
                                    env={**os.environ, 'MYSQL_PWD': os.getenv('MYSQL_PASSWORD', '')})

            if result.returncode == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                Colors.success(f"MySQL 备份完成: {output_file.name}")
                return True
            else:
                Colors.error(f"MySQL 备份失败: {result.stderr.strip()}")
                return False
        except Exception as e:
            Colors.error(f"MySQL 备份异常: {e}")
            return False

    def _backup_postgresql(self, db: Dict, output_dir: Path) -> bool:
        """备份 PostgreSQL 数据库"""
        output_file = output_dir / f"{db['name']}.sql"

        cmd = [
            'ssh', f'-p {self.project["port"]}',
            f'{self.project["user"]}@{self.project["host"]}',
            f'PGPASSWORD=$PG_PWD pg_dump -U {db["user"]} {db["name"]}'
        ]

        try:
            result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True,
                                    env={**os.environ, 'PG_PWD': os.getenv('PG_PASSWORD', '')})

            if result.returncode == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                Colors.success(f"PostgreSQL 备份完成: {output_file.name}")
                return True
            else:
                Colors.error(f"PostgreSQL 备份失败: {result.stderr.strip()}")
                return False
        except Exception as e:
            Colors.error(f"PostgreSQL 备份异常: {e}")
            return False

    def _get_latest_backup(self) -> Optional[Path]:
        """获取最新的备份目录"""
        if not self.backup_base.exists():
            return None

        backups = sorted(self.backup_base.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        return backups[0] if backups else None

    def _create_manifest(self, backup_path: Path):
        """创建备份清单"""
        manifest = {
            'project': self.project['name'],
            'timestamp': datetime.datetime.now().isoformat(),
            'host': self.project['host'],
            'remotePath': self.project['remotePath'],
            'includesDatabase': bool(self.project.get('databases')),
        }

        manifest_file = backup_path / 'manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)


class RestoreManager:
    """还原管理器"""

    def __init__(self, project: Dict):
        self.project = project
        self.local_path = Path(project['localPath']).expanduser()
        self.backup_base = self.local_path / "backups"

    def list_versions(self) -> List[Dict]:
        """列出所有备份版本"""
        if not self.backup_base.exists():
            return []

        versions = []
        for backup_dir in sorted(self.backup_base.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            manifest_file = backup_dir / 'manifest.json'
            manifest = self._load_manifest(manifest_file)

            size = self._calculate_size(backup_dir)
            versions.append({
                'name': backup_dir.name,
                'timestamp': backup_dir.stat().st_mtime,
                'size': size,
                'manifest': manifest
            })

        return versions

    def _load_manifest(self, manifest_file: Path) -> Optional[Dict]:
        """加载清单文件"""
        if not manifest_file.exists():
            return None

        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def _calculate_size(self, path: Path) -> str:
        """计算目录大小"""
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except:
            pass

        return self._format_size(total)

    def _format_size(self, size: int) -> str:
        """格式化大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def restore(self, version: str = None, files_only: bool = False,
                db_only: bool = False, dry_run: bool = False) -> bool:
        """还原备份"""
        # 确定备份版本
        if version:
            backup_path = self.backup_base / version
            if not backup_path.exists():
                Colors.error(f"备份版本 '{version}' 不存在")
                return False
        else:
            backup_path = self._get_latest_backup()
            if not backup_path:
                Colors.error("没有可用的备份")
                return False

        Colors.header(f"还原 {self.project['name']} - 版本 {backup_path.name}")

        if dry_run:
            Colors.info(f"[模拟] 将还原: {backup_path.name}")
            if not db_only:
                Colors.info(f"[模拟] 还原文件到 {self.project['remotePath']}")
            if not files_only and self.project.get('databases'):
                Colors.info(f"[模拟] 还原数据库")
            return True

        # 还原文件
        if not db_only:
            files_dir = backup_path / "files"
            if files_dir.exists():
                if not self._restore_files(files_dir):
                    return False

        # 还原数据库
        if not files_only and self.project.get('databases'):
            db_dir = backup_path / "databases"
            if db_dir.exists():
                if not self._restore_databases(db_dir):
                    return False

        Colors.success("还原完成")
        return True

    def _get_latest_backup(self) -> Optional[Path]:
        """获取最新的备份"""
        backups = list(self.backup_base.iterdir())
        if not backups:
            return None
        return max(backups, key=lambda p: p.stat().st_mtime)

    def _restore_files(self, files_dir: Path) -> bool:
        """还原文件"""
        Colors.info("还原文件系统...")

        # 检查是否有压缩包
        archives = list(files_dir.glob('backup_*.tar.gz'))
        if archives:
            # 使用压缩包还原
            return self._restore_from_archive(archives[0])

        # 使用 rsync 还原
        if self._is_command_available('rsync'):
            cmd = [
                'rsync', '-avz',
                f'-e "ssh -p {self.project["port"]}"',
                f'{files_dir}/',
                f'{self.project["user"]}@{self.project["host"]}:{self.project["remotePath"]}/'
            ]

            try:
                result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    Colors.success("文件还原完成")
                    return True
                else:
                    Colors.error(f"文件还原失败: {result.stderr.strip()}")
                    return False
            except Exception as e:
                Colors.error(f"还原文件异常: {e}")
                return False
        else:
            Colors.error("rsync 不可用，且未找到压缩包，无法还原")
            return False

    def _is_command_available(self, cmd: str) -> bool:
        """检查命令是否可用"""
        return shutil.which(cmd) is not None

    def _restore_from_archive(self, archive_path: Path) -> bool:
        """从压缩包还原"""
        Colors.info(f"使用压缩包还原: {archive_path.name}")

        remote_target = f'/tmp/{archive_path.name}'

        # 上传压缩包
        if not self._upload_archive(archive_path, remote_target):
            return False

        # 在远程解压
        if not self._extract_remote_archive(remote_target):
            return False

        # 清理远程临时文件
        Colors.info("清理远程临时文件...")
        cleanup_cmd = f'ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "rm -f {remote_target}"'
        subprocess.run(cleanup_cmd, shell=True, capture_output=True)

        Colors.success("文件还原完成")
        return True

    def _upload_archive(self, local_archive: Path, remote_archive: str) -> bool:
        """上传压缩包到远程"""
        Colors.info("上传压缩包...")

        scp_cmd = f'scp -P {self.project["port"]} "{local_archive}" {self.project["user"]}@{self.project["host"]}:{remote_archive}'

        try:
            result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                Colors.success(f"上传完成")
                return True
            else:
                Colors.error(f"上传失败: {result.stderr.strip()}")
                return False
        except Exception as e:
            Colors.error(f"上传异常: {e}")
            return False

    def _extract_remote_archive(self, remote_archive: str) -> bool:
        """在远程服务器解压压缩包"""
        Colors.info("在远程服务器解压...")

        # 先备份远程现有文件
        backup_cmd = f'ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "mv {self.project["remotePath"]} {self.project["remotePath"]}.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true"'
        subprocess.run(backup_cmd, shell=True, capture_output=True)

        # 解压命令
        extract_cmd = f'ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "cd /tmp && tar -xzf {remote_archive} && mv $(tar -tzf {remote_archive} | head -1 | cut -f1 -d\"/\") {self.project["remotePath"]}"'

        try:
            result = subprocess.run(extract_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                Colors.success("远程解压完成")
                return True
            else:
                Colors.error(f"远程解压失败: {result.stderr.strip()}")
                # 恢复备份
                restore_cmd = f'ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "rm -rf {self.project["remotePath"]} && mv {self.project["remotePath"]}.backup.* {self.project["remotePath"]} 2>/dev/null || true"'
                subprocess.run(restore_cmd, shell=True, capture_output=True)
                return False
        except Exception as e:
            Colors.error(f"远程解压异常: {e}")
            return False

    def _restore_databases(self, db_dir: Path) -> bool:
        """还原数据库"""
        Colors.info("还原数据库...")

        success = True
        for db in self.project.get('databases', []):
            sql_file = db_dir / f"{db['name']}.sql"
            if not sql_file.exists():
                continue

            if not self._restore_single_database(db, sql_file):
                success = False

        if success:
            Colors.success("数据库还原完成")
        return success

    def _restore_single_database(self, db: Dict, sql_file: Path) -> bool:
        """还原单个数据库"""
        db_type = db['type']
        db_name = db['name']

        Colors.info(f"还原 {db_type} 数据库: {db_name}")

        if db_type == 'mysql':
            return self._restore_mysql(db, sql_file)
        elif db_type == 'postgresql':
            return self._restore_postgresql(db, sql_file)
        else:
            Colors.warning(f"暂不支持 {db_type} 数据库类型")
            return True

    def _restore_mysql(self, db: Dict, sql_file: Path) -> bool:
        """还原 MySQL 数据库"""
        cmd = f'cat "{sql_file}" | ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "mysql -u {db["user"]} -p$MYSQL_PWD {db["name"]}"'

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                    env={**os.environ, 'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD', '')})

            if result.returncode == 0:
                Colors.success(f"MySQL 还原完成")
                return True
            else:
                Colors.error(f"MySQL 还原失败: {result.stderr.strip()}")
                return False
        except Exception as e:
            Colors.error(f"MySQL 还原异常: {e}")
            return False

    def _restore_postgresql(self, db: Dict, sql_file: Path) -> bool:
        """还原 PostgreSQL 数据库"""
        cmd = f'cat "{sql_file}" | ssh -p {self.project["port"]} {self.project["user"]}@{self.project["host"]} "PGPASSWORD=$PG_PWD psql -U {db["user"]} {db["name"]}"'

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                    env={**os.environ, 'PG_PASSWORD': os.getenv('PG_PASSWORD', '')})

            if result.returncode == 0:
                Colors.success(f"PostgreSQL 还原完成")
                return True
            else:
                Colors.error(f"PostgreSQL 还原失败: {result.stderr.strip()}")
                return False
        except Exception as e:
            Colors.error(f"PostgreSQL 还原异常: {e}")
            return False


def cmd_add(args):
    """添加项目命令"""
    project = {
        'name': args.name,
        'host': args.host,
        'port': args.port,
        'user': args.user,
        'remotePath': args.remote_path,
        'localPath': args.local_path,
        'exclude': list(args.exclude) if args.exclude else [],
    }

    if args.db_type and args.db_name:
        project['databases'] = [{
            'type': args.db_type,
            'name': args.db_name,
            'user': args.db_user or 'root',
            'host': 'localhost',
            'port': 3306 if args.db_type == 'mysql' else 5432
        }]

    config = ProjectConfig()
    config.add_project(project)


def cmd_list(args):
    """列出项目命令"""
    config = ProjectConfig()
    projects = config.list_projects()

    if not projects:
        Colors.warning("没有配置任何项目")
        return

    Colors.header("项目列表")
    for p in projects:
        print(f"  {Colors.GREEN}{p['name']}{Colors.RESET}")
        print(f"    主机: {p['user']}@{p['host']}:{p.get('port', 22)}")
        print(f"    远程: {p['remotePath']}")
        print(f"    本地: {p['localPath']}")
        if p.get('databases'):
            print(f"    数据库: {', '.join([db['name'] for db in p['databases']])}")
        print()


def cmd_delete(args):
    """删除项目命令"""
    config = ProjectConfig()
    config.delete_project(args.name)


def cmd_backup(args):
    """备份命令"""
    config = ProjectConfig()
    project = config.get_project(args.project_name)

    if not project:
        Colors.error(f"项目 '{args.project_name}' 不存在")
        return

    manager = BackupManager(project)
    manager.create_backup(
        incremental=args.incremental,
        db_only=args.db_only,
        files_only=args.files_only,
        exclude=list(args.exclude) if args.exclude else None,
        dry_run=args.dry_run
    )


def cmd_restore(args):
    """还原命令"""
    config = ProjectConfig()
    project = config.get_project(args.project_name)

    if not project:
        Colors.error(f"项目 '{args.project_name}' 不存在")
        return

    manager = RestoreManager(project)
    manager.restore(
        version=args.version,
        files_only=args.files_only,
        db_only=args.db_only,
        dry_run=args.dry_run
    )


def cmd_versions(args):
    """列出备份版本命令"""
    config = ProjectConfig()
    project = config.get_project(args.project_name)

    if not project:
        Colors.error(f"项目 '{args.project_name}' 不存在")
        return

    manager = RestoreManager(project)
    versions = manager.list_versions()

    if not versions:
        Colors.warning("没有可用的备份版本")
        return

    Colors.header(f"{project['name']} 备份版本")
    for i, v in enumerate(versions, 1):
        timestamp = datetime.datetime.fromtimestamp(v['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  {i}. {Colors.GREEN}{v['name']}{Colors.RESET}")
        print(f"     时间: {timestamp}")
        print(f"     大小: {v['size']}")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='远程项目备份与还原工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 添加项目
  back-mgr add --name myapp --host example.com --user deploy \\
               --remote-path /var/www/myapp --local-path ~/backups/myapp

  # 创建完整备份
  back-mgr backup myapp

  # 创建增量备份
  back-mgr backup myapp --incremental

  # 还原最新版本
  back-mgr restore myapp

  # 列出备份版本
  back-mgr versions myapp
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 添加项目命令
    add_parser = subparsers.add_parser('add', help='添加项目')
    add_parser.add_argument('--name', required=True, help='项目名称')
    add_parser.add_argument('--host', required=True, help='远程服务器地址')
    add_parser.add_argument('--user', default='root', help='SSH用户名')
    add_parser.add_argument('--port', type=int, default=22, help='SSH端口')
    add_parser.add_argument('--remote-path', required=True, help='远程项目路径')
    add_parser.add_argument('--local-path', required=True, help='本地备份路径')
    add_parser.add_argument('--exclude', action='append', help='排除的文件模式')
    add_parser.add_argument('--db-type', choices=['mysql', 'postgresql'], help='数据库类型')
    add_parser.add_argument('--db-name', help='数据库名称')
    add_parser.add_argument('--db-user', help='数据库用户')

    # 列出项目命令
    subparsers.add_parser('list', help='列出所有项目')

    # 删除项目命令
    delete_parser = subparsers.add_parser('delete', help='删除项目')
    delete_parser.add_argument('name', help='项目名称')

    # 备份命令
    backup_parser = subparsers.add_parser('backup', help='创建备份')
    backup_parser.add_argument('project_name', help='项目名称')
    backup_parser.add_argument('--files-only', action='store_true', help='仅备份文件')
    backup_parser.add_argument('--db-only', action='store_true', help='仅备份数据库')
    backup_parser.add_argument('--incremental', action='store_true', help='增量备份')
    backup_parser.add_argument('--exclude', action='append', help='额外排除的文件模式')
    backup_parser.add_argument('--dry-run', action='store_true', help='模拟运行')

    # 还原命令
    restore_parser = subparsers.add_parser('restore', help='还原项目')
    restore_parser.add_argument('project_name', help='项目名称')
    restore_parser.add_argument('--version', help='指定还原的版本')
    restore_parser.add_argument('--files-only', action='store_true', help='仅还原文件')
    restore_parser.add_argument('--db-only', action='store_true', help='仅还原数据库')
    restore_parser.add_argument('--dry-run', action='store_true', help='模拟运行')

    # 列出版本命令
    versions_parser = subparsers.add_parser('versions', help='列出备份版本')
    versions_parser.add_argument('project_name', help='项目名称')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 命令映射
    commands = {
        'add': cmd_add,
        'list': cmd_list,
        'delete': cmd_delete,
        'backup': cmd_backup,
        'restore': cmd_restore,
        'versions': cmd_versions,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
