#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""链上数据分析模块

基于 DefiLlama API 提供链上基本面分析功能
分析维度：
1. 存量指标: TVL、稳定币市值
2. 流量指标: 协议费用、收入
3. 健康度评分: 多维度综合评估
"""

import sys
import os
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.defillama import get_defillama_api, PROTOCOL_ALIASES


class OnchainAnalyzer:
    """链上数据分析器"""
    
    def __init__(self):
        self.api = get_defillama_api()
        self._protocols_cache = None
        self._chains_cache = None
    
    def resolve_protocol_name(self, name):
        """解析协议名称（支持别名）"""
        name_lower = name.lower().strip()
        return PROTOCOL_ALIASES.get(name_lower, name_lower)
    
    def format_tvl(self, tvl):
        """格式化 TVL"""
        if tvl is None:
            return "N/A"
        try:
            tvl = float(tvl)
        except (ValueError, TypeError):
            return "N/A"
        
        if tvl >= 1e9:
            return f"${tvl/1e9:.2f}B"
        elif tvl >= 1e6:
            return f"${tvl/1e6:.2f}M"
        elif tvl >= 1e3:
            return f"${tvl/1e3:.2f}K"
        return f"${tvl:.2f}"
    
    def format_percentage(self, pct):
        """格式化百分比"""
        if pct is None or isinstance(pct, (list, dict)):
            return "N/A"
        try:
            return f"{float(pct):+.2f}%"
        except (ValueError, TypeError):
            return "N/A"
    
    def _get_protocols_list(self):
        """获取协议列表（带缓存）"""
        if self._protocols_cache is None:
            self._protocols_cache = self.api.get_all_protocols()
        return self._protocols_cache
    
    def get_tvl(self, protocol):
        """
        获取协议 TVL
        
        Args:
            protocol: 协议名称
        
        Returns:
            TVL 数据字典
        """
        name = self.resolve_protocol_name(protocol)
        
        # 先从协议列表快速查找
        protocols = self._get_protocols_list()
        if protocols:
            for p in protocols:
                if p.get('name', '').lower() == name.lower() or \
                   p.get('slug', '').lower() == name.lower():
                    return self._parse_protocol_summary(p)
        
        # 找不到再请求详情
        data = self.api.get_protocol(name)
        if not data:
            return None
        
        return self._parse_protocol_detail(data)
    
    def _parse_protocol_summary(self, p):
        """解析协议摘要数据"""
        return {
            'name': p.get('name', ''),
            'symbol': p.get('symbol', ''),
            'tvl': self._safe_float(p.get('tvl')),
            'tvl_change_1d': self._safe_float(p.get('change_1d')),
            'tvl_change_7d': self._safe_float(p.get('change_7d')),
            'chains': p.get('chains', []),
            'category': p.get('category', ''),
            'slug': p.get('slug', ''),
            'logo': p.get('logo', ''),
        }
    
    def _parse_protocol_detail(self, data):
        """解析协议详情数据"""
        return {
            'name': data.get('name', ''),
            'symbol': data.get('symbol', ''),
            'tvl': self._safe_float(data.get('tvl')),
            'tvl_change_1d': self._safe_float(data.get('change_1d')),
            'tvl_change_7d': self._safe_float(data.get('change_7d')),
            'chains': data.get('chains', []),
            'category': data.get('category', ''),
            'slug': data.get('slug', ''),
            'logo': data.get('logo', ''),
            'description': data.get('description', ''),
            'forked_from': data.get('forkedFrom', []),
        }
    
    def _safe_float(self, val):
        """安全转换为浮点数"""
        if val is None or isinstance(val, (list, dict)):
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
    
    def get_fees(self, protocol):
        """
        获取协议费用数据
        
        Args:
            protocol: 协议名称
        
        Returns:
            费用数据字典
        """
        name = self.resolve_protocol_name(protocol)
        data = self.api.get_protocol_fees(name)
        
        if not data:
            return None
        
        return {
            'name': protocol.upper(),
            'total_fees_24h': self._safe_float(data.get('total24h')),
            'total_fees_7d': self._safe_float(data.get('total7d')),
            'total_fees_30d': self._safe_float(data.get('total30d')),
            'total_fees_all_time': self._safe_float(data.get('totalAllTime')),
        }
    
    def get_chain_tvl(self, chain):
        """
        获取公链 TVL
        
        Args:
            chain: 链名称
        
        Returns:
            链 TVL 数据
        """
        chains_data = self.api.get_chains()
        if not chains_data:
            return None
        
        chain_lower = chain.lower()
        for c in chains_data:
            if c.get('name', '').lower() == chain_lower:
                return {
                    'name': c.get('name'),
                    'tvl': self._safe_float(c.get('tvl')),
                    'tvl_change_1d': self._safe_float(c.get('change_1d')),
                    'tvl_change_7d': self._safe_float(c.get('change_7d')),
                    'tvl_change_1m': self._safe_float(c.get('change_1m')),
                    'token_symbol': c.get('tokenSymbol', ''),
                    'token_price': self._safe_float(c.get('tokenPrice')),
                }
        
        return None
    
    def get_top_protocols(self, limit=10):
        """
        获取 TVL 排名前 N 的协议
        
        Args:
            limit: 数量
        
        Returns:
            协议列表
        """
        protocols = self._get_protocols_list()
        if not protocols:
            return []
        
        # 过滤无效数据并按 TVL 排序
        valid_protocols = []
        for p in protocols:
            tvl = self._safe_float(p.get('tvl'))
            if tvl and tvl > 0:
                valid_protocols.append(p)
        
        sorted_protocols = sorted(
            valid_protocols,
            key=lambda x: self._safe_float(x.get('tvl')) or 0,
            reverse=True
        )
        
        return [self._parse_protocol_summary(p) for p in sorted_protocols[:limit]]
    
    def get_top_chains(self, limit=10):
        """
        获取 TVL 排名前 N 的公链
        
        Args:
            limit: 数量
        
        Returns:
            链列表
        """
        chains = self.api.get_chains()
        if not chains:
            return []
        
        # 过滤并排序
        valid_chains = []
        for c in chains:
            tvl = self._safe_float(c.get('tvl'))
            if tvl and tvl > 0:
                valid_chains.append({
                    'name': c.get('name'),
                    'tvl': tvl,
                    'tvl_change_1d': self._safe_float(c.get('change_1d')),
                    'tvl_change_7d': self._safe_float(c.get('change_7d')),
                    'token_symbol': c.get('tokenSymbol', ''),
                })
        
        sorted_chains = sorted(valid_chains, key=lambda x: x['tvl'], reverse=True)
        return sorted_chains[:limit]
    
    def get_stablecoins_data(self, limit=10):
        """获取稳定币市值数据"""
        data = self.api.get_stablecoins()
        if not data or 'peggedAssets' not in data:
            return None
        
        stablecoins = data['peggedAssets']
        
        # 按市值排序
        sorted_coins = []
        for c in stablecoins:
            # 市值在 circulating.peggedUSD 或 circulating.total
            circulating = c.get('circulating', {})
            market_cap = self._safe_float(circulating.get('peggedUSD')) or \
                         self._safe_float(circulating.get('total'))
            
            if market_cap and market_cap > 0:
                sorted_coins.append({
                    'name': c.get('name'),
                    'symbol': c.get('symbol'),
                    'market_cap': market_cap,
                    'peg_type': c.get('pegType', 'peggedUSD'),
                    'price': self._safe_float(c.get('price')),
                })
        
        sorted_coins.sort(key=lambda x: x['market_cap'], reverse=True)
        return sorted_coins[:limit]
    
    def calculate_health_score(self, protocol):
        """
        计算协议健康度评分
        
        评分维度（总分100）：
        - TVL 规模 (30分): 规模越大越安全
        - TVL 变化趋势 (20分): 持续增长为佳
        - 链分散度 (20分): 多链部署降低风险
        - 费用收入 (30分): 有可持续的收入模型
        
        Args:
            protocol: 协议名称
        
        Returns:
            (评分, 详情字典)
        """
        tvl_data = self.get_tvl(protocol)
        if not tvl_data:
            return None, None
        
        score = 0
        details = {}
        
        # 1. TVL 规模 (30分)
        tvl = tvl_data.get('tvl', 0) or 0
        if tvl >= 10e9:  # 100亿+
            tvl_score = 30
        elif tvl >= 5e9:  # 50亿+
            tvl_score = 25
        elif tvl >= 1e9:  # 10亿+
            tvl_score = 20
        elif tvl >= 100e6:  # 1亿+
            tvl_score = 15
        else:
            tvl_score = 10
        score += tvl_score
        details['tvl_score'] = tvl_score
        
        # 2. TVL 变化趋势 (20分)
        change_7d = tvl_data.get('tvl_change_7d')
        if change_7d is not None:
            if change_7d >= 10:
                trend_score = 20
            elif change_7d >= 5:
                trend_score = 15
            elif change_7d >= 0:
                trend_score = 10
            elif change_7d >= -5:
                trend_score = 5
            else:
                trend_score = 0
        else:
            trend_score = 10  # 无数据给中等分
        score += trend_score
        details['trend_score'] = trend_score
        
        # 3. 链分散度 (20分)
        chains = tvl_data.get('chains', [])
        chain_count = len(chains) if isinstance(chains, list) else 0
        if chain_count >= 5:
            chain_score = 20
        elif chain_count >= 3:
            chain_score = 15
        elif chain_count >= 2:
            chain_score = 10
        else:
            chain_score = 5
        score += chain_score
        details['chain_score'] = chain_score
        
        # 4. 费用收入 (30分)
        fees_data = self.get_fees(protocol)
        if fees_data:
            fees_24h = fees_data.get('total_fees_24h') or 0
            if fees_24h >= 1e6:  # 日费用 100万+
                fees_score = 30
            elif fees_24h >= 100e3:  # 10万+
                fees_score = 25
            elif fees_24h >= 10e3:  # 1万+
                fees_score = 20
            else:
                fees_score = 15
        else:
            fees_score = 10
        score += fees_score
        details['fees_score'] = fees_score
        
        return min(100, score), details


class OnchainDisplay:
    """链上数据显示器"""
    
    def __init__(self):
        self.analyzer = OnchainAnalyzer()
    
    def format_tvl(self, tvl):
        """格式化 TVL"""
        return self.analyzer.format_tvl(tvl)
    
    def format_percentage(self, pct):
        """格式化百分比"""
        return self.analyzer.format_percentage(pct)
    
    def show_tvl(self, protocol):
        """显示协议 TVL"""
        print(f"\n=== {protocol.upper()} TVL Data ===\n")
        
        data = self.analyzer.get_tvl(protocol)
        
        if not data:
            print(f"Cannot get data for {protocol}")
            print("Tip: Try full protocol name like: uniswap, aave, lido")
            return
        
        print(f"Protocol: {data['name']}")
        if data.get('symbol'):
            print(f"Symbol: {data['symbol']}")
        if data.get('category'):
            print(f"Category: {data['category']}")
        
        print(f"\nTVL: {self.format_tvl(data['tvl'])}")
        
        if data.get('tvl_change_1d') is not None:
            print(f"24h Change: {self.format_percentage(data['tvl_change_1d'])}")
        if data.get('tvl_change_7d') is not None:
            print(f"7d Change: {self.format_percentage(data['tvl_change_7d'])}")
        
        if data.get('chains'):
            chains_str = ', '.join(data['chains'][:5])
            if len(data['chains']) > 5:
                chains_str += f" ... (+{len(data['chains'])-5} more)"
            print(f"\nChains: {chains_str}")
        
        print()
    
    def show_fees(self, protocol):
        """显示协议费用"""
        print(f"\n=== {protocol.upper()} Fee Revenue ===\n")
        
        data = self.analyzer.get_fees(protocol)
        
        if not data:
            print(f"Cannot get fee data for {protocol}")
            return
        
        fees_24h = data.get('total_fees_24h') or 0
        fees_7d = data.get('total_fees_7d') or 0
        fees_30d = data.get('total_fees_30d') or 0
        fees_all = data.get('total_fees_all_time') or 0
        
        print(f"24h Fees: {self.format_tvl(fees_24h)}")
        print(f"7d Fees: {self.format_tvl(fees_7d)}")
        print(f"30d Fees: {self.format_tvl(fees_30d)}")
        print(f"All-time Fees: {self.format_tvl(fees_all)}")
        
        # 计算日均
        if fees_7d > 0:
            daily_avg = fees_7d / 7
            print(f"\nDaily Average (7d): {self.format_tvl(daily_avg)}")
        
        # 估算年化收入
        if fees_24h > 0:
            annualized = fees_24h * 365
            print(f"Annualized: {self.format_tvl(annualized)}")
        
        print()
    
    def show_health(self, protocol):
        """显示协议健康度"""
        print(f"\n=== {protocol.upper()} Health Score ===\n")
        
        score, details = self.analyzer.calculate_health_score(protocol)
        
        if score is None:
            print(f"Cannot get data for {protocol}")
            return
        
        # 评级
        if score >= 80:
            grade = "Excellent (A)"
            indicator = "[++]"
        elif score >= 60:
            grade = "Good (B)"
            indicator = "[+]"
        elif score >= 40:
            grade = "Fair (C)"
            indicator = "[-]"
        else:
            grade = "Risk (D)"
            indicator = "[!]"
        
        # 进度条
        bar_length = int(score / 5)
        bar = "#" * bar_length + "-" * (20 - bar_length)
        
        print(f"{indicator} Score: {score}/100")
        print(f"[{bar}] {score}%")
        print(f"Grade: {grade}")
        
        # 分项得分
        if details:
            print(f"\nScore Breakdown:")
            print(f"  TVL Size: {details.get('tvl_score', 0)}/30")
            print(f"  TVL Trend: {details.get('trend_score', 0)}/20")
            print(f"  Multi-chain: {details.get('chain_score', 0)}/20")
            print(f"  Fee Revenue: {details.get('fees_score', 0)}/30")
        
        # 获取 TVL 数据补充显示
        tvl_data = self.analyzer.get_tvl(protocol)
        if tvl_data:
            print(f"\nDetails:")
            print(f"  TVL: {self.format_tvl(tvl_data['tvl'])}")
            if tvl_data.get('tvl_change_7d') is not None:
                print(f"  7d Change: {self.format_percentage(tvl_data['tvl_change_7d'])}")
            print(f"  Chains: {len(tvl_data.get('chains', []))}")
        
        print()
    
    def show_top_protocols(self, limit=10):
        """显示 TVL 排行榜"""
        print(f"\n=== DeFi TVL Ranking (Top {limit}) ===\n")
        
        protocols = self.analyzer.get_top_protocols(limit)
        
        if not protocols:
            print("Cannot get data")
            return
        
        print(f"{'Rank':<4} {'Protocol':<20} {'TVL':<15} {'7d Change':<12} {'Chains':<6}")
        print("-" * 60)
        
        for i, p in enumerate(protocols, 1):
            name = p.get('name', 'N/A')[:18]
            tvl = self.format_tvl(p.get('tvl'))
            change = p.get('tvl_change_7d')
            change_str = self.format_percentage(change)
            chains = len(p.get('chains', []))
            
            print(f"{i:<4} {name:<20} {tvl:<15} {change_str:<12} {chains:<6}")
        
        print()
    
    def show_top_chains(self, limit=10):
        """显示公链 TVL 排行"""
        print(f"\n=== Chain TVL Ranking (Top {limit}) ===\n")
        
        chains = self.analyzer.get_top_chains(limit)
        
        if not chains:
            print("Cannot get data")
            return
        
        print(f"{'Rank':<4} {'Chain':<15} {'TVL':<15} {'7d Change':<12} {'Token':<8}")
        print("-" * 60)
        
        for i, c in enumerate(chains, 1):
            name = c.get('name', 'N/A')[:13]
            tvl = self.format_tvl(c.get('tvl'))
            change = c.get('tvl_change_7d')
            change_str = self.format_percentage(change)
            token = c.get('token_symbol', '-')[:6]
            
            print(f"{i:<4} {name:<15} {tvl:<15} {change_str:<12} {token:<8}")
        
        print()
    
    def show_chain_tvl(self, chain):
        """显示单链 TVL"""
        print(f"\n=== {chain.upper()} Chain TVL ===\n")
        
        data = self.analyzer.get_chain_tvl(chain)
        
        if not data:
            print(f"Cannot get data for {chain}")
            return
        
        print(f"Chain: {data['name']}")
        print(f"TVL: {self.format_tvl(data['tvl'])}")
        
        if data.get('tvl_change_1d') is not None:
            print(f"24h Change: {self.format_percentage(data['tvl_change_1d'])}")
        if data.get('tvl_change_7d') is not None:
            print(f"7d Change: {self.format_percentage(data['tvl_change_7d'])}")
        if data.get('tvl_change_1m') is not None:
            print(f"30d Change: {self.format_percentage(data['tvl_change_1m'])}")
        
        if data.get('token_symbol'):
            print(f"\nNative Token: {data['token_symbol']}")
            if data.get('token_price'):
                print(f"Token Price: ${data['token_price']:,.2f}")
        
        print()
    
    def show_stablecoins(self, limit=10):
        """显示稳定币市值排行"""
        print(f"\n=== Stablecoin Market Cap (Top {limit}) ===\n")
        
        coins = self.analyzer.get_stablecoins_data(limit)
        
        if not coins:
            print("Cannot get stablecoin data")
            return
        
        print(f"{'Rank':<4} {'Name':<15} {'Symbol':<10} {'Market Cap':<15} {'Type':<10}")
        print("-" * 60)
        
        for i, c in enumerate(coins[:limit], 1):
            name = c.get('name', 'N/A')[:13]
            symbol = c.get('symbol', 'N/A')[:8]
            cap_str = self.format_tvl(c.get('market_cap'))
            peg_type = c.get('peg_type', 'N/A')[:8]
            
            print(f"{i:<4} {name:<15} {symbol:<10} {cap_str:<15} {peg_type:<10}")
        
        print()


# 单例实例
_onchain_display = None

def get_onchain_display():
    """获取链上数据显示器（单例）"""
    global _onchain_display
    if _onchain_display is None:
        _onchain_display = OnchainDisplay()
    return _onchain_display
