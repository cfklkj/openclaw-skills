#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""市场数据查询与展示"""

import sys
import os
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.binance import get_binance_api
from api.coingecko import get_coingecko_api


class MarketAnalyzer:
    """市场数据分析器"""

    def __init__(self):
        self.binance = get_binance_api()
        self.coingecko = get_coingecko_api()

    def format_price(self, price):
        """格式化价格显示"""
        if price >= 1000:
            return f"${price:,.2f}"
        elif price >= 1:
            return f"${price:.4f}"
        else:
            return f"${price:.8f}"

    def format_volume(self, volume):
        """格式化成交量"""
        if volume >= 1e9:
            return f"{volume/1e9:.2f}B"
        elif volume >= 1e6:
            return f"{volume/1e6:.2f}M"
        elif volume >= 1e3:
            return f"{volume/1e3:.2f}K"
        return f"{volume:.2f}"

    def format_percentage(self, pct):
        """格式化百分比"""
        return f"{pct:+.2f}%" if pct is not None else "N/A"

    def show_price(self, symbol="BTC"):
        """显示价格信息"""
        print(f"\n=== {symbol.upper()} 价格信息 ===\n")

        # 从币安获取24小时行情
        ticker = self.binance.get_24h_ticker(symbol)
        if not ticker:
            print(f"无法获取 {symbol} 的数据")
            return

        # 注意：币安24h ticker中使用 lastPrice 而不是 price
        price = float(ticker.get('lastPrice', ticker.get('price', 0)))
        change_24h = float(ticker.get('priceChangePercent', 0))
        high_24h = float(ticker.get('highPrice', 0))
        low_24h = float(ticker.get('lowPrice', 0))
        volume_24h = float(ticker.get('quoteVolume', 0))

        print(f"当前价格: {self.format_price(price)}")
        print(f"24h涨跌:  {self.format_percentage(change_24h)}")
        print(f"24h成交量: {self.format_volume(volume_24h)} USD")
        print(f"24h最高价: {self.format_price(high_24h)}")
        print(f"24h最低价: {self.format_price(low_24h)}")

        # 资金费率
        funding = self.binance.get_funding_rate(symbol)
        if funding and 'lastFundingRate' in funding:
            rate = float(funding['lastFundingRate']) * 100
            print(f"资金费率:  {rate:+.4f}%")
            print(f"标记价格:  {self.format_price(float(funding.get('markPrice', 0)))}")

        print()

    def show_klines(self, symbol="BTC", interval="1h", limit=50):
        """显示 K 线数据"""
        print(f"\n=== {symbol.upper()} K线数据 ({interval}) ===\n")

        klines = self.binance.get_klines(symbol, interval, limit)
        if not klines:
            print("无法获取K线数据")
            return

        print(f"{'时间':<20} {'开盘':<12} {'最高':<12} {'最低':<12} {'收盘':<12} {'成交量'}")
        print("-" * 85)

        for kline in reversed(klines[:10]):
            open_time = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            print(f"{open_time:<20} "
                  f"{self.format_price(open_price):<12} "
                  f"{self.format_price(high_price):<12} "
                  f"{self.format_price(low_price):<12} "
                  f"{self.format_price(close_price):<12} "
                  f"{self.format_volume(volume)}")

        print(f"\n显示最近 10 条数据（共获取 {len(klines)} 条）")
        print()

    def show_orderbook(self, symbol="BTC", limit=20):
        """显示订单簿深度"""
        print(f"\n=== {symbol.upper()} 订单簿深度 ===\n")

        depth = self.binance.get_orderbook(symbol, limit)
        if not depth:
            print("无法获取订单簿数据")
            return

        asks = depth.get('asks', [])[:5]  # 卖单（前5档）
        bids = depth.get('bids', [])[:5]   # 买单（前5档）

        print("卖单 (Asks):")
        print(f"{'价格':<15} {'数量':<20}")
        print("-" * 35)
        for ask in reversed(asks):
            price = float(ask[0])
            qty = float(ask[1])
            print(f"{self.format_price(price):<15} {qty:<20.4f}")

        print()

        print("买单 (Bids):")
        print(f"{'价格':<15} {'数量':<20}")
        print("-" * 35)
        for bid in bids:
            price = float(bid[0])
            qty = float(bid[1])
            print(f"{self.format_price(price):<15} {qty:<20.4f}")

        print()

    def show_volume(self, symbol="BTC"):
        """显示成交量统计"""
        print(f"\n=== {symbol.upper()} 成交量统计 ===\n")

        ticker = self.binance.get_24h_ticker(symbol)
        if not ticker:
            print("无法获取数据")
            return

        quote_volume = float(ticker.get('quoteVolume', 0))
        base_volume = float(ticker.get('volume', 0))
        trade_count = ticker.get('count', 0)

        print(f"24h成交额: {self.format_volume(quote_volume)} USD")
        print(f"24h成交量: {base_volume:.4f} {symbol.upper()}")
        print(f"24h成交笔数: {trade_count:,}")
        print()
