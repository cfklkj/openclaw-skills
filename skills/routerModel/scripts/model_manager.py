#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义模型管理脚本 - 直接管理 ~/.openclaw/openclaw.json
提供模型的增删查改功能
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

# OpenClaw 配置文件路径
CONFIG_FILE = Path.home() / ".openclaw" / "openclaw.json"


class ModelManager:
    """模型管理器"""

    def __init__(self):
        self.config_file = CONFIG_FILE
        self._ensure_config()

    def _ensure_config(self):
        """确保配置文件存在"""
        if not self.config_file.exists():
            print(f"✗ 配置文件不存在: {self.config_file}")
            print("请先安装并配置 OpenClaw")
            sys.exit(1)

    def _read_config(self):
        """读取配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"✗ 配置文件格式错误: {self.config_file}")
            sys.exit(1)

    def _write_config(self, config):
        """写入配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _ensure_models_structure(self, config):
        """确保 models 结构存在"""
        if "models" not in config:
            config["models"] = {}
        if "providers" not in config["models"]:
            config["models"]["providers"] = {}
        return config

    def _init_provider(self, config, provider, api_key, base_url=None, api_type="openai-completions"):
        """初始化提供商配置"""
        provider_config = {
            "apiKey": api_key,
            "api": api_type
        }
        if base_url:
            provider_config["baseUrl"] = base_url
        return provider_config

    def _create_model_entry(self, model_id, model_name, **kwargs):
        """创建模型条目（默认值）"""
        model_entry = {
            "id": model_id,
            "name": model_name,
            "reasoning": kwargs.get("reasoning", False),
            "input": kwargs.get("input", ["text"]),
            "cost": kwargs.get("cost", {
                "input": 0,
                "output": 0,
                "cacheRead": 0,
                "cacheWrite": 0
            }),
            "contextWindow": kwargs.get("contextWindow", 128000),
            "maxTokens": kwargs.get("maxTokens", 16384)
        }
        return model_entry

    def list_providers(self):
        """列出所有提供商"""
        config = self._read_config()

        if not config.get("models", {}).get("providers"):
            print("暂无已配置的提供商")
            return

        providers = config["models"]["providers"]

        print(f"\n{'提供商':<15} {'Base URL':<50} {'API密钥前缀':<20}")
        print("-" * 85)

        for provider_name, provider_config in providers.items():
            base_url = provider_config.get("baseUrl", "N/A")
            api_key = provider_config.get("apiKey", "N/A")
            api_key_prefix = api_key[:8] + "..." if len(api_key) > 8 else api_key
            print(f"{provider_name:<15} {base_url:<50} {api_key_prefix:<20}")

        print(f"\n总计: {len(providers)} 个提供商")

    def list_models(self, provider=None):
        """列出模型"""
        config = self._read_config()

        providers = config.get("models", {}).get("providers", {})
        if not providers:
            print("暂无已配置的提供商")
            return

        # 如果指定了提供商，只列出该提供商的模型
        if provider:
            if provider.lower() not in [p.lower() for p in providers.keys()]:
                print(f"✗ 未找到提供商: {provider}")
                return

            actual_provider = next(p for p in providers.keys() if p.lower() == provider.lower())
            provider_config = providers[actual_provider]
            models = provider_config.get("models", [])

            if not models:
                print(f"提供商 {actual_provider} 暂无模型")
                return

            print(f"\n提供商: {actual_provider}")
            print(f"{'模型ID':<60} {'名称':<40} {'上下文窗口':<12}")
            print("-" * 112)

            for model in models:
                model_id = model.get("id", "N/A")
                name = model.get("name", "N/A")
                context = model.get("contextWindow", "N/A")
                print(f"{model_id:<60} {name:<40} {context:<12}")

            print(f"\n总计: {len(models)} 个模型")
        else:
            # 列出所有提供商的所有模型
            print(f"\n{'提供商':<12} {'模型ID':<50} {'名称':<40}")
            print("-" * 102)

            total_models = 0
            for provider_name, provider_config in providers.items():
                models = provider_config.get("models", [])
                for model in models:
                    model_id = model.get("id", "N/A")
                    name = model.get("name", "N/A")
                    print(f"{provider_name:<12} {model_id:<50} {name:<40}")
                    total_models += 1

            print(f"\n总计: {total_models} 个模型，{len(providers)} 个提供商")

    def add_provider(self, provider, api_key, base_url=None, api_type="openai-completions"):
        """添加提供商"""
        config = self._read_config()
        config = self.__ensure_models_structure(config)

        providers = config["models"]["providers"]

        # 检查提供商是否已存在
        if provider in providers:
            print(f"✗ 提供商 '{provider}' 已存在")
            return False

        # 创建提供商配置
        providers[provider] = self._init_provider(provider, api_key, base_url, api_type)

        self._write_config(config)

        print(f"✓ 提供商添加成功")
        print(f"  名称: {provider}")
        print(f"  API密钥: {api_key[:8]}...")
        if base_url:
            print(f"  Base URL: {base_url}")
        print(f"  API类型: {api_type}")

        return True

    def add_model(self, provider, model_id, **kwargs):
        """添加模型"""
        config = self._read_config()
        config = self.__ensure_models_structure(config)

        providers = config["models"]["providers"]

        # 检查提供商是否存在
        if provider not in providers:
            print(f"✗ 提供商 '{provider}' 不存在")
            print(f"请先使用 add-provider 添加该提供商")
            return False

        # 创建模型条目
        model_entry = self._create_model_entry(model_id, model_id, **kwargs)

        # 添加模型
        providers[provider]["models"] = providers[provider].get("models", [])
        providers[provider]["models"].append(model_entry)

        self._write_config(config)

        print(f"✓ 模型添加成功")
        print(f"  提供商: {provider}")
        print(f"  模型ID: {model_id}")

        return True

    def add_model_quick(self, provider, api_key, model_name, base_url=None):
        """快速添加：提供商 + 模型"""
        # 先添加提供商（如果不存在）
        provider_exists = provider in self._read_config().get("models", {}).get("providers", {})

        if not provider_exists:
            self.add_provider(provider, api_key, base_url)

        # 添加模型
        return self.add_model(provider, model_name)

    def update_provider(self, provider, api_key=None, base_url=None):
        """更新提供商配置"""
        config = self._read_config()

        providers = config.get("models", {}).get("providers", {})
        if provider not in providers:
            print(f"✗ 提供商 '{provider}' 不存在")
            return False

        provider_config = providers[provider]

        if api_key:
            provider_config["apiKey"] = api_key
            print(f"✓ API密钥已更新")
        if base_url:
            provider_config["baseUrl"] = base_url
            print(f"✓ Base URL已更新: {base_url}")

        self._write_config(config)
        print(f"✓ 提供商 '{provider}' 更新成功")
        return True

    def delete_model(self, provider, model_id):
        """删除模型"""
        config = self._read_config()

        providers = config.get("models", {}).get("providers", {})
        if provider not in providers:
            print(f"✗ 提供商 '{provider}' 不存在")
            return False

        provider_config = providers[provider]
        models = provider_config.get("models", [])

        original_count = len(models)
        provider_config["models"] = [m for m in models if m.get("id") != model_id]

        if len(provider_config["models"]) == original_count:
            print(f"✗ 未找到模型ID: {model_id}")
            return False

        self._write_config(config)
        print(f"✓ 模型已删除: {model_id}")
        return True

    def delete_provider(self, provider):
        """删除提供商及其所有模型"""
        config = self._read_config()

        providers = config.get("models", {}).get("providers", {})
        if provider not in providers:
            print(f"✗ 提供商 '{provider}' 不存在")
            return False

        del providers[provider]

        self._write_config(config)
        print(f"✓ 提供商 '{provider}' 已删除")
        return True


def main():
    parser = argparse.ArgumentParser(description="OpenClaw 模型管理工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 列出提供商
    list_providers_parser = subparsers.add_parser("list-providers", help="列出所有提供商")

    # 列出模型
    list_models_parser = subparsers.add_parser("list-models", help="列出所有模型")
    list_models_parser.add_argument("--provider", help="按提供商过滤")

    # 添加提供商
    add_provider_parser = subparsers.add_parser("add-provider", help="添加提供商")
    add_provider_parser.add_argument("--name", required=True, help="提供商名称")
    add_provider_parser.add_argument("--api-key", required=True, help="API密钥")
    add_provider_parser.add_argument("--base-url", help="Base URL")
    add_provider_parser.add_argument("--api-type", default="openai-completions", help="API类型")

    # 添加模型
    add_model_parser = subparsers.add_parser("add-model", help="添加模型")
    add_model_parser.add_argument("--provider", required=True, help="提供商名称")
    add_model_parser.add_argument("--id", required=True, help="模型ID")
    add_model_parser.add_argument("--name", help="模型名称（默认与ID相同）")
    add_model_parser.add_argument("--context-window", type=int, default=128000, help="上下文窗口大小")
    add_model_parser.add_argument("--max-tokens", type=int, default=16384, help="最大token数")

    # 快速添加（提供商 + 模型）
    quick_add_parser = subparsers.add_parser("add", help="快速添加提供商和模型")
    quick_add_parser.add_argument("--provider", required=True, help="提供商名称")
    quick_add_parser.add_argument("--api-key", required=True, help="API密钥")
    quick_add_parser.add_argument("--model-name", required=True, help="模型名称")
    quick_add_parser.add_argument("--base-url", help="Base URL")

    # 更新提供商
    update_provider_parser = subparsers.add_parser("update-provider", help="更新提供商配置")
    update_provider_parser.add_argument("--name", required=True, help="提供商名称")
    update_provider_parser.add_argument("--api-key", help="新的API密钥")
    update_provider_parser.add_argument("--base-url", help="新的Base URL")

    # 删除模型
    delete_model_parser = subparsers.add_parser("delete-model", help="删除模型")
    delete_model_parser.add_argument("--provider", required=True, help="提供商名称")
    delete_model_parser.add_argument("--id", required=True, dest="model_id", help="模型ID")

    # 删除提供商
    delete_provider_parser = subparsers.add_parser("delete-provider", help="删除提供商")
    delete_provider_parser.add_argument("--name", required=True, help="提供商名称")

    args = parser.parse_args()
    manager = ModelManager()

    if args.command == "list-providers":
        manager.list_providers()

    elif args.command == "list-models":
        manager.list_models(provider=args.provider)

    elif args.command == "add-provider":
        manager.add_provider(args.name, args.api_key, args.base_url, args.api_type)

    elif args.command == "add-model":
        manager.add_model(
            args.provider,
            args.id,
            name=args.name or args.id,
            contextWindow=args.context_window,
            maxTokens=args.max_tokens
        )

    elif args.command == "add":
        manager.add_model_quick(args.provider, args.api_key, args.model_name, args.base_url)

    elif args.command == "update-provider":
        manager.update_provider(args.name, args.api_key, args.base_url)

    elif args.command == "delete-model":
        manager.delete_model(args.provider, args.model_id)

    elif args.command == "delete-provider":
        manager.delete_provider(args.name)


if __name__ == "__main__":
    main()
