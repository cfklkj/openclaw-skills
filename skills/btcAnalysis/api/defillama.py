#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DefiLlama API 封装 - 链上数据

文档参考: https://defillama.com/docs/api
"""

import requests
import sys
import os
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import get_config


class DefiLlamaAPI:
    """DefiLlama API 客户端
    
    主要端点:
    - /protocols: 所有协议列表
    - /protocol/{name}: 单个协议详情
    - /v2/chains: 所有链TVL
    - /stablecoins: 稳定币数据
    """
    
    def __init__(self):
        config = get_config()
        self.base_url = config.get("defillama", {}).get(
            "base_url", "https://api.llama.fi"
        )
        self.yields_url = "https://yields.llama.fi"
        self.stablecoins_url = "https://stablecoins.llama.fi"
        self.fees_url = "https://fees.llama.fi"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
    
    def _get(self, url, params=None, timeout=15):
        """发送 GET 请求"""
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print("请求超时，请检查网络连接")
            return None
        except requests.exceptions.ConnectionError:
            print("网络连接失败")
            return None
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def get_all_protocols(self):
        """获取所有协议列表 (包含 TVL)
        
        Returns:
            list: 协议列表，每个协议包含 name, tvl, chains 等字段
        """
        url = f"{self.base_url}/protocols"
        return self._get(url, timeout=20)
    
    def get_protocol(self, name):
        """
        获取单个协议详情
        
        Args:
            name: 协议名称（如 uniswap, aave, lido）
        
        Returns:
            dict: 协议详情，包含 tvl, chainTvls, fees, revenue 等
        """
        url = f"{self.base_url}/protocol/{name.lower()}"
        return self._get(url)
    
    def get_chains(self):
        """获取所有链的 TVL
        
        Returns:
            list: 链列表，包含 name, tvl, tokenSymbol 等
        """
        url = f"{self.base_url}/v2/chains"
        return self._get(url)
    
    def get_chain(self, chain_name):
        """获取单链详情"""
        url = f"{self.base_url}/v2/chains"
        chains = self._get(url)
        if chains:
            for c in chains:
                if c.get('name', '').lower() == chain_name.lower():
                    return c
        return None
    
    def get_defi_tvl(self):
        """获取整个 DeFi 的总 TVL"""
        url = f"{self.base_url}/tvl"
        return self._get(url)
    
    def get_stablecoins(self):
        """获取稳定币数据
        
        Returns:
            dict: 包含 peggedAssets 列表
        """
        url = f"{self.stablecoins_url}/stablecoins"
        return self._get(url, timeout=20)
    
    def get_stablecoin_charts(self):
        """获取稳定币历史图表数据"""
        url = f"{self.stablecoins_url}/stablecoincharts/all"
        return self._get(url)
    
    def get_yields(self):
        """获取收益池数据
        
        Returns:
            dict: 包含 data 列表，每个池有 apy, tvlUsd 等
        """
        url = f"{self.yields_url}/pools"
        return self._get(url, timeout=20)
    
    def get_protocol_fees(self, name):
        """获取协议费用数据"""
        url = f"{self.fees_url}/summary/{name.lower()}"
        return self._get(url)
    
    def get_all_fees(self):
        """获取所有协议费用摘要"""
        url = f"{self.fees_url}/overview/fees"
        return self._get(url, timeout=20)
    
    def get_all_revenue(self):
        """获取所有协议收入摘要"""
        url = f"{self.fees_url}/overview/revenue"
        return self._get(url, timeout=20)


# 协议名称映射（支持常见别名）
PROTOCOL_ALIASES = {
    # 比特币/以太坊
    'btc': 'bitcoin',
    'bitcoin': 'bitcoin',
    'eth': 'ethereum',
    'ethereum': 'ethereum',
    
    # DEX
    'uni': 'uniswap',
    'uniswap': 'uniswap',
    'crv': 'curve-finance',
    'curve': 'curve-finance',
    'sushi': 'sushi-swap',
    'sushiswap': 'sushi-swap',
    'pancake': 'pancakeswap',
    'pancakeswap': 'pancakeswap',
    
    # 借贷
    'aave': 'aave',
    'comp': 'compound',
    'compound': 'compound',
    'maker': 'makerdao',
    'mkr': 'makerdao',
    
    # 流动性质押
    'lido': 'lido',
    'steth': 'lido',
    'rocket': 'rocket-pool',
    'reth': 'rocket-pool',
    
    # 公链
    'sol': 'solana',
    'solana': 'solana',
    'bnb': 'bsc',
    'bsc': 'bsc',
    'avax': 'avalanche',
    'avalanche': 'avalanche',
    'arb': 'arbitrum',
    'arbitrum': 'arbitrum',
    'op': 'optimism',
    'optimism': 'optimism',
    'matic': 'polygon',
    'polygon': 'polygon',
    'base': 'base',
    
    # 其他
    'gmxi': 'gmx',
    'gmx': 'gmx',
    'convex': 'convex-finance',
    'yearn': 'yearn-finance',
    'yfi': 'yearn-finance',
}


def get_defillama_api():
    """获取 DefiLlama API 客户端（单例）"""
    global _defillama_api
    if '_defillama_api' not in globals():
        _defillama_api = DefiLlamaAPI()
    return _defillama_api
