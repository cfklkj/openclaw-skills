---
name: btcAnalysis
description: 比特币与加密货币行情分析技能。整合市场数据、链上基本面和宏观情绪三大板块，提供价格查询、K线分析、链上数据、情绪指标等多维度分析功能。
version: 1.0.0
---

# BTC Analysis - 比特币行情分析技能

全面的加密货币行情分析工具，整合市场数据、链上基本面和宏观情绪数据，提供投资决策参考。

## 快速开始

```bash
# 查询实时价格
btc price btc

# 查看 K 线数据
btc kline btc 1h

# 综合分析
btc analyze btc

# 查看恐惧与贪婪指数
btc feargreed
```

## 核心功能

### 市场数据
- 实时价格查询
- K线分析（1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M）
- 订单簿深度
- 成交量统计

### 链上数据
- 总锁仓量（TVL）
- 稳定币市值
- 协议费用与收入
- 健康度评分

### 情绪分析
- 恐惧与贪婪指数
- 社交媒体热度
- 市场趋势判断

### 综合分析
- 多维交叉验证
- 技术指标分析
- 价格信号提醒

## 命令格式

```bash
# 市场数据
btc price <symbol> [--fiat <currency>]
btc kline <symbol> <interval> [--days <n>]
btc depth <symbol> --limit <n>
btc volume <symbol>

# 链上数据
btc tvl <protocol>
btc fees <protocol>
btc health <protocol>

# 情绪分析
btc feargreed
btc social <symbol>
btc trends <symbol>

# 综合分析
btc analyze <symbol>
btc trend <symbol>
btc signals <symbol>

# 提醒
btc alert <symbol> --price <value>
```

## 数据源

- 币安 API（市场数据、衍生品）
- DefiLlama API（链上数据）
- CoinGecko API（基础市场数据）
- Alternative.me API（情绪指数）

## 注意事项

- 免费API有请求限制，已做缓存处理
- 数据仅供参考，不构成投资建议
- 不同数据源延迟不同，标注数据时效性
