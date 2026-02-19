#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型应用脚本 - 直接管理 ~/.openclaw/openclaw.json
将模型应用到当前会话
"""

import json
import argparse
import sys
from pathlib import Path

# OpenClaw 配置文件路径
CONFIG_FILE = Path.home() / ".openclaw" / "openclaw.json"


class ModelApplier:
    """模型应用器"""

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

    def _ensure_agents_structure(self, config):
        """确保 agents 结构存在"""
        if "agents" not in config:
            config["agents"] = {}
        if "defaults" not in config["agents"]:
            config["agents"]["defaults"] = {}
        if "model" not in config["agents"]["defaults"]:
            config["agents"]["defaults"]["model"] = {}
        return config

    def get_current_model(self):
        """获取当前默认模型"""
        config = self._read_config()

        try:
            primary = config["agents"]["defaults"]["model"]["primary"]
            print(f"当前默认模型: {primary}")
            return primary
        except KeyError:
            print("未设置默认模型")
            return None

    def list_available_models(self):
        """列出所有可用模型"""
        config = self._read_config()

        providers = config.get("models", {}).get("providers", {})
        if not providers:
            print("暂无已配置的模型")
            return

        print(f"\n{'提供商':<12} {'模型ID':<50}")
        print("-" * 62)

        for provider_name, provider_config in providers.items():
            models = provider_config.get("models", [])
            for model in models:
                model_id = model.get("id", "N/A")
                print(f"{provider_name:<12} {model_id:<50}")

        total_models = sum(len(p.get("models", [])) for p in providers.values())
        print(f"\n总计: {total_models} 个模型，{len(providers)} 个提供商")

    def _find_model(self, model_spec):
        """
        查找模型（支持多种格式）：
        - {model_id} 如 "z-ai/glm4.7"
        - {provider}/{model_id} 如 "nvidia/z-ai/glm4.7"
        """
        config = self._read_config()

        providers = config.get("models", {}).get("providers", {})
        if not providers:
            print("✗ 暂无已配置的模型")
            return None, None

        # 尝试直接匹配 {provider}/{model_id} 格式
        if "/" in model_spec:
            parts = model_spec.split("/", 1)
            if len(parts) == 2:
                provider, model_id = parts
                # 检查指定提供商
                for prov_name, prov_config in providers.items():
                    if prov_name.lower() == provider.lower():
                        for model in prov_config.get("models", []):
                            if model.get("id") == model_id:
                                return prov_name, model

        # 尝试模糊匹配模型ID
        for provider_name, provider_config in providers.items():
            for model in provider_config.get("models", []):
                if model_spec.lower() in model.get("id", "").lower():
                    return provider_name, model

        return None, None

    def apply_model(self, model_spec, dry_run=False):
        """应用模型为默认模型"""
        # 查找模型
        provider_name, model = self._find_model(model_spec)

        if not model:
            print(f"✗ 未找到匹配 '{model_spec}' 的模型")
            print("\n可用模型：")
            self.list_available_models()
            return False

        model_id = model.get("id")

        # 显示将要应用的模型信息
        print(f"\n将要应用的模型：")
        print(f"  提供商: {provider_name}")
        print(f"  模型ID: {model_id}")
        print(f"  模型名称: {model.get('name', 'N/A')}")

        # 获取当前模型
        config = self._read_config()
        try:
            current_model = config["agents"]["defaults"]["model"]["primary"]
            if current_model == f"{provider_name}/{model_id}":
                print(f"\nℹ  这已经是当前默认模型")
                return True
        except KeyError:
            pass

        if dry_run:
            print("\n[DRY RUN] 不会实际应用模型")
            print(f"将设置默认模型为: {provider_name}/{model_id}")
            return True

        # 确保结构存在
        config = self._ensure_agents_structure(config)

        # 设置默认模型
        config["agents"]["defaults"]["model"]["primary"] = f"{provider_name}/{model_id}"

        # 写入配置
        self._write_config(config)

        print(f"\n✓ 已设置默认模型: {provider_name}/{model_id}")
        print("\n提示：修改已生效，但正在运行的会话可能需要重启才能使用新模型")
        print("重启命令: openclaw gateway restart")

        return True

    def list_session_models(self):
        """列出当前会话可用的模型"""
        config = self._read_config()

        # 默认模型
        try:
            primary = config["agents"]["defaults"]["model"]["primary"]
            print(f"\n默认模型: {primary}")
        except KeyError:
            print("\n默认模型: 未设置")

        # agent列表模型
        try:
            models = config["agents"]["defaults"]["models"]
            if models:
                print(f"\n可用模型列表: {len(models)} 个")
                for model_id in models.keys():
                    print(f"  - {model_id}")
        except KeyError:
            print("\n可用模型列表: 未配置")


def main():
    parser = argparse.ArgumentParser(description="将模型应用到当前会话")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 应用模型
    apply_parser = subparsers.add_parser("apply", help="应用模型为默认")
    apply_parser.add_argument("model_spec", help="模型ID或{provider}/{model_id}")
    apply_parser.add_argument("--dry-run", action="store_true", help="只显示不实际应用")

    # 列出可用模型
    list_parser = subparsers.add_parser("list", help="列出所有可用模型")

    # 获取当前模型
    current_parser = subparsers.add_parser("current", help="获取当前默认模型")

    # 列出会话模型
    session_parser = subparsers.add_parser("session", help="列出当前会话配置")

    args = parser.parse_args()
    applier = ModelApplier()

    if args.command == "apply":
        applier.apply_model(args.model_spec, args.dry_run)

    elif args.command == "list":
        applier.list_available_models()

    elif args.command == "current":
        applier.get_current_model()

    elif args.command == "session":
        applier.list_session_models()


if __name__ == "__main__":
    main()
