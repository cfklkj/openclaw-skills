# btcAnalysis - 比特币行情分析技能架构

## 技能概述

提供全面的比特币及加密货币行情分析能力，整合市场数据、链上基本面数据和宏观情绪数据三大核心板块，通过多维交叉验证给出投资决策参考。

## 核心功能模块

### 1. 市场数据分析 (Market Analysis)

#### 1.1 价格与成交数据
- **功能：** 获取实时和历史价格、成交量、K线数据（OHLC）
- **数据源：**
  - 币安 API (Binance API)
  - CoinGecko API (免费基础数据)
  - CoinMarketCap API
- **支持命令：**
  - `price <symbol>` - 查询实时价格
  - `kline <symbol> <interval>` - 获取K线数据（1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M）
  - `volume <symbol>` - 查询成交量统计
  - `ohlc <symbol> -d <days>` - 获取OHLC历史数据

#### 1.2 订单簿数据
- **功能：** 查看买卖盘深度和流动性
- **数据源：** 币安 API (Order Book)
- **支持命令：**
  - `depth <symbol> -l <limit>` - 查看订单簿深度（5/10/20档）
  - `liquidity <symbol>` - 分析流动性指标

#### 1.3 衍生品数据
- **功能：** 获取期货和期权数据
- **数据源：** 币安 Futures API
- **支持命令：**
  - `openinterest <symbol>` - 未平仓合约量
  - `funding <symbol>` - 资金费率
  - `longshort <symbol>` - 多空比

### 2. 链上基本面分析 (On-chain Analysis)

#### 2.1 规模与资金分析
- **功能：** TVL、稳定币市值分析
- **数据源：** DefiLlama API
- **支持命令：**
  - `tvl <protocol>` - 查询协议总锁仓量
  - `stablecoin` - 稳定币市值统计
  - `netflow <protocol>` - 净流量分析

#### 2.2 活动与效益分析
- **功能：** 交易量、费用收入分析
- **数据源：** DefiLlama API, Etherscan API
- **支持命令：**
  - `volume-chain <protocol>` - DEX 交易量
  - `fees <protocol>` - 费用与收入统计
  - `activity <protocol>` - 活跃度系数

#### 2.3 健康度评估
- **功能：** LP周转率、国库周转率
- **数据源：** DefiLlama API
- **支持命令：**
  - `lptr <dex>` - LP周转率分析
  - `treasury <dao>` - 国库健康度评估
  - `health <protocol>` - 综合健康度评分

### 3. 宏观与情绪分析 (Macro & Sentiment Analysis)

#### 3.1 市场情绪指标
- **功能：** 恐惧与贪婪指数、社交媒体热度、搜索趋势
- **数据源：** Alternative.me API, Google Trends
- **支持命令：**
  - `feargreed` - 恐惧与贪婪指数
  - `social <coin>` - 社交媒体热度
  - `trends <coin> -d <days>` - Google Trends 搜索趋势

#### 3.2 宏观环境监控
- **功能：** 监管动态、传统金融市场关联
- **数据源：** 新闻API、金融数据API
- **支持命令：**
  - `news <coin>` - 最新新闻
  - `macro` - 宏观指标（美股、美元指数、美联储利率）
  - `correlation <symbol>` - 与传统金融市场相关性分析

### 4. 综合分析 (Comprehensive Analysis)

#### 4.1 多维交叉验证
- **功能：** 整合多维度数据进行综合分析
- **支持命令：**
  - `analyze <symbol>` - 综合分析报告
  - `trend <symbol>` - 趋势判断（重趋势，轻短期峰值）
  - `verify <symbol>` - 多维交叉验证

#### 4.2 信号提醒
- **功能：** 重要信号和转折点提醒
- **支持命令：**
  - `signals <symbol>` - 查看当前信号
  - `alert <symbol> <condition>` - 设置提醒条件

## 技术架构

### 技能目录结构

```
btcAnalysis/
├── SKILL.md              # 技能文档
├── README.md             # 使用说明
├── CHANGELOG.md          # 更新日志
├── scripts/              # 脚本文件
│   ├── btc_cli.py        # 主CLI入口
│   ├── market.py         # 市场数据模块
│   ├── onchain.py        # 链上数据模块
│   ├── sentiment.py      # 情绪分析模块
│   ├── analysis.py       # 综合分析模块
│   └── config.py         # 配置管理
├── data/                 # 数据缓存目录
│   └── .gitignore
└── api/                  # API封装
    ├── binance.py        # 币安API
    ├── defillama.py      # DefiLlama API
    ├── coingecko.py      # CoinGecko API
    └── sentiment.py      # 情绪数据API
```

### 主要依赖

```python
# 数据请求
requests>=2.31.0

# 数据处理
pandas>=2.0.0
numpy>=1.24.0

# 图表可视化（可选）
matplotlib>=3.7.0
plotly>=5.14.0

# CLI框架
click>=8.1.0
```

### API 配置

```bash
# ~/.openclaw/skills/btcAnalysis/config.json
{
  "binance": {
    "base_url": "https://api.binance.com",
    "futures_url": "https://fapi.binance.com"
  },
  "defillama": {
    "base_url": "https://api.llama.fi"
  },
  "coingecko": {
    "base_url": "https://api.coingecko.com/api/v3"
  },
  "alternative": {
    "base_url": "https://api.alternative.me"
  },
  "cache": {
    "enabled": true,
    "ttl": 300  # 5分钟缓存
  }
}
```

## 命令设计

### 快速开始

```bash
# 查询比特币实时价格
btc price btc

# 查看K线数据
btc kline btc 1h

# 综合分析
btc analyze btc

# 查看恐惧与贪婪指数
btc feargreed

# 链上数据
btc tvl bitcoin

# 设置价格提醒
btc alert btc --price 70000
```

### 命令格式

```bash
# 市场数据
btc <command> <symbol> [options]
btc price <symbol> [--fiat usd]
btc kline <symbol> <interval> --days 7
btc depth <symbol> --limit 20
btc funding <symbol>

# 链上数据
btc tvl <protocol>
btc fees <protocol>
btc health <protocol>
btc volume-chain <protocol>

# 情绪分析
btc feargreed
btc social <symbol>
btc trends <symbol> --days 30

# 综合分析
btc analyze <symbol>
btc trend <symbol>
btc signals <symbol>

# 提醒
btc alert <symbol> --price <value>
btc alert <symbol> --condition "above/below"
```

## 输出格式

### 文本输出（默认）

```
=== BTC 价格信息 ===
当前价格: $67,845.32
24h涨跌: +2.34%
24h成交量: 23.5B USD
最高价: $69,200.00
最低价: $65,800.00

=== 技术指标 ===
RSI(14): 58.6 (中性)
MACD: 金叉 (看涨)
布林带: 中轨附近
```

### 表格输出

```
┌──────────────┬──────────┬──────────┬──────────┐
│   交易所     │   价格   │  涨跌幅   │  成交量  │
├──────────────┼──────────┼──────────┼──────────┤
│    币安      │ $67,845  │  +2.34%  │  12.3B   │
│   Coinbase   │ $67,823  │  +2.31%  │   8.5B   │
│   Kraken     │ $67,856  │  +2.35%  │   2.1B   │
└──────────────┴──────────┴──────────┴──────────┘
```

### JSON 输出（可选手动）

```bash
btc price btc --json
```

## 数据缓存策略

- **实时数据（价格、订单簿）**：缓存 5-30 秒
- **技术指标数据**：缓存 1-5 分钟
- **链上数据（TVL、费用）**：缓存 10-30 分钟
- **情绪数据**：缓存 1-6 小时

## 扩展性设计

### 支持添加新数据源

```python
# api/custom_provider.py
class CustomProvider:
    def get_price(self, symbol):
        pass

    def get_volume(self, symbol):
        pass
```

### 支持自定义分析策略

```python
# analysis/custom_strategy.py
class CustomStrategy:
    def analyze(self, data):
        pass
```

## 开发路线图

### Phase 1: 基础功能 (v1.0.0)
- ✅ 市场价格查询
- ✅ K线数据
- ✅ 基础订单簿
- ✅ 查询命令

### Phase 2: 链上数据 (v1.1.0)
- ✅ DefiLlama API 集成
- ✅ TVL 查询
- ✅ 费用收入分析
- ✅ 健康度评分

### Phase 3: 情绪分析 (v1.2.0)
- ✅ 恐惧贪婪指数
- ✅ 社交媒体热度
- ✅ 综合情绪评分

### Phase 4: 高级分析 (v2.0.0)
- 🔲 多维交叉验证
- 🔲 趋势判断算法
- 🔲 价格提醒系统
- 🔲 可视化图表

## 使用示例

### 基础查询
```bash
# 查询 BTC 价格
btc price btc

# 查询 1小时 K线（最近24小时）
btc kline btc 1h --days 1

# 查询恐惧与贪婪指数
btc feargreed
```

### 综合分析
```bash
# 完整分析报告
btc analyze btc

# 趋势判断
btc trend btc

# 多维验证
btc verify btc
```

### 链上分析
```bash
# Bitcoin TVL
btc tvl bitcoin

# Uniswap 费用收入
btc fees uniswap

# 健康度评分
btc health aave
```

### 监控提醒
```bash
# 设置价格提醒（BTC突破70000）
btc alert btc --price 70000 --action above

# 查看当前信号
btc signals btc

# 综合监控
btc monitor btc --interval 1h
```

## 注意事项

1. **API限制：** 免费API有请求频率限制，需要做好缓存和限流
2. **数据延迟：** 不同数据源延迟不同，标注数据时效性
3. **投资建议：** 仅供参考，不构成投资建议
4. **隐私保护：** 不存储用户交易数据和敏感信息

## 快速开始指南

1. **安装技能**
   ```bash
   cp -r btcAnalysis ~/.openclaw/skills/
   pip install -r requirements.txt
   ```

2. **配置API**（可选）
   ```bash
   # 编辑配置文件
   vim ~/.openclaw/skills/btcAnalysis/config.json
   ```

3. **测试运行**
   ```bash
   python scripts/btc_cli.py price btc
   ```

4. **开始使用**
   ```bash
   # 通过 OpenClaw 调用
   btc price btc
   btc analyze btc
   ```
