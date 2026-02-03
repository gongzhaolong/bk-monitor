# 刷新到 Redis 的原理详解

## 概述

`ClusterInfo.refresh_redis_storage_config()` 方法用于将 MySQL 数据库中的存储集群配置信息同步到 Redis 中，以便查询模块（unify-query）能够快速读取配置信息。

## 核心流程

### 1. 数据源：从 MySQL 读取

```python
# 从数据库查询所有存储集群配置信息
info_list = cls.objects.all()  # 获取所有 ClusterInfo 记录
```

**数据来源**：`metadata_clusterinfo` 表

**包含的字段**：
- `cluster_id`: 集群ID（主键）
- `cluster_name`: 集群名称
- `cluster_type`: 集群类型（influxdb、kafka、redis、elasticsearch 等）
- `domain_name`: 集群域名或IP地址
- `port`: 端口号
- `schema`: 访问协议（http、https）
- `username`: 用户名
- `password`: 密码（加密存储）

### 2. 数据转换：构建配置字典

```python
# 为每个集群构建配置字典
config_value = {
    "address": f"{schema}://{domain_name}:{port}",  # 例如: "http://127.0.0.1:4090"
    "username": storage_info.username,
    "password": storage_info.password,
    "type": storage_info.cluster_type,  # 例如: "influxdb"
}
```

**关键处理**：
- **地址构建**：根据 `schema` 字段生成完整的访问地址
  - 如果 `schema` 是 `http` 或 `https`，直接使用
  - 否则默认使用 `http`
  - 格式：`{schema}://{domain_name}:{port}`

**示例**：
```python
# 输入
schema = "http"
domain_name = "127.0.0.1"
port = 4090

# 输出
address = "http://127.0.0.1:4090"
```

### 3. 数据存储：写入 Redis

```python
# 构建 Redis key
redis_key = f"{cls.REDIS_PREFIX_KEY}:{cluster_id}"
# 例如: "bkmonitorv3:unify-query:data:storage:1"

# 将配置序列化为 JSON 字符串并写入 Redis
RedisTools().client.set(redis_key, json.dumps(config_value))
```

**Redis Key 格式**：
```
bkmonitorv3:unify-query:data:storage:{cluster_id}
```

**Redis Value 格式**（JSON 字符串）：
```json
{
    "address": "http://127.0.0.1:4090",
    "username": "admin",
    "password": "password123",
    "type": "influxdb"
}
```

## Redis 连接初始化

### RedisTools 类

```python
class RedisTools:
    metadata_redis_client = None  # 类变量，存储 Redis 客户端实例
    
    @property
    def client(self) -> RedisClient:
        client = self.metadata_redis_client
        if client is None:
            client = setup_client()  # 延迟初始化
        return client
```

### 客户端初始化

```python
def setup_client():
    """初始化 Redis 客户端"""
    RedisTools.metadata_redis_client = RedisClient.from_envs(
        prefix=os.environ.get("METADATA_REDIS_CONFIG_PREFIX", "BK_MONITOR_TRANSFER")
    )
```

**环境变量配置**：
- `BK_MONITOR_TRANSFER_REDIS_HOST`: Redis 主机地址
- `BK_MONITOR_TRANSFER_REDIS_PORT`: Redis 端口
- `BK_MONITOR_TRANSFER_REDIS_PASSWORD`: Redis 密码
- `BK_MONITOR_TRANSFER_REDIS_DB`: Redis 数据库编号
- `BK_MONITOR_TRANSFER_REDIS_MODE`: Redis 模式（standalone、sentinel、cluster）

**关键点**：
- 使用环境变量前缀 `BK_MONITOR_TRANSFER` 来配置 Redis 连接
- 支持多种 Redis 部署模式（单机、哨兵、集群）
- 客户端在模块导入时尝试初始化，失败时静默处理（避免启动报错）

## 完整流程图

```
┌─────────────────────────────────────────────────────────────┐
│  1. 从 MySQL 读取数据                                        │
│     metadata_clusterinfo 表                                  │
│     ↓                                                        │
│     ClusterInfo.objects.all()                                │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 数据转换                                                 │
│     ↓                                                        │
│     for storage_info in info_list:                            │
│         config_value = {                                     │
│             "address": f"{schema}://{domain}:{port}",       │
│             "username": storage_info.username,               │
│             "password": storage_info.password,               │
│             "type": storage_info.cluster_type                 │
│         }                                                    │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 序列化为 JSON                                            │
│     ↓                                                        │
│     json.dumps(config_value)                                │
│     ↓                                                        │
│     '{"address":"http://127.0.0.1:4090",...}'              │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 写入 Redis                                               │
│     ↓                                                        │
│     redis_key = "bkmonitorv3:unify-query:data:storage:1"     │
│     ↓                                                        │
│     RedisTools().client.set(redis_key, json_string)         │
│     ↓                                                        │
│     Redis 存储                                               │
│     Key:   bkmonitorv3:unify-query:data:storage:1           │
│     Value: {"address":"http://127.0.0.1:4090",...}          │
└─────────────────────────────────────────────────────────────┘
```

## 数据读取流程

### get_redis_storage_config() 方法

```python
@classmethod
def get_redis_storage_config(cls, cluster_id: int) -> dict | None:
    """从 Redis 读取存储集群配置"""
    # 1. 构建 Redis key
    redis_key = f"{cls.REDIS_PREFIX_KEY}:{cluster_id}"
    
    # 2. 从 Redis 读取数据
    data = RedisTools().client.get(redis_key)
    
    # 3. 解析 JSON 字符串
    if data:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return json.loads(data)
    
    return None
```

**读取流程**：
1. 根据 `cluster_id` 构建 Redis key
2. 从 Redis 读取数据（可能是 bytes 类型）
3. 解码为字符串（如果需要）
4. 解析 JSON 字符串为 Python 字典
5. 返回配置字典或 `None`（如果不存在）

## 与 Consul 的对比

### 相同点

1. **数据源相同**：都从 `metadata_clusterinfo` 表读取
2. **数据格式相同**：都包含 `address`、`username`、`password`、`type` 字段
3. **用途相同**：供查询模块（unify-query）读取配置

### 不同点

| 特性 | Redis | Consul |
|------|-------|--------|
| **存储位置** | Redis 数据库 | Consul KV 存储 |
| **Key 格式** | `bkmonitorv3:unify-query:data:storage:{cluster_id}` | `/bkmonitorv3/unify-query/data/storage/{cluster_id}` |
| **访问方式** | `RedisTools().client.get(key)` | `hash_consul.get(key=path)` |
| **性能** | 更快（内存存储） | 较慢（网络请求） |
| **适用场景** | 高频读取、低延迟要求 | 配置中心、服务发现 |

## 为什么需要刷新到 Redis？

### 1. **性能优化**
- Redis 是内存数据库，读取速度远快于 MySQL
- 减少数据库查询压力
- 降低网络延迟

### 2. **解耦设计**
- 查询模块（unify-query）不需要直接访问 MySQL
- 通过 Redis 作为中间层，实现数据缓存
- 便于横向扩展

### 3. **配置同步**
- 当 MySQL 中的配置更新时，需要刷新到 Redis
- 确保查询模块读取到最新配置
- 支持配置的热更新

## 使用场景

### 1. **配置更新后刷新**
```python
# 修改集群配置后
cluster = ClusterInfo.objects.get(cluster_id=1)
cluster.domain_name = "new.example.com"
cluster.save()

# 刷新到 Redis
ClusterInfo.refresh_redis_storage_config()
```

### 2. **批量刷新**
```python
# 刷新所有集群配置
ClusterInfo.refresh_redis_storage_config()
```

### 3. **查询模块读取**
```python
# 查询模块从 Redis 读取配置
config = ClusterInfo.get_redis_storage_config(cluster_id=1)
if config:
    address = config["address"]
    username = config["username"]
    password = config["password"]
    # 使用配置连接存储集群
```

## 注意事项

### 1. **环境变量配置**
刷新前必须确保以下环境变量已配置：
- `BK_MONITOR_TRANSFER_REDIS_HOST`
- `BK_MONITOR_TRANSFER_REDIS_PORT`
- `BK_MONITOR_TRANSFER_REDIS_PASSWORD`（如果有）
- `BK_MONITOR_TRANSFER_REDIS_DB`
- `BK_MONITOR_TRANSFER_REDIS_MODE`

### 2. **Redis 连接初始化时机**
- `RedisTools` 在模块导入时尝试初始化客户端
- 如果初始化失败，会在首次使用时重试
- 确保环境变量在 Django 启动前已设置

### 3. **数据一致性**
- MySQL 是数据源，Redis 是缓存
- 配置更新后需要主动刷新 Redis
- 如果 Redis 数据丢失，可以从 MySQL 重新刷新

### 4. **错误处理**
- `refresh_redis_storage_config()` 会记录日志，但不会抛出异常
- `get_redis_storage_config()` 如果读取失败，返回 `None`
- 调用方需要处理 `None` 的情况，可以回退到从 MySQL 读取

## 总结

刷新到 Redis 的核心原理是：
1. **读取**：从 MySQL 数据库读取集群配置
2. **转换**：将数据库记录转换为配置字典
3. **序列化**：将配置字典序列化为 JSON 字符串
4. **存储**：将 JSON 字符串写入 Redis，使用固定的 key 格式

这样设计的好处是：
- ✅ 提高读取性能（内存数据库）
- ✅ 减少数据库压力
- ✅ 实现配置缓存和热更新
- ✅ 支持查询模块快速获取配置

