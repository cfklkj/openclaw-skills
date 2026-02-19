#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试脚本"""

import sys
import os
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.binance import get_binance_api

api = get_binance_api()
data = api.get_24h_ticker("BTC")
print("Ticker data:")
print(json.dumps(data, indent=2))
