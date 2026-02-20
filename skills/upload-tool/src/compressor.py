"""
文件压缩模块
支持 ZIP 和 TAR.GZ 格式的压缩
"""

import os
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Tuple
import hashlib
from tqdm import tqdm
from datetime import datetime


class Compressor:
    """文件压缩处理器"""

    SUPPORTED_FORMATS = ['zip', 'tar.gz']

    def __init__(self, source_path: str, compression_format: str = 'zip',
                 exclude_patterns: Optional[list] = None):
        """
        初始化压缩器

        Args:
            source_path: 源文件或目录路径
            compression_format: 压缩格式 ('zip' 或 'tar.gz')
            exclude_patterns: 要排除的文件模式列表
        """
        self.source_path = Path(source_path)
        self.format = compression_format
        self.exclude_patterns = exclude_patterns or []

        # 设置临时目录
        if os.name == 'nt':  # Windows
            self.temp_dir = Path(os.environ.get('TEMP', 'C:\\temp')) / 'upload_tool'
        else:  # Unix-like
            self.temp_dir = Path('/tmp') / 'upload_tool'

        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def compress(self) -> Tuple[Path, str]:
        """
        压缩文件/目录

        Returns:
            (压缩包路径, MD5值)
        """
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source path not found: {self.source_path}")

        output_name = f"{self.source_path.name}_{self._generate_timestamp()}.{self.format}"
        output_path = self.temp_dir / output_name

        if self.source_path.is_file():
            return self._compress_file(output_path)
        else:
            return self._compress_directory(output_path)

    def _compress_file(self, output_path: Path) -> Tuple[Path, str]:
        """压缩单个文件"""
        if self.format == 'zip':
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(self.source_path, self.source_path.name)
        else:  # tar.gz
            with tarfile.open(output_path, 'w:gz') as tar:
                tar.add(self.source_path, arcname=self.source_path.name)

        return output_path, self._calculate_md5(output_path)

    def _compress_directory(self, output_path: Path) -> Tuple[Path, str]:
        """压缩目录"""
        if self.format == 'zip':
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(self.source_path):
                    # 过滤排除的目录
                    dirs[:] = [d for d in dirs if not self._should_exclude(d)]

                    for file in tqdm(files, desc="Compressing files", unit="file"):
                        if self._should_exclude(file):
                            continue

                        file_path = Path(root) / file
                        arcname = os.path.relpath(file_path, self.source_path.parent)
                        zf.write(file_path, arcname)
        else:  # tar.gz
            with tarfile.open(output_path, 'w:gz') as tar:
                for item in self.source_path.iterdir():
                    if self._should_exclude(item.name):
                        continue
                    tar.add(item, arcname=item.name,
                            filter=lambda info: self._filter_tar(info))

        return output_path, self._calculate_md5(output_path)

    def _should_exclude(self, name: str) -> bool:
        """检查文件/目录是否应该被排除"""
        for pattern in self.exclude_patterns:
            if pattern in name or name.endswith(pattern.replace('*', '')):
                return True
        return False

    def _filter_tar(self, tarinfo):
        """Tar过滤器，用于排除文件"""
        if self._should_exclude(tarinfo.name):
            return None
        return tarinfo

    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件MD5"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _generate_timestamp(self) -> str:
        """生成时间戳"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def cleanup(self, file_path: Path):
        """清理临时文件"""
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"Warning: Failed to cleanup {file_path}: {e}")
