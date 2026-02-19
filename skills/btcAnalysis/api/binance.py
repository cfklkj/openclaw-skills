#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""币安 API 封装"""

import requests
import time
from datetime import datetime
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import get_config


class BinanceAPI:
    """币安 API 客户端"""

    def __init__(self):
        config = get_config()
        self.base_url = config["binance"]["base_url"]
        self.futures_url = config["binance"]["futures_url"]
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

    def get_price(self, symbol="BTC"):
        """获取实时价格"""
        # 币安 symbol 格式：BTCUSDT
        binance_symbol = f"{symbol.upper()}USDT"
        url = f"{self.base_url}/api/v3/ticker/price"
        params = {"symbol": binance_symbol}
        result = self._get(url, params)
        return result

    def get_24h_ticker(self, symbol="BTC"):
        """获取24小时行情"""
        binance_symbol = f"{symbol.upper()}USDT"
        url = f"{self.base_url}/api/v3/ticker/24hr"
        params = {"symbol": binance_symbol}
        result = self._get(url, params)
        return result

    def get_klines(self, symbol="BTC", interval="1h", limit=100):
        """
        获取 K 线数据

        Args:
            symbol: 交易对符号（BTC）
            interval: 时间间隔（1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M）
            limit: 返回数量（默认100，最大500）
        """
        binance_symbol = f"{symbol.upper()}USDT"
        url = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": binance_symbol,
            "interval": interval,
            "limit": limit
        }
        result = self._get(url, params)
        return result

    def get_orderbook(self, symbol="BTC", limit=20):
        """
        获取订单簿深度

        Args:
            symbol: 交易对符号（BTC）
            limit: 深度档位（5, 10, 20, 50, 100, 500, 1000）
        """
        binance_symbol = f"{symbol.upper()}USDT"
        url = f"{self.base_url}/api/v3/depth"
        params = {
            "symbol": binance_symbol,
            "limit": limit
        }
        result = self._get(url, params)
        return result

    def get_funding_rate(self, symbol="BTC"):
        """获取资金费率（期货）"""
        binance_symbol = f"{symbol.upper()}USDT"
        url = f"{self.futures_url}/fapi/v1/premiumIndex"
        params = {"symbol": binance_symbol}
        result = self._get(url, params)
        return result

    def get_open_interest(self, symbol="BTC"):
        """获取未平仓合约量"""
        binance_symbol = f"{symbol.upper()}USDT"
        url = f"{self.futures_url}/fapi/v1/openInterest"
        params = {"symbol": binance_symbol}
        result = self._get(url, params)
        return result

    def get_long_short_ratio(self, symbol="BTC", period="1h"):
        """获取多空比"""
        binance_symbol = f"{symbol.upper()}USDT"
        url = f"{self.futures_url}/futures/data/globalLongShortAccountRatio"
        params = {
            "symbol": binance_symbol,
            "period": period
        }
        result = self._get(url, params)
        return result


# 单例实例
_binance_api = None

def get_binance_api():
    """获取币安 API 客户端（单例）"""
    global _binance_api
    if _binance_api is None:
        _binance_api = BinanceAPI()
    return _binance_api
