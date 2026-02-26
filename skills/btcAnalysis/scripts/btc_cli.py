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
from indicators import get_indicators_display
from onchain import get_onchain_display
from trend import get_trend_display


def main():
    parser = argparse.ArgumentParser(
        description="BTC Analysis - 比特币与加密货币行情分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 市场数据
  btc price btc              # 查询BTC价格
  btc kline btc 1h           # 查看1小时K线
  btc depth btc --limit 20   # 查看订单簿
  
  # 技术指标
  btc rsi btc 1d             # 查看RSI指标
  btc macd btc 1d            # 查看MACD指标
  btc bb btc 1d              # 查看布林带
  btc indicators btc 1d      # 查看所有技术指标
  
  # 链上数据
  btc tvl uniswap            # 查看协议TVL
  btc fees aave              # 查看协议费用
  btc health lido            # 查看协议健康度
  btc chains                 # 查看公链TVL排行
  btc stablecoins            # 查看稳定币市值
  
  # 情绪分析
  btc feargreed              # 恐惧与贪婪指数
  
  # 综合分析
  btc analyze btc            # 综合分析
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

    # ========== 技术指标命令 ==========
    
    # RSI
    rsi_parser = subparsers.add_parser('rsi', help='查看RSI指标')
    rsi_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    rsi_parser.add_argument('interval', nargs='?', default='1d', help='时间间隔（默认: 1d）')
    
    # MACD
    macd_parser = subparsers.add_parser('macd', help='查看MACD指标')
    macd_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    macd_parser.add_argument('interval', nargs='?', default='1d', help='时间间隔（默认: 1d）')
    
    # 布林带
    bb_parser = subparsers.add_parser('bb', help='查看布林带指标')
    bb_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    bb_parser.add_argument('interval', nargs='?', default='1d', help='时间间隔（默认: 1d）')
    
    # 所有技术指标
    indicators_parser = subparsers.add_parser('indicators', aliases=['ti'], help='查看所有技术指标')
    indicators_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    indicators_parser.add_argument('interval', nargs='?', default='1d', help='时间间隔（默认: 1d）')

    # ========== 链上数据命令 ==========
    
    # TVL
    tvl_parser = subparsers.add_parser('tvl', help='查看协议TVL')
    tvl_parser.add_argument('protocol', nargs='?', default='bitcoin', help='协议名称（默认: bitcoin）')
    
    # 费用
    fees_parser = subparsers.add_parser('fees', help='查看协议费用收入')
    fees_parser.add_argument('protocol', nargs='?', default='uniswap', help='协议名称（默认: uniswap）')
    
    # 健康度
    health_parser = subparsers.add_parser('health', help='查看协议健康度评分')
    health_parser.add_argument('protocol', nargs='?', default='lido', help='协议名称（默认: lido）')
    
    # 公链TVL排行
    chains_parser = subparsers.add_parser('chains', help='查看公链TVL排行')
    chains_parser.add_argument('--limit', type=int, default=10, help='显示数量（默认: 10）')
    
    # 单链TVL
    chain_parser = subparsers.add_parser('chain', help='查看单链TVL')
    chain_parser.add_argument('name', nargs='?', default='Ethereum', help='链名称（默认: Ethereum）')
    
    # 稳定币
    stablecoins_parser = subparsers.add_parser('stablecoins', aliases=['sc'], help='查看稳定币市值排行')
    stablecoins_parser.add_argument('--limit', type=int, default=10, help='显示数量（默认: 10）')
    
    # 排行榜（协议TVL）
    ranking_parser = subparsers.add_parser('ranking', aliases=['top'], help='查看协议TVL排行榜')
    ranking_parser.add_argument('--limit', type=int, default=10, help='显示数量（默认: 10）')

    # ========== 情绪分析命令 ==========
    
    # 恐惧与贪婪指数
    subparsers.add_parser('feargreed', aliases=['fg'], help='恐惧与贪婪指数')

    # ========== 趋势分析命令 ==========
    
    # 趋势分析
    trend_parser = subparsers.add_parser('trend', help='趋势分析（多维交叉验证）')
    trend_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    trend_parser.add_argument('interval', nargs='?', default='1d', help='时间周期（默认: 1d）')
    
    # 信号摘要
    signal_parser = subparsers.add_parser('signal', help='交易信号摘要')
    signal_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    signal_parser.add_argument('interval', nargs='?', default='1d', help='时间周期（默认: 1d）')

    # ========== 综合分析命令 ==========
    
    # 综合分析
    analyze_parser = subparsers.add_parser('analyze', help='综合分析')
    analyze_parser.add_argument('symbol', nargs='?', default='BTC', help='币种代码（默认: BTC）')
    
    args = parser.parse_args()

    # 执行命令
    market = MarketAnalyzer()
    sentiment = SentimentAnalyzer()
    indicators = get_indicators_display()
    onchain = get_onchain_display()
    
    # 市场数据命令
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
    
    # 技术指标命令
    elif args.command == 'rsi':
        indicators.show_rsi(args.symbol.upper(), args.interval)
    
    elif args.command == 'macd':
        indicators.show_macd(args.symbol.upper(), args.interval)
    
    elif args.command == 'bb':
        indicators.show_bollinger(args.symbol.upper(), args.interval)
    
    elif args.command in ['indicators', 'ti']:
        indicators.show_all(args.symbol.upper(), args.interval)
    
    # 链上数据命令
    elif args.command == 'tvl':
        onchain.show_tvl(args.protocol)
    
    elif args.command == 'fees':
        onchain.show_fees(args.protocol)
    
    elif args.command == 'health':
        onchain.show_health(args.protocol)
    
    elif args.command == 'chains':
        onchain.show_top_chains(args.limit)
    
    elif args.command == 'chain':
        onchain.show_chain_tvl(args.name)
    
    elif args.command in ['stablecoins', 'sc']:
        onchain.show_stablecoins(args.limit)
    
    elif args.command in ['ranking', 'top']:
        onchain.show_top_protocols(args.limit)
    
    # 情绪分析命令
    elif args.command in ['feargreed', 'fg']:
        sentiment.show_fear_greed_index()
    
    # 趋势分析命令
    elif args.command == 'trend':
        trend = get_trend_display()
        trend.show_trend(args.symbol.upper(), args.interval)
    
    elif args.command == 'signal':
        trend = get_trend_display()
        trend.show_signals(args.symbol.upper(), args.interval)
    
    # 综合分析
    elif args.command == 'analyze':
        print(f"\n=== {args.symbol.upper()} 综合分析 ===\n")
        print("[市场数据]")
        market.show_price(args.symbol.upper())
        print("[技术指标]")
        indicators.show_all(args.symbol.upper(), '1d')
        print("[链上数据]")
        onchain.show_tvl(args.symbol.lower())
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
