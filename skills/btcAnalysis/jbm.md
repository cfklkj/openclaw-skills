好的，这是针对“链上数据-基本面分析”技能的开发文档方案。它延续了之前确定的指标体系和分析框架，为开发者提供从数据获取到应用落地的完整技术路径。

---

# 链上数据基本面分析 - 开发文档

**版本**: 1.0
**最后更新**: 2025年2月
**文档目标**: 为开发者提供构建链上基本面分析工具和应用的API参考、代码示例及架构指南。

## 1. 引言

### 1.1 概述
本开发文档旨在帮助开发者高效地集成和使用链上数据，构建强大的基本面分析工具。通过利用专业数据提供商和应用层的API，开发者可以绕过直接索引和解析原始区块链数据的复杂性，专注于核心业务逻辑：将数据转化为深刻的投资见解和用户价值 。

### 1.2 核心分析框架回顾
在开始开发前，请确保您的应用逻辑围绕以下基本面核心展开：
- **存量指标**: 总锁仓价值（TVL）、稳定币市值。
- **流量与收益指标**: 协议费用（Fees）、协议收入（Revenue）、交易量。
- **网络健康度**: 活跃地址数、开发者活动、巨鲸动向、MVRV比率。

## 2. 数据源API参考

本节提供主流链上数据平台的API接入文档和关键端点示例。

### 2.1 DefiLlama API
**适用场景**: 获取全面的DeFi协议数据，包括TVL、费用、收入、稳定币信息等。完全免费，是构建基本面仪表盘的首选 。

- **基础URL**: `https://api.llama.fi`
- **Python 客户端**: 可通过`apify-client`等第三方库进行封装调用 。

**关键端点示例**:

| **端点** | **描述** | **示例请求 (curl)** |
| :--- | :--- | :--- |
| `/overview/protocols` | 获取所有协议的最新TVL及排名 | `curl https://api.llama.fi/overview/protocols` |
| `/protocol/{protocolName}` | 获取特定协议的详细信息，包括TVL历史、费用、收入等 | `curl https://api.llama.fi/protocol/aave` |
| `/stablecoins` | 获取各链上稳定币的市值和分布数据 | `curl https://api.llama.fi/stablecoins` |

### 2.2 Token Terminal API
**适用场景**: 获取标准化、传统金融风格的财务指标（如P/E、P/S比率），用于跨协议和跨链的对比分析。需要API密钥 。

- **基础URL**: `https://api.tokenterminal.com/v2`
- **认证**: 在Header中添加`Authorization: Bearer <YOUR_API_KEY>` 。
- **速率限制**: 60次/分钟 。

**关键端点示例**:

| **端点** | **描述** | **示例请求 (curl)** |
| :--- | :--- | :--- |
| `/projects` | 获取所有支持项目的基本信息和最新指标 | `curl -H "Authorization: Bearer YOUR_API_KEY" https://api.tokenterminal.com/v2/projects` |
| `/metrics` | 获取可用的指标列表（如`fee`, `revenue`, `pe`等） | `curl -H "Authorization: Bearer YOUR_API_KEY" https://api.tokenterminal.com/v2/metrics` |
| `/projects/{project_id}/metrics` | 获取特定项目在指定时间范围内的指标数据 | `curl -H "Authorization: Bearer YOUR_API_KEY" "https://api.tokenterminal.com/v2/projects/aave/metrics?metric=revenue&from=2025-01-01&to=2025-02-01&interval=1d"` |

### 2.3 Glassnode API
**适用场景**: 获取底层区块链行为数据，如活跃地址、持币分布、MVRV比率、已实现盈亏等，用于研判市场周期和网络健康状况。需要API密钥 。

- **基础URL**: `https://api.glassnode.com/v1/metrics`
- **认证**: 所有请求需在Query参数中附带`api_key` 。

**关键端点示例** :

| **端点** | **描述** | **示例请求 (curl)** |
| :--- | :--- | :--- |
| `/addresses/active_count` | 获取指定资产的每日活跃地址数 | `curl "https://api.glassnode.com/v1/metrics/addresses/active_count?a=BTC&api_key=YOUR_API_KEY"` |
| `/addresses/accumulation_balance` | 获取积累地址的总余额 | `curl "https://api.glassnode.com/v1/metrics/addresses/accumulation_balance?a=ETH&api_key=YOUR_API_KEY"` |
| `/indicators/mvrv` | 获取MVRV比率 | `curl "https://api.glassnode.com/v1/metrics/indicators/mvrv?a=BTC&api_key=YOUR_API_KEY"` |

### 2.4 Nansen API
**适用场景**: 追踪“聪明钱”动向，获取标记地址（如巨鲸、VC）的实时链上行为，进行事件驱动分析和早期机会发现。需要API密钥 。

- **基础URL**: `https://api.nansen.ai/api/v1`
- **认证**: 在Header中添加`apiKey: <YOUR_API_KEY>` 。

**关键端点示例** :

| **端点** | **描述** | **示例请求 (curl)** |
| :--- | :--- | :--- |
| **POST** `/token-screener` | 基于多种指标（如聪明钱活动、流动性）筛选和发现代币 | `curl -X POST https://api.nansen.ai/api/v1/token-screener -H "apiKey: YOUR_API_KEY" -H "Content-Type: application/json" -d '{"chains": ["ethereum", "base"], "timeframe": "24h", "filters": {"only_smart_money": true}}'` |

### 2.5 Dune Analytics API
**适用场景**: 执行自定义的SQL查询，访问社区创建的丰富数据看板，获取解码后的事件和调用数据。Python SDK使集成变得简单 。

- **Python SDK**: `dune-client` 。
- **认证**: 使用API密钥初始化客户端 。

**Python 代码示例** :

```python
from dune_client.client import DuneClient
from dune_client.query import QueryBase

# 1. 初始化客户端
dune = DuneClient(api_key="YOUR_API_KEY")

# 2. 定义要执行的查询（通过查询ID）
query = QueryBase(query_id=1215383) # 示例查询ID

# 3. 执行查询并获取结果为DataFrame
results_df = dune.run_query_dataframe(query)
print(results_df.head())
```

## 3. 高级开发：自定义索引与计算

对于需要实时性、定制化逻辑或链上验证的场景，开发者可以构建自己的数据索引和处理管道。

### 3.1 使用The Graph进行自定义索引
The Graph允许开发者定义“子图”（subgraphs）来精确索引所需的区块链数据，非常适合为特定应用（如friend.tech）或协议构建高性能的数据API 。

**核心步骤** ：
1.  **定义 Schema (`schema.graphql`)**: 声明你想要存储和查询的数据实体（如`Trade`）。
    ```graphql
    type Trade @entity {
      id: ID!
      trader: Bytes!
      subject: Bytes!
      isBuy: Boolean!
      shareAmount: BigInt!
      ethAmount: BigInt!
      blockNumber: BigInt!
      blockTimestamp: BigInt!
    }
    ```
2.  **编写映射 (`mapping.ts`)**: 使用AssemblyScript编写事件处理函数，将链上事件数据转换并存储到schema定义的实体中。
    ```typescript
    // 处理 Trade 事件
    export function handleTrade(event: TradeEvent): void {
      let entity = new Trade(event.transaction.hash.toHex());
      entity.trader = event.params.trader;
      entity.subject = event.params.subject;
      entity.isBuy = event.params.isBuy;
      entity.shareAmount = event.params.shareAmount;
      entity.ethAmount = event.params.ethAmount;
      // ... 其他字段赋值
      entity.save();
    }
    ```
3.  **部署子图**: 将编译后的子图部署到Graph节点或托管服务。

### 3.2 高级链上计算与聚合
对于需要链上可验证的计算结果（如TWAP、波动率指数），可以利用支持WASM的索引器。开发者可以上传用Rust编写的自定义逻辑，在去中心化环境中对原始数据进行复杂计算，确保结果的可靠性和透明性 。

**Rust 代码示例: 计算已实现波动率** 

```rust
use primitive_types::U256;

fn calc_realized_volatility(prices: Vec<U256>) -> f64 {
    let mut squared_returns: Vec<f64> = Vec::new();
    
    // 1. 计算对数收益率
    for i in 0..prices.len() - 1 {
        let pt = prices[i+1].as_u128() as f64;
        let pt_minus_1 = prices[i].as_u128() as f64;
        let r = (pt / pt_minus_1).ln() * 100.0; // 百分比收益率
        squared_returns.push(r * r);
    }
    
    // 2. 计算平方收益率的均值并开方（标准差）
    let avg_squared = squared_returns.iter().sum::<f64>() / (squared_returns.len() as f64);
    (avg_squared).sqrt() * (squared_returns.len() as f64).sqrt()
}
```

### 3.3 贡献数据：DefiLlama Coins Adapter
如果你分析的协议价格数据未被现有数据源覆盖，可以为DefiLlama的Coins数据库贡献适配器（Adapter）。通过编写TypeScript代码，从链上流动性池或预言机中提取价格，使数据惠及整个社区 。

## 4. 应用架构示例

以下是一个典型链上基本面分析工具的后端微服务架构：

1.  **数据采集层**:
    - 调度器（Scheduler）定期调用2.1-2.5节中的各种API。
    - 使用消息队列（如RabbitMQ, Kafka）缓冲原始数据，确保可靠性。

2.  **数据处理与存储层**:
    - 消费者服务从队列中拉取数据。
    - **清洗与标准化**: 将不同来源的数据转换为统一的内部格式（例如，统一所有TVL的计价单位为USD）。
    - **指标计算**: 执行派生指标的计算，如计算**收入/费用比率**、**P/S比率**、**净资金流入**等 。
    - **存储**:
        - **时间序列数据库** (如 **InfluxDB**, **TimescaleDB**): 存储指标历史数据，用于趋势分析和图表展示。
        - **关系型数据库** (如 **PostgreSQL**): 存储协议元数据、配置信息等。

3.  **API与服务层**:
    - 使用 **RESTful API** 或 **GraphQL** 为前端提供聚合后的数据和查询服务。
    - 实现用户认证、API限流等功能。

4.  **应用层 (前端/客户端)**:
    - 基于Web的控制台（如使用React, Vue.js）。
    - 移动端应用。
    - 自动化交易脚本或监控报警机器人。

## 5. 快速开始指南

1.  **获取API密钥**: 根据你的需求，在Token Terminal、Glassnode或Nansen等平台上注册并获取API密钥。
2.  **选择一个切入点**:
    - **构建仪表盘**: 从调用**DefiLlama**的免费API开始，获取协议列表和TVL数据 。
    - **进行估值分析**: 集成**Token Terminal API**，获取协议的标准化财务指标 。
    - **监控聪明钱**: 探索**Nansen API**的`token-screener`端点，追踪市场热点 。
3.  **编写第一段代码**: 参考2.5节中的Python代码，尝试从Dune Analytics获取一个社区看板的数据。
4.  **扩展与深化**: 根据你的分析框架，逐步集成更多数据源，并开始构建2.2节中提到的“三维度验证法”等分析逻辑。

通过以上文档和工具链，开发者可以快速构建出专业、深入的链上数据基本面分析应用。