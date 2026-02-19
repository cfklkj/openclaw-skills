#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型应用脚本
将配置的模型应用到当前会话
"""

import json
import argparse
import sys
from pathlib import Path

# 配置文件路径
CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / "model_config.json"

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ModelApplier:
    """模型应用器"""

    def __init__(self):
        self.config_file = CONFIG_FILE

    def _read_config(self):
        """读取配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"✗ 配置文件不存在: {self.config_file}")
            print("请先使用 model_manager.py 添加模型")
            return None

    def _find_model(self, model_id=None, model_name=None):
        """查找模型"""
        config = self._read_config()
        if not config:
            return None

        # 通过ID查找
        if model_id:
            for model in config["models"]:
                if model["id"] == model_id:
                    return model
            print(f"✗ 未找到模型ID: {model_id}")
            return None

        # 通过名称查找（模糊匹配）
        if model_name:
            matches = []
            for model in config["models"]:
                if model_name.lower() in model["model_name"].lower():
                    matches.append(model)

            if len(matches) == 0:
                print(f"✗ 未找到匹配 '{model_name}' 的模型")
                return None
            elif len(matches) == 1:
                return matches[0]
            else:
                print(f"✗ 找到多个匹配的模型：")
                for m in matches:
                    print(f"  - {m['id']}: {m['model_name']}")
                print("请使用 --id 参数指定精确的模型ID")
                return None

        return None

    def list_models(self):
        """列出所有可用模型"""
        config = self._read_config()
        if not config:
            return

        if not config["models"]:
            print("暂无已配置的模型")
            return

        print(f"\n{'ID':<15} {'提供商':<12} {'模型名称':<40}")
        print("-" * 67)

        for model in config["models"]:
            print(f"{model['id']:<15} {model['provider']:<12} {model['model_name']:<40}")

    def apply(self, model_id=None, model_name=None, dry_run=False):
        """应用模型到会话"""

        # 如果没有指定模型，只列出可用模型
        if not model_id and not model_name:
            print("可用模型：")
            self.list_models()
            return

        # 查找模型
        model = self._find_model(model_id, model_name)
        if not model:
            return

        # 显示将要应用的模型信息
        print(f"\n将要应用的模型：")
        print(f"  提供商: {model['provider']}")
        print(f"  模型名称: {model['model_name']}")
        print(f"  API密钥: {model['api_key'][:8]}...")

        if dry_run:
            print("\n[DRY RUN] 不会实际应用模型")
            return

        # 生成配置补丁
        # 注意：这里需要根据 OpenClaw 的实际 API 结构来调整
        # 假设可以通过 environment 变量设置 API key
        config_patch = {
            "environment": {
                "OPENAI_API_KEY": model["api_key"]
            },
            "model": model["model_name"]
        }

        # 输出配置用于说明如何应用
        print("\n配置补丁（需要通过 OpenClaw API 应用）：")
        print(json.dumps(config_patch, indent=2, ensure_ascii=False))

        print("\n提示：当前脚本生成配置，需要通过 OpenClaw Gateway API 实际应用")
        print("可以使用以下命令：")
        print(f"  openclaw gateway config.patch '{json.dumps(config_patch)}'")

        # 尝试通过 CLI 应用配置
        try:
            import subprocess
            result = subprocess.run(
                ["openclaw", "gateway", "config.patch", json.dumps(config_patch)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("\n✓ 模型已成功应用到会话")
            else:
                print(f"\n✗ 应用失败: {result.stderr}")
                sys.exit(1)

        except FileNotFoundError:
            print("\n提示：未找到 openclaw 命令，请手动使用以下命令应用配置：")
            print(f"  openclaw gateway config.patch '{json.dumps(config_patch)}'")
        except subprocess.TimeoutExpired:
            print("\n✗ 操作超时")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="将模型应用到当前会话")
    parser.add_argument("--id", dest="model_id", help="模型ID")
    parser.add_argument("--name", dest="model_name", help="模型名称（模糊匹配）")
    parser.add_argument("--dry-run", action="store_true", help="只显示不实际应用")
    parser.add_argument("--list", action="store_true", help="列出所有可用模型")

    args = parser.parse_args()
    applier = ModelApplier()

    if args.list:
        applier.list_models()
    else:
        applier.apply(args.model_id, args.model_name, args.dry_run)


if __name__ == "__main__":
    main()
