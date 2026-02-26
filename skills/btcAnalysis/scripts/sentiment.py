#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""情绪数据分析"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.sentiment import get_alternative_api


class SentimentAnalyzer:
    """情绪数据分析器"""
    
    def __init__(self):
        self.alt_api = get_alternative_api()
    
    def get_fear_greed_index(self):
        """
        获取恐惧与贪婪指数数据
        
        Returns:
            dict: {'value': int, 'classification': str}
        """
        data = self.alt_api.get_fear_greed_index(limit=1)
        if not data or 'data' not in data or not data['data']:
            return None
        
        current = data['data'][0]
        return {
            'value': int(current.get('value', 0)),
            'classification': current.get('value_classification', ''),
            'timestamp': current.get('timestamp', '')
        }
    
    def show_fear_greed_index(self):
        """显示恐惧与贪婪指数"""
        print("\n=== 恐惧与贪婪指数 ===\n")

        data = self.alt_api.get_fear_greed_index(limit=1)
        if not data or 'data' not in data:
            print("无法获取数据")
            return

        current = data['data'][0]
        value = int(current['value'])
        classification = current['value_classification']
        timestamp = current['timestamp']

        # 判断情绪级别
        if value <= 20:
            emoji = "[恐惧]"
            advice = "极度恐慌 - 买入机会"
        elif value <= 40:
            emoji = "[担忧]"
            advice = "恐慌 - 考虑买入"
        elif value <= 60:
            emoji = "[中性]"
            advice = "中性 - 观望为主"
        elif value <= 80:
            emoji = "[贪婪]"
            advice = "贪婪 - 注意风险"
        else:
            emoji = "[极度贪婪]"
            advice = "极度贪婪 - 考虑卖出"

        print(f"{emoji} 当前指数: {value}")
        print(f"   市场情绪: {classification}")
        print(f"   建议: {advice}")
        print(f"   更新时间: {timestamp[:10]} {timestamp[11:19]}\n")
