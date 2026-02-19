# BTC Analysis - 比特币行情分析技能

全面的加密货币行情分析工具，整合市场数据、链上基本面和宏观情绪数据。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行示例

```bash
# 查询 BTC 价格
python scripts/btc_cli.py price btc

# 查看 K 线
python scripts/btc_cli.py kline btc 1h

# 查看订单簿
python scripts/btc_cli.py depth btc --limit 20

# 恐惧与贪婪指数
python scripts/btc_cli.py feargreed

# 综合分析
python scripts/btc_cli.py analyze btc
```

## 功能列表

### 市场数据
- 实时价格查询
- K线分析（1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M）
- 订单簿深度
- 成交量统计

### 情绪分析
- 恐惧与贪婪指数
- 市场情绪评估

### 综合分析
- 多维度数据整合
- 投资参考建议

## 数据源

- 币安 API（Binance API）
- CoinGecko API
- Alternative.me（恐惧贪婪指数）

## 注意事项

1. 免费API有请求频率限制
2. 数据仅供参考，不构成投资建议
3. 不同数据源延迟可能不同

## 版本

v1.0.0 - 基础功能实现
