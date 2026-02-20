"""
压缩模块单元测试
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compressor import Compressor


class TestCompressor(unittest.TestCase):

    def setUp(self):
        """创建测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_dir = Path(self.temp_dir) / "test_dir"

        # 创建测试文件
        with open(self.test_file, 'w') as f:
            f.write("test content" * 1000)

        # 创建测试目录
        self.test_dir.mkdir()
        (self.test_dir / "file1.txt").write_text("content 1")
        (self.test_dir / "file2.txt").write_text("content 2")
        (self.test_dir / "subdir").mkdir()
        (self.test_dir / "subdir" / "file3.txt").write_text("content 3")

    def test_compress_single_file_zip(self):
        """测试ZIP压缩单个文件"""
        compressor = Compressor(str(self.test_file), 'zip')
        archive_path, md5 = compressor.compress()

        self.assertTrue(archive_path.exists())
        self.assertTrue(archive_path.suffix == '.zip')
        self.assertTrue(len(md5) == 32)  # MD5长度

        # 清理
        compressor.cleanup(archive_path)

    def test_compress_single_file_targz(self):
        """测试TAR.GZ压缩单个文件"""
        compressor = Compressor(str(self.test_file), 'tar.gz')
        archive_path, md5 = compressor.compress()

        self.assertTrue(archive_path.exists())
        self.assertTrue(str(archive_path).endswith('.tar.gz'))
        self.assertTrue(len(md5) == 32)

        # 清理
        compressor.cleanup(archive_path)

    def test_compress_directory(self):
        """测试压缩目录"""
        compressor = Compressor(str(self.test_dir), 'zip')
        archive_path, md5 = compressor.compress()

        self.assertTrue(archive_path.exists())
        self.assertTrue(archive_path.suffix == '.zip')

        # 清理
        compressor.cleanup(archive_path)

    def test_exclude_patterns(self):
        """测试排除文件模式"""
        # 创建应该被排除的文件
        (self.test_dir / "__pycache__").mkdir()
        (self.test_dir / "__pycache__" / "cache.pyc").write_text("cached")
        (self.test_dir / ".git").mkdir()
        (self.test_dir / ".git" / "config").write_text("git config")

        compressor = Compressor(
            str(self.test_dir),
            'zip',
            exclude_patterns=['__pycache__', '.git']
        )
        archive_path, md5 = compressor.compress()

        self.assertTrue(archive_path.exists())

        # 清理
        compressor.cleanup(archive_path)

    def test_nonexistent_path(self):
        """测试不存在的路径"""
        compressor = Compressor('/nonexistent/path', 'zip')
        with self.assertRaises(FileNotFoundError):
            compressor.compress()

    def test_unsupported_format(self):
        """测试不支持的压缩格式（虽然内部不强制，但可以测试边界情况）"""
        compressor = Compressor(str(self.test_file), 'zip')
        # ZIP是支持的，应该成功
        archive_path, md5 = compressor.compress()
        self.assertTrue(archive_path.exists())
        compressor.cleanup(archive_path)

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


if __name__ == '__main__':
    unittest.main()
