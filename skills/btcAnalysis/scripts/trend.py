#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""趋势判断与综合分析模块

多维度交叉验证分析框架：
1. 技术面：RSI、MACD、布林带、均线交叉
2. 基本面：TVL、费用收入、健康度
3. 情绪面：恐惧贪婪指数

通过多维交叉验证提高判断准确率
"""

import sys
import os
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.indicators import TechnicalIndicators
from scripts.onchain import OnchainAnalyzer
from scripts.sentiment import SentimentAnalyzer
from api.binance import get_binance_api
from api.defillama import get_defillama_api


class TrendAnalyzer:
    """趋势分析器 - 多维交叉验证"""
    
    def __init__(self):
        self.tech = TechnicalIndicators()
        self.onchain = OnchainAnalyzer()
        self.sentiment = SentimentAnalyzer()
    
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
    
    def get_technical_signals(self, symbol, interval='1d'):
        """
        获取技术面信号
        
        Returns:
            dict: 技术指标信号
        """
        prices = self.tech.get_kline_prices(symbol, interval, 100)
        if not prices:
            return None
        
        current_price = prices[-1]
        
        # 计算各指标
        rsi = self.tech.calculate_rsi(prices)
        macd, signal, hist = self.tech.calculate_macd(prices)
        upper, middle, lower = self.tech.calculate_bollinger_bands(prices)
        ma5, ma20, cross_status = self.tech.calculate_ma_cross(prices)
        
        signals = []
        score = 0  # -100 到 +100
        
        # RSI 信号
        rsi_signal = "neutral"
        if rsi:
            if rsi <= 30:
                rsi_signal = "oversold"
                signals.append("RSI oversold (BUY)")
                score += 30
            elif rsi >= 70:
                rsi_signal = "overbought"
                signals.append("RSI overbought (SELL)")
                score -= 30
            elif rsi >= 50:
                rsi_signal = "bullish"
                score += 10
            else:
                rsi_signal = "bearish"
                score -= 10
        
        # MACD 信号
        macd_signal = "neutral"
        if macd is not None and hist is not None:
            if macd > 0 and hist > 0:
                macd_signal = "bullish"
                signals.append("MACD bullish")
                score += 20
            elif macd > 0 and hist < 0:
                macd_signal = "bullish_weakening"
                signals.append("MACD bullish weakening")
                score += 5
            elif macd < 0 and hist < 0:
                macd_signal = "bearish"
                signals.append("MACD bearish")
                score -= 20
            elif macd < 0 and hist > 0:
                macd_signal = "bearish_weakening"
                signals.append("MACD bearish weakening")
                score -= 5
        
        # 布林带信号
        bb_signal = "neutral"
        if upper and lower:
            if current_price <= lower:
                bb_signal = "oversold"
                signals.append("Below BB lower (BUY)")
                score += 25
            elif current_price >= upper:
                bb_signal = "overbought"
                signals.append("Above BB upper (SELL)")
                score -= 25
            elif current_price < middle:
                bb_signal = "bearish"
                score -= 5
        
        # 均线交叉信号
        ma_signal = "neutral"
        if "golden" in str(cross_status).lower():
            ma_signal = "golden_cross"
            signals.append("MA Golden Cross (BUY)")
            score += 25
        elif "death" in str(cross_status).lower():
            ma_signal = "death_cross"
            signals.append("MA Death Cross (SELL)")
            score -= 25
        
        return {
            'current_price': current_price,
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'macd': macd,
            'macd_signal': macd_signal,
            'bb_signal': bb_signal,
            'ma_signal': ma_signal,
            'signals': signals,
            'score': max(-100, min(100, score))
        }
    
    def get_onchain_signals(self, protocol):
        """
        获取链上面信号
        
        Args:
            protocol: 协议名称
        
        Returns:
            dict: 链上数据信号
        """
        tvl_data = self.onchain.get_tvl(protocol)
        if not tvl_data:
            return None
        
        signals = []
        score = 0
        
        tvl = tvl_data.get('tvl', 0) or 0
        tvl_change = tvl_data.get('tvl_change_7d')
        
        # TVL 变化信号
        if tvl_change is not None:
            if tvl_change >= 10:
                signals.append(f"TVL surge {tvl_change:.1f}%")
                score += 30
            elif tvl_change >= 5:
                signals.append(f"TVL up {tvl_change:.1f}%")
                score += 20
            elif tvl_change > 0:
                signals.append(f"TVL slight up {tvl_change:.1f}%")
                score += 10
            elif tvl_change >= -5:
                signals.append(f"TVL slight down {tvl_change:.1f}%")
                score -= 10
            elif tvl_change >= -10:
                signals.append(f"TVL down {tvl_change:.1f}%")
                score -= 20
            else:
                signals.append(f"TVL plunge {tvl_change:.1f}%")
                score -= 30
        
        # 链分散度
        chains = tvl_data.get('chains', [])
        if len(chains) >= 5:
            signals.append(f"Multi-chain ({len(chains)} chains)")
            score += 10
        
        # 健康度评分
        health_score, _ = self.onchain.calculate_health_score(protocol)
        
        return {
            'tvl': tvl,
            'tvl_change_7d': tvl_change,
            'chains': len(chains) if chains else 0,
            'health_score': health_score,
            'signals': signals,
            'score': max(-100, min(100, score))
        }
    
    def get_sentiment_signals(self):
        """
        获取情绪面信号
        
        Returns:
            dict: 情绪指标信号
        """
        fgi = self.sentiment.get_fear_greed_index()
        if not fgi:
            return None
        
        value = fgi.get('value')
        classification = fgi.get('classification', '')
        
        signals = []
        score = 0
        
        if value is not None:
            if value <= 25:
                signals.append("Extreme fear (BUY)")
                score += 40
            elif value <= 45:
                signals.append("Fear (lean BUY)")
                score += 20
            elif value <= 55:
                signals.append("Neutral")
                score += 0
            elif value <= 75:
                signals.append("Greed (lean SELL)")
                score -= 20
            else:
                signals.append("Extreme greed (SELL)")
                score -= 40
        
        return {
            'value': value,
            'classification': classification,
            'signals': signals,
            'score': max(-100, min(100, score))
        }
    
    def cross_validate(self, tech_score, onchain_score, sentiment_score):
        """
        多维交叉验证
        
        三维度一致性判断：
        - 全部同向：高置信度信号
        - 两个同向：中等置信度
        - 方向不一：低置信度，观望
        
        Returns:
            dict: 交叉验证结果
        """
        scores = [s for s in [tech_score, onchain_score, sentiment_score] if s is not None]
        
        if not scores:
            return {'confidence': 'none', 'direction': 'neutral', 'agreement': 0}
        
        # 计算方向
        positive = sum(1 for s in scores if s > 10)
        negative = sum(1 for s in scores if s < -10)
        neutral = len(scores) - positive - negative
        
        # 一致性判断
        if positive >= 2 and negative == 0:
            confidence = 'high'
            direction = 'bullish'
        elif negative >= 2 and positive == 0:
            confidence = 'high'
            direction = 'bearish'
        elif positive == 1 and negative == 0:
            confidence = 'medium'
            direction = 'slightly_bullish'
        elif negative == 1 and positive == 0:
            confidence = 'medium'
            direction = 'slightly_bearish'
        elif positive == negative:
            confidence = 'low'
            direction = 'neutral'
        else:
            confidence = 'medium'
            direction = 'mixed'
        
        # 综合得分
        total_score = sum(scores) / len(scores)
        
        return {
            'confidence': confidence,
            'direction': direction,
            'agreement': max(positive, negative, neutral) / len(scores) * 100,
            'total_score': total_score,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral
        }
    
    def generate_trading_signal(self, cross_result, tech_signals, onchain_signals, sentiment_signals):
        """
        生成交易信号
        
        Returns:
            dict: 交易建议
        """
        direction = cross_result['direction']
        confidence = cross_result['confidence']
        total_score = cross_result['total_score']
        
        action = "HOLD"
        reason = []
        
        if direction in ['bullish', 'slightly_bullish'] and confidence in ['high', 'medium']:
            if total_score >= 30:
                action = "STRONG_BUY"
                reason.append("Strong bullish signals across dimensions")
            elif total_score >= 15:
                action = "BUY"
                reason.append("Multi-dimension bullish")
            else:
                action = "ACCUMULATE"
                reason.append("Slightly bullish, accumulate on dips")
        
        elif direction in ['bearish', 'slightly_bearish'] and confidence in ['high', 'medium']:
            if total_score <= -30:
                action = "STRONG_SELL"
                reason.append("Strong bearish signals across dimensions")
            elif total_score <= -15:
                action = "SELL"
                reason.append("Multi-dimension bearish")
            else:
                action = "REDUCE"
                reason.append("Slightly bearish, reduce position")
        
        else:
            action = "HOLD"
            if confidence == 'low':
                reason.append("Mixed signals, wait and see")
            else:
                reason.append("Neutral market, maintain position")
        
        # 添加具体信号
        if tech_signals and tech_signals.get('signals'):
            reason.append(f"Technical: {', '.join(tech_signals['signals'][:2])}")
        if onchain_signals and onchain_signals.get('signals'):
            reason.append(f"On-chain: {', '.join(onchain_signals['signals'][:2])}")
        if sentiment_signals and sentiment_signals.get('signals'):
            reason.append(f"Sentiment: {', '.join(sentiment_signals['signals'])}")
        
        return {
            'action': action,
            'confidence': confidence,
            'reasons': reason,
            'score': total_score
        }
    
    def analyze(self, symbol, interval='1d'):
        """
        综合分析入口
        
        Args:
            symbol: 币种代码
            interval: 时间周期
        
        Returns:
            dict: 完整分析报告
        """
        # 获取三维度信号
        tech = self.get_technical_signals(symbol, interval)
        onchain = self.get_onchain_signals(symbol.lower())
        sentiment = self.get_sentiment_signals()
        
        # 交叉验证
        tech_score = tech.get('score') if tech else None
        onchain_score = onchain.get('score') if onchain else None
        sentiment_score = sentiment.get('score') if sentiment else None
        
        cross = self.cross_validate(tech_score, onchain_score, sentiment_score)
        
        # 生成交易信号
        trading = self.generate_trading_signal(cross, tech, onchain, sentiment)
        
        return {
            'symbol': symbol.upper(),
            'interval': interval,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'technical': tech,
            'onchain': onchain,
            'sentiment': sentiment,
            'cross_validation': cross,
            'trading_signal': trading
        }


class TrendDisplay:
    """趋势分析显示器"""
    
    def __init__(self):
        self.analyzer = TrendAnalyzer()
    
    def format_price(self, price):
        """格式化价格"""
        return self.analyzer.format_price(price)
    
    def show_trend(self, symbol, interval='1d'):
        """显示趋势分析"""
        result = self.analyzer.analyze(symbol, interval)
        
        print(f"\n{'=' * 60}")
        print(f" {result['symbol']} Trend Analysis ({result['interval']})")
        print(f" Time: {result['timestamp']}")
        print(f"{'=' * 60}\n")
        
        # 当前价格
        tech = result.get('technical')
        if tech:
            print(f"Current Price: {self.format_price(tech.get('current_price'))}\n")
        
        # 三维度信号
        self._show_dimension("Technical", result.get('technical'))
        self._show_dimension("On-chain", result.get('onchain'))
        self._show_dimension("Sentiment", result.get('sentiment'))
        
        # 交叉验证
        cross = result.get('cross_validation', {})
        print(f"\n{'=' * 60}")
        print(" Cross Validation")
        print(f"{'=' * 60}\n")
        
        direction_map = {
            'bullish': 'BULLISH [+]',
            'slightly_bullish': 'SLIGHTLY BULLISH [+]',
            'bearish': 'BEARISH [-]',
            'slightly_bearish': 'SLIGHTLY BEARISH [-]',
            'neutral': 'NEUTRAL [=]',
            'mixed': 'MIXED [?]'
        }
        
        confidence_map = {
            'high': 'HIGH',
            'medium': 'MEDIUM',
            'low': 'LOW'
        }
        
        print(f"Direction: {direction_map.get(cross.get('direction'), 'N/A')}")
        print(f"Confidence: {confidence_map.get(cross.get('confidence'), 'N/A')}")
        print(f"Agreement: {cross.get('agreement', 0):.0f}%")
        print(f"Total Score: {cross.get('total_score', 0):+.0f}")
        
        # 交易信号
        trading = result.get('trading_signal', {})
        print(f"\n{'=' * 60}")
        print(" Trading Signal")
        print(f"{'=' * 60}\n")
        
        action_map = {
            'STRONG_BUY': '[++] STRONG BUY',
            'BUY': '[+] BUY',
            'ACCUMULATE': '[+] ACCUMULATE',
            'HOLD': '[=] HOLD',
            'REDUCE': '[-] REDUCE POSITION',
            'SELL': '[-] SELL',
            'STRONG_SELL': '[--] STRONG SELL'
        }
        
        print(f"Action: {action_map.get(trading.get('action'), trading.get('action'))}")
        print(f"Confidence: {confidence_map.get(trading.get('confidence'), 'N/A')}")
        print(f"\nReasons:")
        for r in trading.get('reasons', []):
            print(f"  - {r}")
        
        print(f"\n{'=' * 60}")
        print(" DISCLAIMER: This is not financial advice.")
        print("{'=' * 60}\n")
    
    def _show_dimension(self, name, data):
        """显示单维度数据"""
        print(f"[{name}]")
        
        if not data:
            print("  Data unavailable\n")
            return
        
        signals = data.get('signals', [])
        score = data.get('score', 0)
        
        if signals:
            for s in signals[:3]:
                print(f"  - {s}")
        
        score_indicator = "+" if score > 0 else "" if score < 0 else ""
        print(f"  Score: {score_indicator}{score}")
        print()
    
    def show_signals(self, symbol, interval='1d'):
        """仅显示信号摘要"""
        result = self.analyzer.analyze(symbol, interval)
        
        print(f"\n=== {symbol.upper()} Signal Summary ===\n")
        
        trading = result.get('trading_signal', {})
        action = trading.get('action', 'N/A')
        confidence = trading.get('confidence', 'N/A')
        
        action_display = {
            'STRONG_BUY': 'STRONG BUY',
            'BUY': 'BUY',
            'ACCUMULATE': 'ACCUMULATE',
            'HOLD': 'HOLD',
            'REDUCE': 'REDUCE',
            'SELL': 'SELL',
            'STRONG_SELL': 'STRONG SELL'
        }
        
        print(f"Signal: {action_display.get(action, action)}")
        print(f"Confidence: {confidence.upper()}")
        print(f"Score: {trading.get('score', 0):+.0f}")
        
        if trading.get('reasons'):
            print(f"\nKey factors:")
            for r in trading['reasons'][:3]:
                print(f"  - {r}")
        
        print()


# 单例
_trend_display = None

def get_trend_display():
    global _trend_display
    if _trend_display is None:
        _trend_display = TrendDisplay()
    return _trend_display
