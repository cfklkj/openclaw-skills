#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义模型管理脚本
提供模型的增删查改功能
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# 配置文件路径
CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / "model_config.json"

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ModelManager:
    """模型管理器"""

    def __init__(self):
        self.config_file = CONFIG_FILE
        self._ensure_config()

    def _ensure_config(self):
        """确保配置文件存在"""
        if not self.config_file.exists():
            self._write_config({"models": []})

    def _read_config(self):
        """读取配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"models": []}

    def _write_config(self, config):
        """写入配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _generate_id(self, provider):
        """生成模型ID"""
        # 查找该provider现有的模型数量
        config = self._read_config()
        count = sum(1 for m in config["models"] if m["provider"] == provider)
        return f"{provider.lower()}-{count + 1:03d}"

    def add(self, provider, api_key, model_name):
        """添加新模型"""
        config = self._read_config()

        model = {
            "id": self._generate_id(provider),
            "provider": provider,
            "api_key": api_key,
            "model_name": model_name,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "last_used": None
        }

        config["models"].append(model)
        self._write_config(config)

        print(f"✓ 模型添加成功")
        print(f"  ID: {model['id']}")
        print(f"  提供商: {model['provider']}")
        print(f"  模型名称: {model['model_name']}")

        return model

    def list(self, provider=None):
        """列出模型"""
        config = self._read_config()

        if not config["models"]:
            print("暂无已配置的模型")
            return

        # 过滤
        models = config["models"]
        if provider:
            models = [m for m in models if m["provider"].lower() == provider.lower()]
            if not models:
                print(f"未找到提供商 '{provider}' 的模型")
                return

        # 打印表格
        print(f"\n{'ID':<15} {'提供商':<12} {'模型名称':<40} {'创建时间':<20}")
        print("-" * 87)

        for model in models:
            created = model["created_at"][:19].replace('T', ' ')
            print(f"{model['id']:<15} {model['provider']:<12} {model['model_name']:<40} {created:<20}")

        print(f"\n总计: {len(models)} 个模型")

    def search(self, provider):
        """按提供商搜索模型"""
        self.list(provider=provider)

    def get_model(self, model_id=None, model_name=None):
        """获取模型（通过ID或名称）"""
        config = self._read_config()

        # 通过ID查找
        if model_id:
            for model in config["models"]:
                if model["id"] == model_id:
                    return model

        # 通过名称查找（模糊匹配）
        if model_name:
            for model in config["models"]:
                if model_name.lower() in model["model_name"].lower():
                    return model

        return None

    def update(self, model_id, api_key=None, model_name=None):
        """更新模型"""
        config = self._read_config()

        for model in config["models"]:
            if model["id"] == model_id:
                if api_key:
                    model["api_key"] = api_key
                if model_name:
                    model["model_name"] = model_name

                self._write_config(config)

                print(f"✓ 模型更新成功: {model_id}")
                if api_key:
                    print(f"  API密钥已更新")
                if model_name:
                    print(f"  模型名称: {model['model_name']}")

                return model

        print(f"✗ 未找到模型ID: {model_id}")
        return None

    def delete(self, model_id):
        """删除模型"""
        config = self._read_config()

        original_count = len(config["models"])
        config["models"] = [m for m in config["models"] if m["id"] != model_id]

        if len(config["models"]) == original_count:
            print(f"✗ 未找到模型ID: {model_id}")
            return False

        self._write_config(config)
        print(f"✓ 模型已删除: {model_id}")
        return True

    def mark_used(self, model_id):
        """标记模型已使用"""
        config = self._read_config()

        for model in config["models"]:
            if model["id"] == model_id:
                model["last_used"] = datetime.utcnow().isoformat() + "Z"
                self._write_config(config)
                break


def main():
    parser = argparse.ArgumentParser(description="自定义模型管理工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 添加模型
    add_parser = subparsers.add_parser("add", help="添加新模型")
    add_parser.add_argument("--provider", required=True, help="提供商名称（如 nvidia, openai）")
    add_parser.add_argument("--api-key", required=True, help="API密钥")
    add_parser.add_argument("--model-name", required=True, help="模型名称")

    # 列出模型
    list_parser = subparsers.add_parser("list", help="列出所有模型")
    list_parser.add_argument("--provider", help="按提供商过滤")

    # 搜索模型
    search_parser = subparsers.add_parser("search", help="按提供商搜索模型")
    search_parser.add_argument("--provider", required=True, help="提供商名称")

    # 更新模型
    update_parser = subparsers.add_parser("update", help="更新模型配置")
    update_parser.add_argument("--id", required=True, dest="model_id", help="模型ID")
    update_parser.add_argument("--api-key", help="新的API密钥")
    update_parser.add_argument("--model-name", help="新的模型名称")

    # 删除模型
    delete_parser = subparsers.add_parser("delete", help="删除模型")
    delete_parser.add_argument("--id", required=True, dest="model_id", help="模型ID")

    # 获取模型
    get_parser = subparsers.add_parser("get", help="获取模型信息")
    get_parser.add_argument("--id", dest="model_id", help="模型ID")
    get_parser.add_argument("--name", dest="model_name", help="模型名称（模糊匹配）")

    args = parser.parse_args()
    manager = ModelManager()

    if args.command == "add":
        manager.add(args.provider, args.api_key, args.model_name)

    elif args.command == "list":
        manager.list(provider=args.provider)

    elif args.command == "search":
        manager.search(args.provider)

    elif args.command == "update":
        manager.update(args.model_id, args.api_key, args.model_name)

    elif args.command == "delete":
        manager.delete(args.model_id)

    elif args.command == "get":
        model = manager.get_model(args.model_id, args.model_name)
        if model:
            print(json.dumps(model, indent=2, ensure_ascii=False))
        else:
            print("未找到匹配的模型")
            sys.exit(1)


if __name__ == "__main__":
    main()
