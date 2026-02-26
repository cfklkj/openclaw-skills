#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""技术指标分析模块"""

import sys
import os
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.binance import get_binance_api


class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        self.binance = get_binance_api()
    
    def calculate_sma(self, data, period):
        """
        计算简单移动平均线 (SMA)
        
        Args:
            data: 价格数据列表
            period: 周期
        
        Returns:
            SMA值列表
        """
        if len(data) < period:
            return None
        return sum(data[-period:]) / period
    
    def calculate_ema(self, data, period):
        """
        计算指数移动平均线 (EMA)
        
        Args:
            data: 价格数据列表
            period: 周期
        
        Returns:
            EMA值
        """
        if len(data) < period:
            return None
        
        # EMA = (Close - previous EMA) * multiplier + previous EMA
        multiplier = 2 / (period + 1)
        
        # 第一个EMA用SMA
        ema = sum(data[:period]) / period
        
        for price in data[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_rsi(self, data, period=14):
        """
        计算相对强弱指数 (RSI)
        
        Args:
            data: 价格数据列表
            period: 周期（默认14）
        
        Returns:
            RSI值 (0-100)
        """
        if len(data) < period + 1:
            return None
        
        # 计算价格变化
        gains = []
        losses = []
        
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return None
        
        # 计算平均涨跌
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """
        计算 MACD 指标
        
        Args:
            data: 价格数据列表
            fast: 快线周期（默认12）
            slow: 慢线周期（默认26）
            signal: 信号线周期（默认9）
        
        Returns:
            (MACD值, 信号线, 柱状图)
        """
        if len(data) < slow + signal:
            return None, None, None
        
        # 计算 EMA
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None, None
        
        macd_line = ema_fast - ema_slow
        
        # 信号线（MACD的EMA）
        # 简化处理：使用当前MACD值
        signal_line = macd_line * 0.8  # 近似值
        
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """
        计算布林带
        
        Args:
            data: 价格数据列表
            period: 周期（默认20）
            std_dev: 标准差倍数（默认2）
        
        Returns:
            (上轨, 中轨, 下轨)
        """
        if len(data) < period:
            return None, None, None
        
        # 中轨 = SMA
        middle = sum(data[-period:]) / period
        
        # 标准差
        variance = sum((x - middle) ** 2 for x in data[-period:]) / period
        std = variance ** 0.5
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return upper, middle, lower
    
    def calculate_ma_cross(self, data, fast=5, slow=20):
        """
        计算均线交叉
        
        Args:
            data: 价格数据列表
            fast: 快线周期
            slow: 慢线周期
        
        Returns:
            (快线值, 慢线值, 交叉状态)
        """
        ma_fast = self.calculate_sma(data, fast)
        ma_slow = self.calculate_sma(data, slow)
        
        if ma_fast is None or ma_slow is None:
            return None, None, None
        
        # 判断交叉状态
        if ma_fast > ma_slow:
            status = "金叉 (看涨)"
        elif ma_fast < ma_slow:
            status = "死叉 (看跌)"
        else:
            status = "持平"
        
        return ma_fast, ma_slow, status
    
    def get_kline_prices(self, symbol, interval="1d", limit=100):
        """
        获取K线收盘价
        
        Args:
            symbol: 币种
            interval: 时间间隔
            limit: 数量
        
        Returns:
            收盘价列表
        """
        klines = self.binance.get_klines(symbol, interval, limit)
        if not klines:
            return []
        
        return [float(k[4]) for k in klines]  # 收盘价
    
    def analyze_all(self, symbol, interval="1d"):
        """
        综合技术分析
        
        Args:
            symbol: 币种
            interval: 时间间隔
        
        Returns:
            分析结果字典
        """
        prices = self.get_kline_prices(symbol, interval, 100)
        
        if not prices:
            return None
        
        current_price = prices[-1]
        
        # 计算各指标
        rsi = self.calculate_rsi(prices)
        macd, signal, hist = self.calculate_macd(prices)
        upper, middle, lower = self.calculate_bollinger_bands(prices)
        ma5, ma20, cross_status = self.calculate_ma_cross(prices)
        
        # RSI 判断
        rsi_status = "中性"
        if rsi:
            if rsi >= 70:
                rsi_status = "超买 (卖出信号)"
            elif rsi <= 30:
                rsi_status = "超卖 (买入信号)"
            elif rsi >= 50:
                rsi_status = "偏强"
            else:
                rsi_status = "偏弱"
        
        # MACD 判断
        macd_status = "中性"
        if macd is not None:
            if macd > 0:
                macd_status = "多头市场"
                if hist > 0:
                    macd_status += " (动能增强)"
            else:
                macd_status = "空头市场"
                if hist < 0:
                    macd_status += " (动能减弱)"
        
        # 布林带判断
        bb_status = "中性"
        bb_position = ""
        if upper and middle and lower:
            if current_price >= upper:
                bb_status = "超买"
                bb_position = "上轨上方"
            elif current_price <= lower:
                bb_status = "超卖"
                bb_position = "下轨下方"
            elif current_price >= middle:
                bb_position = "中轨上方"
            else:
                bb_position = "中轨下方"
        
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "current_price": current_price,
            "rsi": {
                "value": rsi,
                "status": rsi_status
            },
            "macd": {
                "value": macd,
                "signal": signal,
                "histogram": hist,
                "status": macd_status
            },
            "bollinger": {
                "upper": upper,
                "middle": middle,
                "lower": lower,
                "status": bb_status,
                "position": bb_position
            },
            "ma_cross": {
                "ma5": ma5,
                "ma20": ma20,
                "status": cross_status
            }
        }


class IndicatorsDisplay:
    """技术指标显示器"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def format_price(self, price):
        """格式化价格"""
        if price is None:
            return "N/A"
        if price >= 1000:
            return f"${price:,.2f}"
        elif price >= 1:
            return f"${price:.4f}"
        else:
            return f"${price:.8f}"
    
    def show_rsi(self, symbol="BTC", interval="1d"):
        """显示 RSI 指标"""
        print(f"\n=== {symbol.upper()} RSI 指标 ({interval}) ===\n")
        
        prices = self.indicators.get_kline_prices(symbol, interval, 50)
        if not prices:
            print("无法获取数据")
            return
        
        rsi = self.indicators.calculate_rsi(prices)
        
        if rsi is None:
            print("数据不足，无法计算 RSI")
            return
        
        # RSI 等级条 (Windows兼容)
        bar_length = int(rsi / 5)
        bar = "#" * bar_length + "-" * (20 - bar_length)
        
        print(f"RSI(14): {rsi:.2f}")
        print(f"[{bar}] {rsi:.0f}%")
        
        if rsi >= 70:
            print("状态: 超买区 (>70) - 注意回调风险")
        elif rsi <= 30:
            print("状态: 超卖区 (<30) - 可能存在反弹机会")
        elif rsi >= 50:
            print("状态: 强势区 (50-70)")
        else:
            print("状态: 弱势区 (30-50)")
        
        print()
    
    def show_macd(self, symbol="BTC", interval="1d"):
        """显示 MACD 指标"""
        print(f"\n=== {symbol.upper()} MACD 指标 ({interval}) ===\n")
        
        prices = self.indicators.get_kline_prices(symbol, interval, 100)
        if not prices:
            print("无法获取数据")
            return
        
        macd, signal, hist = self.indicators.calculate_macd(prices)
        
        if macd is None:
            print("数据不足，无法计算 MACD")
            return
        
        print(f"MACD线:  {macd:.4f}")
        print(f"信号线:  {signal:.4f}")
        print(f"柱状图:  {hist:+.4f}")
        print()
        
        if hist > 0:
            print("趋势: 多头 (MACD > 信号线)")
            if hist > abs(macd) * 0.1:
                print("动能: 增强")
            else:
                print("动能: 减弱")
        else:
            print("趋势: 空头 (MACD < 信号线)")
            if hist < -abs(macd) * 0.1:
                print("动能: 减弱")
            else:
                print("动能: 增强")
        
        print()
    
    def show_bollinger(self, symbol="BTC", interval="1d"):
        """显示布林带"""
        print(f"\n=== {symbol.upper()} 布林带 ({interval}) ===\n")
        
        prices = self.indicators.get_kline_prices(symbol, interval, 50)
        if not prices:
            print("无法获取数据")
            return
        
        upper, middle, lower = self.indicators.calculate_bollinger_bands(prices)
        current_price = prices[-1]
        
        if upper is None:
            print("数据不足，无法计算布林带")
            return
        
        print(f"上轨: {self.format_price(upper)}")
        print(f"中轨: {self.format_price(middle)}")
        print(f"下轨: {self.format_price(lower)}")
        print()
        print(f"当前价格: {self.format_price(current_price)}")
        
        # 计算带宽
        bandwidth = (upper - lower) / middle * 100
        print(f"带宽: {bandwidth:.2f}%")
        
        # 位置判断
        if current_price >= upper:
            print("位置: 上轨上方 - 超买警告")
        elif current_price <= lower:
            print("位置: 下轨下方 - 超卖信号")
        elif current_price >= middle:
            pct = (current_price - middle) / (upper - middle) * 100
            print(f"位置: 中轨上方 ({pct:.0f}%)")
        else:
            pct = (middle - current_price) / (middle - lower) * 100
            print(f"位置: 中轨下方 ({pct:.0f}%)")
        
        print()
    
    def show_all(self, symbol="BTC", interval="1d"):
        """显示所有技术指标"""
        print(f"\n{'=' * 50}")
        print(f" {symbol.upper()} 技术指标分析 ({interval})")
        print(f"{'=' * 50}\n")
        
        analysis = self.indicators.analyze_all(symbol, interval)
        
        if not analysis:
            print("无法获取分析数据")
            return
        
        current_price = analysis["current_price"]
        print(f"当前价格: {self.format_price(current_price)}\n")
        
        # RSI
        rsi = analysis["rsi"]
        print(f"[RSI(14)]")
        print(f"  数值: {rsi['value']:.2f}" if rsi['value'] else "  数值: N/A")
        print(f"  状态: {rsi['status']}")
        
        # MACD
        macd = analysis["macd"]
        print(f"\n[MACD(12,26,9)]")
        print(f"  MACD: {macd['value']:.4f}" if macd['value'] else "  MACD: N/A")
        print(f"  信号: {macd['status']}")
        
        # 布林带
        bb = analysis["bollinger"]
        print(f"\n[布林带(20,2)]")
        print(f"  上轨: {self.format_price(bb['upper'])}")
        print(f"  中轨: {self.format_price(bb['middle'])}")
        print(f"  下轨: {self.format_price(bb['lower'])}")
        print(f"  位置: {bb['position']}")
        
        # 均线交叉
        ma = analysis["ma_cross"]
        print(f"\n[均线交叉 MA5/MA20]")
        print(f"  MA5:  {self.format_price(ma['ma5'])}")
        print(f"  MA20: {self.format_price(ma['ma20'])}")
        print(f"  状态: {ma['status']}")
        
        # 综合判断
        print(f"\n{'=' * 50}")
        print(" 综合信号")
        print(f"{'=' * 50}\n")
        
        signals = []
        
        # RSI 信号
        if rsi['value']:
            if rsi['value'] <= 30:
                signals.append("买入")
            elif rsi['value'] >= 70:
                signals.append("卖出")
        
        # MACD 信号
        if macd['histogram']:
            if macd['histogram'] > 0:
                signals.append("看涨")
            else:
                signals.append("看跌")
        
        # 均线信号
        if "金叉" in ma['status']:
            signals.append("金叉")
        elif "死叉" in ma['status']:
            signals.append("死叉")
        
        print(f"信号汇总: {', '.join(signals) if signals else '中性'}")
        print("\n注意: 以上分析仅供参考，不构成投资建议\n")


# 单例实例
_indicators_display = None

def get_indicators_display():
    """获取技术指标显示器（单例）"""
    global _indicators_display
    if _indicators_display is None:
        _indicators_display = IndicatorsDisplay()
    return _indicators_display
