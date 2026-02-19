#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Alternative.me API 封装（恐惧与贪婪指数）"""

import requests
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import get_config


class AlternativeAPI:
    """Alternative.me API 客户端"""

    def __init__(self):
        config = get_config()
        self.base_url = config["alternative"]["base_url"]
        self.session = requests.Session()

    def _get(self, url, params=None):
        """发送 GET 请求"""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_fear_greed_index(self, limit=1):
        """
        获取恐惧与贪婪指数

        Args:
            limit: 返回数量（默认1，最多7天）
        """
        url = f"{self.base_url}/fng/"
        params = {"limit": limit}
        return self._get(url, params)


# 单例实例
_alternative_api = None

def get_alternative_api():
    """获取 Alternative API 客户端（单例）"""
    global _alternative_api
    if _alternative_api is None:
        _alternative_api = AlternativeAPI()
    return _alternative_api
