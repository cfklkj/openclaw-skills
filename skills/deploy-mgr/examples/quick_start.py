#!/usr/bin/env python3
"""
Deploy Mgr 使用示例
演示如何使用 DeploymentManager API
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from manager import DeploymentManager


def main():
    """运行示例"""
    print("=" * 60)
    print("Deploy Mgr 使用示例")
    print("=" * 60)

    manager = DeploymentManager()

    # 示例 1: 添加部署
    print("\n[示例 1] 添加部署")
    print("-" * 60)
    try:
        deployment_id = manager.add_deployment(
            name="test-app",
            host="example.com",
            port=22,
            username="root",
            auth_type="key",
            auth_data="~/.ssh/id_rsa",
            deploy_path="/var/www/test-app",
            start_command="npm start",
            stop_command="npm stop",
            log_path="/var/log/test-app/app.log",
            description="测试应用"
        )
        print(f"✓ 部署添加成功, ID: {deployment_id}")
    except Exception as e:
        print(f"✗ 添加失败: {e}")
        return

    # 示例 2: 列出部署
    print("\n[示例 2] 列出所有部署")
    print("-" * 60)
    deployments = manager.list_deployments()
    for dep in deployments:
        print(f"  - {dep['id']}: {dep['name']} ({dep['host']})")

    # 示例 3: 查看部署详情
    print("\n[示例 3] 查看部署详情")
    print("-" * 60)
    deployment = manager.get_deployment("test-app")
    if deployment:
        print(f"名称: {deployment['name']}")
        print(f"主机: {deployment['host']}")
        print(f"路径: {deployment['deploy_path']}")
        print(f"启动命令: {deployment.get('start_command', '未配置')}")

    # 示例 4: 更新部署
    print("\n[示例 4] 更新部署描述")
    print("-" * 60)
    success = manager.update_deployment("test-app", description="更新的描述")
    if success:
        print("✓ 部署更新成功")

    # 示例 5: 删除部署
    print("\n[示例 5] 删除部署")
    print("-" * 60)
    confirm = input("确认删除 'test-app' 部署? (y/n): ")
    if confirm.lower() == 'y':
        success = manager.remove_deployment("test-app")
        if success:
            print("✓ 部署删除成功")

    manager.close_all()
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
