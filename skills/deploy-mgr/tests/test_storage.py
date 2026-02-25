"""
Deploy Mgr 单元测试
测试核心功能
"""

import sys
import os
import unittest
import tempfile

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage import Storage


class TestStorage(unittest.TestCase):
    """测试存储模块"""

    def setUp(self):
        """设置测试环境"""
        # 使用临时文件作为测试数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.storage = Storage(self.temp_db.name)

    def tearDown(self):
        """清理测试环境"""
        import os
        os.unlink(self.temp_db.name)

    def test_add_deployment(self):
        """测试添加部署"""
        deployment = {
            'name': 'test-app',
            'host': 'example.com',
            'username': 'root',
            'auth_type': 'key',
            'auth_data': '~/.ssh/id_rsa',
            'deploy_path': '/var/www/test',
            'description': 'Test app'
        }

        deployment_id = self.storage.add_deployment(deployment)
        self.assertIsNotNone(deployment_id)
        self.assertGreater(deployment_id, 0)

    def test_get_deployment(self):
        """测试获取部署"""
        deployment = {
            'name': 'test-app',
            'host': 'example.com',
            'username': 'root',
            'auth_type': 'key',
            'auth_data': '~/.ssh/id_rsa',
            'deploy_path': '/var/www/test'
        }

        self.storage.add_deployment(deployment)

        # 按名称获取
        result = self.storage.get_deployment('test-app')
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'test-app')

        # 按ID获取
        result = self.storage.get_deployment(str(result['id']))
        self.assertIsNotNone(result)

    def test_list_deployments(self):
        """测试列出部署"""
        self.storage.add_deployment({
            'name': 'app1',
            'host': 'server1.com',
            'username': 'root',
            'auth_type': 'key',
            'auth_data': '~/.ssh/id_rsa',
            'deploy_path': '/var/www/app1'
        })

        self.storage.add_deployment({
            'name': 'app2',
            'host': 'server2.com',
            'username': 'root',
            'auth_type': 'key',
            'auth_data': '~/.ssh/id_rsa',
            'deploy_path': '/var/www/app2'
        })

        deployments = self.storage.list_deployments()
        self.assertEqual(len(deployments), 2)

    def test_update_deployment(self):
        """测试更新部署"""
        deployment = {
            'name': 'test-app',
            'host': 'example.com',
            'username': 'root',
            'auth_type': 'key',
            'auth_data': '~/.ssh/id_rsa',
            'deploy_path': '/var/www/test'
        }

        self.storage.add_deployment(deployment)

        success = self.storage.update_deployment('test-app', {'description': 'Updated description'})
        self.assertTrue(success)

        result = self.storage.get_deployment('test-app')
        self.assertEqual(result['description'], 'Updated description')

    def test_remove_deployment(self):
        """测试删除部署"""
        deployment = {
            'name': 'test-app',
            'host': 'example.com',
            'username': 'root',
            'auth_type': 'key',
            'auth_data': '~/.ssh/id_rsa',
            'deploy_path': '/var/www/test'
        }

        self.storage.add_deployment(deployment)

        success = self.storage.remove_deployment('test-app')
        self.assertTrue(success)

        result = self.storage.get_deployment('test-app')
        self.assertIsNone(result)

    def test_duplicate_name(self):
        """测试重名部署"""
        deployment = {
            'name': 'test-app',
            'host': 'example.com',
            'username': 'root',
            'auth_type': 'key',
            'auth_data': '~/.ssh/id_rsa',
            'deploy_path': '/var/www/test'
        }

        self.storage.add_deployment(deployment)

        # 添加同名部署应该失败
        with self.assertRaises(ValueError):
            self.storage.add_deployment(deployment)


if __name__ == '__main__':
    unittest.main()
