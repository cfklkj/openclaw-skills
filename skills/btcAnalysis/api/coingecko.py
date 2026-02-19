#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CoinGecko API 封装"""

import requests
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import get_config


class CoinGeckoAPI:
    """CoinGecko API 客户端"""

    def __init__(self):
        config = get_config()
        self.base_url = config["coingecko"]["base_url"]
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

    def get_price(self, coin_id="bitcoin", vs_currencies="usd"):
        """
        获取价格

        Args:
            coin_id: 币种ID（bitcoin, ethereum, etc.）
            vs_currencies: 计价货币（usd, cny, eur, etc.）
        """
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currencies,
            "include_24hr_change": "true",
            "include_24hr_vol": "true"
        }
        return self._get(url, params)

    def get_coin_details(self, coin_id="bitcoin"):
        """获取币种详细信息"""
        url = f"{self.base_url}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false"
        }
        return self._get(url, params)

    def get_market_chart(self, coin_id="bitcoin", vs_currency="usd", days=1):
        """
        获取市场图表数据

        Args:
            coin_id: 币种ID
            vs_currency: 计价货币
            days: 天数（1, 7, 30, 90, 180, 365, max）
        """
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "hourly" if days <= 1 else "daily"
        }
        return self._get(url, params)

    def search_coins(self, query):
        """搜索币种"""
        url = f"{self.base_url}/search"
        params = {"query": query}
        return self._get(url, params)


# 单例实例
_coingecko_api = None

def get_coingecko_api():
    """获取 CoinGecko API 客户端（单例）"""
    global _coingecko_api
    if _coingecko_api is None:
        _coingecko_api = CoinGeckoAPI()
    return _coingecko_api
