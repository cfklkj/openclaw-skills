#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置管理"""

import json
import sys
import os
from pathlib import Path

# 获取 scripts 目录
scripts_dir = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径（scripts目录）
CONFIG_FILE = Path(scripts_dir) / "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "binance": {
        "base_url": "https://api.binance.com",
        "futures_url": "https://fapi.binance.com"
    },
    "defillama": {
        "base_url": "https://api.llama.fi"
    },
    "coingecko": {
        "base_url": "https://api.coingecko.com/api/v3"
    },
    "alternative": {
        "base_url": "https://api.alternative.me"
    },
    "cache": {
        "enabled": True,
        "ttl": 300  # 5分钟缓存
    }
}


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"警告: 加载配置文件失败，使用默认配置: {e}")
    return DEFAULT_CONFIG


def save_config(config):
    """保存配置"""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"保存配置失败: {e}")


def get_config():
    """获取配置（单例）"""
    if not hasattr(get_config, '_config'):
        get_config._config = load_config()
    return get_config._config
