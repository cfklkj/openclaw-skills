"""
命令行界面模块
提供命令行交互接口
"""

import click
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from manager import DeploymentManager


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Deploy Mgr - 远程服务部署管理工具"""
    pass


@cli.command()
def list():
    """列出所有部署"""
    manager = DeploymentManager()
    deployments = manager.list_deployments()

    if not deployments:
        click.echo("No deployments found.")
        return

    click.echo("\n" + "=" * 100)
    click.echo(f"{'ID':<5} {'Name':<20} {'Host':<25} {'Path':<30} {'Description':<20}")
    click.echo("=" * 100)

    for dep in deployments:
        desc = dep.get('description', '')[:20] or '-'
        click.echo(
            f"{dep['id']:<5} {dep['name']:<20} {dep['host']:<25} {dep['deploy_path']:<30} {desc:<20}"
        )

    click.echo("=" * 100)
    click.echo(f"\nTotal: {len(deployments)} deployment(s)")


@cli.command()
@click.argument('identifier')
def info(identifier):
    """查看部署详情"""
    manager = DeploymentManager()
    deployment = manager.get_deployment(identifier, include_auth=True)

    if not deployment:
        click.echo(f"Error: Deployment '{identifier}' not found.", err=True)
        sys.exit(1)

    click.echo("\n" + "=" * 60)
    click.echo(f"Deployment: {deployment['name']}")
    click.echo("=" * 60)
    click.echo(f"ID:              {deployment['id']}")
    click.echo(f"Host:            {deployment['host']}:{deployment['port']}")
    click.echo(f"Username:        {deployment['username']}")
    click.echo(f"Auth Type:       {deployment['auth_type']}")
    click.echo(f"Deploy Path:     {deployment['deploy_path']}")
    click.echo(f"Start Command:   {deployment.get('start_command', 'Not configured')}")
    click.echo(f"Stop Command:    {deployment.get('stop_command', 'Not configured')}")
    click.echo(f"Status Command:  {deployment.get('status_command', 'Not configured')}")
    click.echo(f"Log Path:        {deployment.get('log_path', 'Not configured')}")
    click.echo(f"Description:     {deployment.get('description', '-')}")
    click.echo(f"Created:         {deployment['created_at']}")
    click.echo(f"Updated:         {deployment['updated_at']}")
    click.echo("=" * 60)


@cli.command()
@click.option('--name', required=True, help='项目名称')
@click.option('--host', required=True, help='服务器地址')
@click.option('--port', default=22, help='SSH端口')
@click.option('--username', required=True, help='用户名')
@click.option('--auth-type', type=click.Choice(['password', 'key']), default='password', help='认证类型')
@click.option('--auth-data', required=True, help='密码或SSH密钥路径')
@click.option('--deploy-path', required=True, help='部署路径')
@click.option('--start-command', help='启动命令')
@click.option('--stop-command', help='停止命令')
@click.option('--status-command', help='状态检查命令')
@click.option('--log-path', help='日志文件路径')
@click.option('--description', help='描述信息')
def add(name, host, port, username, auth_type, auth_data, deploy_path,
        start_command, stop_command, status_command, log_path, description):
    """添加部署"""
    manager = DeploymentManager()

    try:
        deployment_id = manager.add_deployment(
            name=name,
            host=host,
            port=port,
            username=username,
            auth_type=auth_type,
            auth_data=auth_data,
            deploy_path=deploy_path,
            start_command=start_command,
            stop_command=stop_command,
            status_command=status_command,
            log_path=log_path,
            description=description
        )

        click.echo(f"\n✓ Deployment added successfully!")
        click.echo(f"  Name: {name}")
        click.echo(f"  ID: {deployment_id}")

    except Exception as e:
        click.echo(f"\n✗ Failed to add deployment: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('identifier')
@click.option('--host', help='更新服务器地址')
@click.option('--port', type=int, help='SSH端口')
@click.option('--username', help='用户名')
@click.option('--auth-data', help='密码或SSH密钥路径')
@click.option('--deploy-path', help='部署路径')
@click.option('--start-command', help='启动命令')
@click.option('--stop-command', help='停止命令')
@click.option('--status-command', help='状态检查命令')
@click.option('--log-path', help='日志文件路径')
@click.option('--description', help='描述信息')
def update(identifier, host, port, username, auth_data, deploy_path,
           start_command, stop_command, status_command, log_path, description):
    """更新部署"""
    manager = DeploymentManager()

    updates = {}
    if host:
        updates['host'] = host
    if port:
        updates['port'] = port
    if username:
        updates['username'] = username
    if auth_data:
        updates['auth_data'] = auth_data
    if deploy_path:
        updates['deploy_path'] = deploy_path
    if start_command:
        updates['start_command'] = start_command
    if stop_command:
        updates['stop_command'] = stop_command
    if status_command:
        updates['status_command'] = status_command
    if log_path:
        updates['log_path'] = log_path
    if description:
        updates['description'] = description

    if not updates:
        click.echo("No updates provided. Use --help to see available options.")
        return

    success = manager.update_deployment(identifier, **updates)

    if success:
        click.echo(f"\n✓ Deployment '{identifier}' updated successfully!")
    else:
        click.echo(f"\n✗ Deployment '{identifier}' not found.", err=True)
        sys.exit(1)


@cli.command()
@click.argument('identifier')
@click.confirmation_option(prompt='Are you sure you want to remove this deployment?')
def remove(identifier):
    """删除部署"""
    manager = DeploymentManager()
    success = manager.remove_deployment(identifier)

    if success:
        click.echo(f"\n✓ Deployment '{identifier}' removed successfully!")
    else:
        click.echo(f"\n✗ Deployment '{identifier}' not found.", err=True)
        sys.exit(1)


@cli.command()
@click.argument('identifier')
def status(identifier):
    """查看部署状态"""
    manager = DeploymentManager()

    try:
        status_info = manager.get_status(identifier)

        click.echo("\n" + "=" * 60)
        click.echo(f"Status: {status_info['name']}")
        click.echo("=" * 60)
        status_emoji = '✅' if status_info['status'] == 'running' else '❌'
        click.echo(f"{status_emoji} Status:  {status_info['status'].upper()}")
        click.echo(f"📝 Message: {status_info['message']}")
        click.echo("=" * 60)

    except ValueError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('identifier')
def start(identifier):
    """启动服务"""
    manager = DeploymentManager()

    try:
        result = manager.start_service(identifier)

        click.echo("\n" + "=" * 60)
        click.echo(f"Start Service: {result['name']}")
        click.echo("=" * 60)

        if result['success']:
            click.echo("✅ Service started successfully!")
            click.echo(f"📝 Message: {result['message']}")
        else:
            click.echo("❌ Failed to start service!")
            click.echo(f"📝 Exit Code: {result['exit_code']}")
            click.echo(f"📝 Message: {result['message']}")
            sys.exit(1)

        click.echo("=" * 60)

    except ValueError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('identifier')
def stop(identifier):
    """停止服务"""
    manager = DeploymentManager()

    try:
        result = manager.stop_service(identifier)

        click.echo("\n" + "=" * 60)
        click.echo(f"Stop Service: {result['name']}")
        click.echo("=" * 60)

        if result['success']:
            click.echo("✅ Service stopped successfully!")
            click.echo(f"📝 Message: {result['message']}")
        else:
            click.echo("❌ Failed to stop service!")
            click.echo(f"📝 Exit Code: {result['exit_code']}")
            click.echo(f"📝 Message: {result['message']}")
            sys.exit(1)

        click.echo("=" * 60)

    except ValueError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('identifier')
def restart(identifier):
    """重启服务"""
    manager = DeploymentManager()

    try:
        result = manager.restart_service(identifier)

        click.echo("\n" + "=" * 60)
        click.echo(f"Restart Service: {result['name']}")
        click.echo("=" * 60)

        if result['success']:
            click.echo("✅ Service restarted successfully!")
            click.echo(f"📝 Message: {result['message']}")
        else:
            click.echo("❌ Failed to restart service!")
            click.echo(f"📝 Message: {result['message']}")
            sys.exit(1)

        click.echo("=" * 60)

    except ValueError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('identifier')
@click.option('--lines', '-n', default=100, help='要显示的行数')
def logs(identifier, lines):
    """查看日志"""
    manager = DeploymentManager()

    try:
        log_info = manager.get_logs(identifier, lines)

        click.echo("\n" + "=" * 100)
        click.echo(f"Logs: {log_info['name']}")
        click.echo(f"File: {log_info['log_path']}")
        click.echo("=" * 100)

        click.echo(log_info['logs'])

        click.echo("=" * 100)

    except ValueError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
