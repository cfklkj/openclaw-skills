#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BTC Analysis - 命令行工具"""

import sys
import os
import argparse

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from market import MarketAnalyzer
from sentiment import SentimentAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="BTC Analysis - 比特币与加密货币行情分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  btc price btc              # 查询BTC价格
  btc kline btc 1h           # 查看1小时K线
  btc depth btc --limit 20   # 查看订单簿
  btc feargreed              # 恐惧与贪婪指数
        """
    )

    subparsers = parser.add_subparsers(dest='command', required=True, help='可用命令')

    # ========== 市场数据命令 ==========

    # 价格查询
    price_parser = subparsers.add_parser('price', help='查询实时价格')
    price_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')

    # K线数据
    kline_parser = subparsers.add_parser('kline', help='查看K线数据')
    kline_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    kline_parser.add_argument('interval', nargs='?', default='1h', help='时间间隔（默认: 1h）')
    kline_parser.add_argument('--limit', type=int, default=50, help='K线数量（默认: 50）')

    # 订单簿
    depth_parser = subparsers.add_parser('depth', help='查看订单簿深度')
    depth_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    depth_parser.add_argument('--limit', type=int, default=20, help='深度档位（默认: 20）')

    # 成交量
    volume_parser = subparsers.add_parser('volume', help='查看成交量统计')
    volume_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')

    # ========== 情绪分析命令 ==========

    # 恐惧与贪婪指数
    subparsers.add_parser('feargreed', help='恐惧与贪婪指数')

    # ========== 综合分析命令 ==========

    # 综合分析
    analyze_parser = subparsers.add_parser('analyze', help='综合分析')
    analyze_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')

    args = parser.parse_args()

    # 执行命令
    market = MarketAnalyzer()
    sentiment = SentimentAnalyzer()

    if args.command == 'price':
        market.show_price(args.symbol.upper())

    elif args.command == 'kline':
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
        if args.interval not in valid_intervals:
            print(f"错误: 无效的时间间隔 '{args.interval}'")
            print(f"可用间隔: {', '.join(valid_intervals)}")
            return 1
        market.show_klines(args.symbol.upper(), args.interval, args.limit)

    elif args.command == 'depth':
        valid_limits = [5, 10, 20, 50, 100, 500, 1000]
        if args.limit not in valid_limits:
            print(f"错误: 无效的深度档位 '{args.limit}'")
            print(f"可用档位: {', '.join(map(str, valid_limits))}")
            return 1
        market.show_orderbook(args.symbol.upper(), args.limit)

    elif args.command == 'volume':
        market.show_volume(args.symbol.upper())

    elif args.command == 'feargreed':
        sentiment.show_fear_greed_index()

    elif args.command == 'analyze':
        print(f"\n=== {args.symbol.upper()} 综合分析 ===\n")
        print("[市场数据]")
        market.show_price(args.symbol.upper())
        print("[情绪指标]")
        sentiment.show_fear_greed_index()
        print("\n注意: 本分析仅供参考，不构成投资建议\n")

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)
